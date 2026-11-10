#!/usr/bin/env python3
"""Add the agent skills and the cluster results to a built site.

Run by ./build after zensical has built the site:

    python3 skills/build.py --site site

Each directory skills/<name>/ that contains a SKILL.md is one skill. Its
bundle.json names the files from elsewhere in the repository that the skill
needs, such as the probes, and a command that tests the assembled skill. Each
skill is published as one archive, listed in an index that follows the Agent
Skills Discovery draft (https://github.com/cloudflare/agent-skills-discovery-rfc):

    .well-known/agent-skills/index.json
    .well-known/agent-skills/<name>.tar.gz
    .well-known/agent-skills/<name>/SKILL.md     to read before installing

The committed results.json of each cluster are published for agents that cannot
run the probes on a cluster:

    generated/clusters/index.json
    generated/clusters/<cluster>/results.json

The archives are reproducible: the same files give the same bytes, so the digest
of a skill changes when the skill changes, and an installed copy can be
compared with the published one.
"""

import argparse
import glob
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
# The page that tells users and agents how to install the skills.
PAGE = os.path.join(REPO, "docs", "agents", "index.md")

INDEX = os.path.join(".well-known", "agent-skills")
SCHEMA = "https://schemas.agentskills.io/discovery/0.2.0/schema.json"
# 1-64 lowercase letters, digits and single hyphens, not at either end.
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
# Files of the working tree that are never published.
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".*", "bundle.json")


class BuildError(Exception):
    pass


def frontmatter(path):
    """The top-level `key: value` pairs of the YAML frontmatter of path."""
    with open(path) as f:
        lines = f.read().splitlines()
    if not lines or lines[0] != "---":
        raise BuildError("%s: no frontmatter" % path)
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise BuildError("%s: frontmatter is not closed with ---" % path)
    meta = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if match:
            key, value = match.group(1), match.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            elif ": " in value or " #" in value:
                # YAML reads these as a nested mapping and a comment: agents that
                # parse the frontmatter strictly would reject or truncate it.
                raise BuildError("%s: the %s contains ': ' or ' #', so it must be quoted"
                                 % (path, key))
            meta[key] = value
    return meta


def find(skills_dir):
    """The skill directories in skills_dir, by name."""
    return [name for name in sorted(os.listdir(skills_dir))
            if os.path.isfile(os.path.join(skills_dir, name, "SKILL.md"))]


def check(skill_dir):
    """The frontmatter of the skill in skill_dir, if it is valid."""
    name = os.path.basename(skill_dir)
    meta = frontmatter(os.path.join(skill_dir, "SKILL.md"))
    if not NAME.match(name) or len(name) > MAX_NAME:
        raise BuildError("%s: the name must be 1-%d lowercase letters, digits and single hyphens"
                         % (name, MAX_NAME))
    if meta.get("name") != name:
        raise BuildError("%s: the name in SKILL.md is %r, it must be the name of its directory"
                         % (name, meta.get("name")))
    description = meta.get("description", "")
    if not description:
        raise BuildError("%s: SKILL.md has no description" % name)
    if len(description) > MAX_DESCRIPTION:
        raise BuildError("%s: the description is %d characters, at most %d are allowed"
                         % (name, len(description), MAX_DESCRIPTION))
    return meta


def bundle(skill_dir):
    path = os.path.join(skill_dir, "bundle.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def assemble(skill_dir, dest, repo):
    """Copy the skill and the files that its bundle.json names to dest."""
    name = os.path.basename(skill_dir)
    shutil.copytree(skill_dir, dest, ignore=IGNORE)
    for target, source in sorted(bundle(skill_dir).get("files", {}).items()):
        if os.path.isabs(target) or ".." in target.split("/"):
            raise BuildError("%s: bundle.json: %s is not a path inside the skill" % (name, target))
        src = os.path.join(repo, source)
        dst = os.path.join(dest, target)
        if not os.path.exists(src):
            raise BuildError("%s: bundle.json: %s does not exist" % (name, source))
        if os.path.exists(dst):
            raise BuildError("%s: bundle.json: %s is already in the skill" % (name, target))
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=IGNORE)
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)


