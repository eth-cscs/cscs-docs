#!/usr/bin/env python3
"""Describe a cluster, for the documentation and for agents. See probe.sh.

Runs on the login nodes, which provide Python 3.6: no f-strings.
"""
import argparse
import datetime
import glob
import hashlib
import os
import sys
import tempfile
from collections import OrderedDict

import views
from probes import PROBES, published
from system import ProbeError, System

LIB = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(LIB)
REPO = os.path.dirname(ROOT)
# The committed artifacts of each cluster: generated/clusters/<cluster>/.
GENERATED = os.path.join(REPO, "generated", "clusters")
RESULTS = "results.json"
MAX_AGE_DAYS = 30


def emitters_sha():
    """Hash of the probe sources, recorded in results.json, so that it shows
    which version of the probes produced the results. Deterministic; no git
    required."""
    digest = hashlib.sha256()
    for path in [os.path.join(ROOT, "probe.sh")] + sorted(glob.glob(os.path.join(LIB, "*.py"))):
        with open(path, "rb") as handle:
            digest.update(handle.read())
    return digest.hexdigest()[:8]


def write(path, text):
    """Replace a file in one step, so that an interrupted run cannot leave a
    truncated artifact."""
    handle, temporary = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".probe.")
    with os.fdopen(handle, "w") as out:
        out.write(text)
    os.chmod(temporary, 0o644)
    os.replace(temporary, path)
    print("writing " + os.path.relpath(path, REPO))


def today():
    # utcnow() is deprecated from Python 3.12; this form also works on 3.6.
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def generate(system, output):
    """Write the artifacts that the documentation includes: the table of each
    published probe as markdown, and the models of all of them in one JSON
    file, results.json."""
    cluster = system.cluster()
    output = output or os.path.join(GENERATED, cluster)

    # Every probe runs before anything is written, so that a failing probe
    # leaves all the committed artifacts untouched.
    models = OrderedDict()
    for probe in published():
        try:
            models[probe.name] = probe.build(system, "intended", True)
        except ProbeError as error:
            raise ProbeError("%s: %s" % (probe.name, error))

    # results.json is the only artifact that carries a date, so that the
    # tables produce empty diffs when nothing has changed. check-freshness.sh
    # reads the date. The login node is not recorded: which one a person lands
    # on would change the file on every run.
    data = views.envelope(cluster, "intended", emitters_sha(), models, [
        ("generated", today()),
        ("max_age_days", MAX_AGE_DAYS),
    ])
    files = [(name + ".md", markdown) for name, markdown in tables(data)]
    files.append((RESULTS, views.to_json(data)))

    os.makedirs(output, exist_ok=True)
    for name, text in files:
        write(os.path.join(output, name), text)


def tables(data):
    """The markdown table of each probe in data, one fragment per probe so
    that a page can include each table where it is needed."""
    for name, model in data["probes"].items():
        single = OrderedDict(data)
        single["probes"] = OrderedDict([(name, model)])
        yield name, views.to_markdown(single)


def show(system, source, names, fmt):
    """Print probes for the person or agent on the system. Nothing is written,
    so this can be run from a read-only checkout."""
    selected = [PROBES[name] for name in names] if names else published()
    models = OrderedDict()
    for probe in selected:
        if source not in probe.sources:
            raise ProbeError("%s describes the %s of the system, which has no intended "
                             "configuration: use --live" % (probe.name, probe.scope))
        models[probe.name] = probe.build(system, source, False)
    data = views.envelope(system.cluster(), source, emitters_sha(), models)
    sys.stdout.write(views.to_json(data) if fmt == "json" else views.to_markdown(data))


def render(check, root=GENERATED):
    """Make the markdown tables again from the committed results.json, for
    every cluster. A change to the columns of a table then needs no access to a
    cluster. With check, nothing is written and a table that differs from the
    results is an error."""
    stale = []
    for directory in sorted(glob.glob(os.path.join(root, "*"))):
        path = os.path.join(directory, RESULTS)
        if not os.path.exists(path):
            print("%s: no %s, run probes/probe.sh --generate there" % (os.path.basename(directory), RESULTS))
            continue
        with open(path) as handle:
            data = views.from_json(handle.read())
        missing = [probe.name for probe in published() if probe.name not in data["probes"]]
        if missing:
            print("%s: no results for %s, run probes/probe.sh --generate there"
                  % (os.path.basename(directory), ", ".join(missing)))
        for name, markdown in tables(data):
            target = os.path.join(directory, name + ".md")
            current = ""
            if os.path.exists(target):
                with open(target) as handle:
                    current = handle.read()
            if current == markdown:
                continue
            if check:
                stale.append(os.path.relpath(target, REPO))
            else:
                write(target, markdown)
    if stale:
        raise ProbeError("not rendered from the committed results, run ./probes/probe.sh --render:\n  "
                         + "\n  ".join(stale))


def main():
    parser = argparse.ArgumentParser(
        prog="probe.sh",
        description="Describe a cluster. With no options, print the probes for the system as it "
                    "is running now, like --live. Nothing is written unless --generate or --render "
                    "is given.",
        epilog="probes: " + ", ".join(PROBES) + ". See --list for what each one reports.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--live", action="store_true",
                      help="print probes for the system as it is running now (the default)")
    mode.add_argument("--intended", action="store_true",
                      help="print probes for the configuration that was deployed (slurm.conf)")
    mode.add_argument("--list", action="store_true",
                      help="print the probes, and with --format json the meaning of their fields")
    mode.add_argument("--generate", action="store_true",
                      help="write the artifacts that the documentation includes to "
                           "generated/clusters/<cluster>/, for maintainers of the documentation")
    mode.add_argument("--render", action="store_true",
                      help="make the markdown tables again from the committed results.json")
    parser.add_argument("--check", action="store_true",
                        help="with --render: write nothing, fail if a table is out of date")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown",
                        help="output of --live, --intended and --list (default: markdown)")
    parser.add_argument("--fixture", metavar="DIR",
                        help="read saved command output from DIR instead of the system (for tests)")
    parser.add_argument("--output", metavar="DIR",
                        help="with --generate: write the artifacts to DIR instead of "
                             "generated/clusters/<cluster>/")
    parser.add_argument("probe", nargs="*", help="the probes to print (default: those in the "
                                                 "documentation)")
    args = parser.parse_args()

    unknown = [name for name in args.probe if name not in PROBES]
    if unknown:
        parser.error("unknown probe: %s (choose from %s)" % (", ".join(unknown), ", ".join(PROBES)))
    if args.probe and (args.list or args.generate or args.render):
        parser.error("probes can only be named when printing them, not with --list, --generate or --render")
    if args.check and not args.render:
        parser.error("--check needs --render")
    if args.output and not args.generate:
        parser.error("--output needs --generate")

    try:
        if args.list:
            sys.stdout.write(views.to_json(views.catalogue()) if args.format == "json"
                             else views.catalogue_text())
        elif args.render:
            render(args.check)
        elif args.generate:
            generate(System(args.fixture), args.output)
        else:
            show(System(args.fixture), "intended" if args.intended else "live", args.probe, args.format)
    except ProbeError as error:
        sys.stderr.write("probe.sh: %s\n" % error)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