def smoke_test(skill_dir, dest, repo):
    """Run the test command of bundle.json in the assembled skill, from repo."""
    command = bundle(skill_dir).get("smoke_test")
    if not command:
        return
    command = [os.path.join(dest, command[0])] + command[1:]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        result = subprocess.run(command, cwd=repo, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, universal_newlines=True)
        output, failed = result.stdout, result.returncode != 0
    except OSError as error:
        output, failed = str(error), True
    if failed:
        raise BuildError("%s: the smoke test failed: %s\n%s"
                         % (os.path.basename(skill_dir), " ".join(command), output))


def pack(dest):
    """dest as a reproducible .tar.gz, with SKILL.md at the root of the archive."""
    def normalised(info):
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        info.mtime = 0
        executable = info.isdir() or info.mode & 0o100
        info.mode = 0o755 if executable else 0o644
        return info

    # In a fixed order, each directory before what it contains.
    paths = []
    for root, dirs, files in os.walk(dest):
        dirs.sort()
        paths += [os.path.join(root, name) for name in dirs + sorted(files)]

    data = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=data, mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.GNU_FORMAT) as tar:
            for path in paths:
                if os.path.islink(path):
                    raise BuildError("%s: symbolic links are not published" % path)
                info = normalised(tar.gettarinfo(path, os.path.relpath(path, dest)))
                if info.isdir():
                    tar.addfile(info)
                else:
                    with open(path, "rb") as f:
                        tar.addfile(info, f)
    return data.getvalue()


def digest(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def to_json(data):
    return (json.dumps(data, indent=2) + "\n").encode()


def build_skills(site, repo=REPO, skills_dir=HERE, page=PAGE):
    out = os.path.join(site, INDEX)
    if os.path.exists(out):
        shutil.rmtree(out)
    with open(page) as f:
        described = f.read()
    entries = []
    for name in find(skills_dir):
        skill_dir = os.path.join(skills_dir, name)
        meta = check(skill_dir)
        # The page lists the skills for people, so that they know what they install.
        if "`%s`" % name not in described:
            raise BuildError("%s: not described on %s" % (name, os.path.relpath(page, repo)))
        with tempfile.TemporaryDirectory() as tmp:
            dest = os.path.join(tmp, name)
            assemble(skill_dir, dest, repo)
            smoke_test(skill_dir, dest, repo)
            data = pack(dest)
        write(os.path.join(out, name + ".tar.gz"), data)
        os.makedirs(os.path.join(out, name))
        shutil.copyfile(os.path.join(skill_dir, "SKILL.md"), os.path.join(out, name, "SKILL.md"))
        entries.append([("name", name), ("type", "archive"), ("description", meta["description"]),
                        ("url", name + ".tar.gz"), ("digest", digest(data))])
        print("skill %s: %s" % (name, digest(data)))
    if not entries:
        raise BuildError("no skills found in %s" % skills_dir)
    index = {"$schema": SCHEMA, "skills": [dict(entry) for entry in entries]}
    write(os.path.join(out, "index.json"), to_json(index))


def build_results(site, repo=REPO):
    """Publish the committed results.json of each cluster, and a list of them."""
    out = os.path.join(site, "generated", "clusters")
    clusters = []
    for path in sorted(glob.glob(os.path.join(repo, "generated", "clusters", "*", "results.json"))):
        with open(path) as f:
            results = json.load(f)
        cluster = os.path.basename(os.path.dirname(path))
        if results.get("cluster") != cluster:
            raise BuildError("%s: results of cluster %r" % (os.path.relpath(path, repo),
                                                           results.get("cluster")))
        os.makedirs(os.path.join(out, cluster), exist_ok=True)
        shutil.copyfile(path, os.path.join(out, cluster, "results.json"))
        clusters.append({"name": cluster, "generated": results["generated"],
                         "results": cluster + "/results.json"})
    write(os.path.join(out, "index.json"), to_json({"clusters": clusters}))
    print("results of %d clusters" % len(clusters))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--site", required=True, metavar="DIR",
                        help="the site built by zensical, to which the skills are added")
    args = parser.parse_args()
    if not os.path.isdir(args.site):
        parser.error("%s is not a directory: build the site first" % args.site)
    try:
        build_skills(args.site)
        build_results(args.site)
    except BuildError as error:
        sys.stderr.write("skills/build.py: %s\n" % error)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
