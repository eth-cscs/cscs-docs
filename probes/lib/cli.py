#!/usr/bin/env python3
"""Describe a cluster, for the documentation and for agents. See probe.sh.

Runs on the login nodes, which provide Python 3.6: no f-strings.
"""
import argparse
import datetime
import glob
import hashlib
import os
import socket
import sys
import tempfile
from collections import OrderedDict

import views
from probes import PROBES, published
from system import ProbeError, System

LIB = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(LIB)
MAX_AGE_DAYS = 30


def emitters_sha():
    """Hash of the probe sources, so a change to them is visible in the
    artifacts and signals that they should be regenerated. Deterministic; no
    git required."""
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
    print("writing " + os.path.relpath(path, os.path.dirname(ROOT)))


def today():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")


def generate(system, output):
    """Write the artifacts that the documentation includes: for each published
    probe the model as JSON and its table as markdown."""
    cluster = system.cluster()
    output = output or os.path.join(ROOT, "generated", cluster)
    sha = emitters_sha()

    # Every probe runs before anything is written, so that a failing probe
    # leaves all the committed artifacts untouched.
    files = []
    for probe in published():
        try:
            model = probe.build(system, "intended", True)
        except ProbeError as error:
            raise ProbeError("%s: %s" % (probe.name, error))
        data = views.envelope(cluster, "intended", sha, {probe.name: model})
        files.append((probe.name + ".json", views.to_json(data)))
        files.append((probe.name + ".md", views.to_markdown(data)))

    # The visible provenance line. This is the only artifact that carries a
    # date, so that the content fragments produce empty diffs when nothing has
    # changed, while a reader of the rendered page can still see how old the
    # facts are.
    files.append(("stamp.md", "*Cluster configuration on this page was generated from the "
                              "configuration of the system on %s.*\n" % today()))
    files.append(("manifest.json", views.to_json(OrderedDict([
        ("cluster", cluster),
        ("generated", today()),
        ("host", socket.gethostname()),
        ("emitters_sha", sha),
        ("max_age_days", MAX_AGE_DAYS),
        ("artifacts", OrderedDict(
            (probe.name + ".md", OrderedDict([
                ("source", probe.sources["intended"].replace("`", "")),
                ("data", probe.name + ".json"),
            ])) for probe in published())),
    ]))))

    os.makedirs(output, exist_ok=True)
    for name, text in files:
        write(os.path.join(output, name), text)


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


def render(check):
    """Make the markdown tables again from the committed JSON, for every
    cluster. A change to the columns of a table then needs no access to a
    cluster. With check, nothing is written and a table that differs from its
    JSON is an error."""
    stale = []
    for probe in published():
        for path in sorted(glob.glob(os.path.join(ROOT, "generated", "*", probe.name + ".json"))):
            with open(path) as handle:
                markdown = views.to_markdown(views.from_json(handle.read()))
            target = path[:-len(".json")] + ".md"
            current = ""
            if os.path.exists(target):
                with open(target) as handle:
                    current = handle.read()
            if current == markdown:
                continue
            if check:
                stale.append(os.path.relpath(target, os.path.dirname(ROOT)))
            else:
                write(target, markdown)
    # A cluster that was last probed before the JSON was introduced has only
    # the tables: they cannot be rendered again until the probe is re-run there.
    for directory in sorted(glob.glob(os.path.join(ROOT, "generated", "*"))):
        if not os.path.exists(os.path.join(directory, published()[0].name + ".json")):
            print("%s: no JSON, run probes/probe.sh there" % os.path.basename(directory))
    if stale:
        raise ProbeError("not rendered from the committed JSON, run ./probes/probe.sh --render:\n  "
                         + "\n  ".join(stale))


def main():
    parser = argparse.ArgumentParser(
        prog="probe.sh",
        description="Describe a cluster. With no options, write the artifacts that the "
                    "documentation includes to probes/generated/<cluster>/.",
        epilog="probes: " + ", ".join(PROBES) + ". See --list for what each one reports.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--live", action="store_true",
                      help="print probes for the system as it is running now")
    mode.add_argument("--intended", action="store_true",
                      help="print probes for the configuration that was deployed (slurm.conf)")
    mode.add_argument("--list", action="store_true",
                      help="print the probes, and with --format json the meaning of their fields")
    mode.add_argument("--render", action="store_true",
                      help="make the markdown tables again from the committed JSON")
    parser.add_argument("--check", action="store_true",
                        help="with --render: write nothing, fail if a table is out of date")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown",
                        help="output of --live, --intended and --list (default: markdown)")
    parser.add_argument("--fixture", metavar="DIR",
                        help="read saved command output from DIR instead of the system (for tests)")
    parser.add_argument("--output", metavar="DIR",
                        help="write the artifacts to DIR instead of probes/generated/<cluster>/")
    parser.add_argument("probe", nargs="*", help="with --live or --intended: the probes to print "
                                                 "(default: those in the documentation)")
    args = parser.parse_args()

    unknown = [name for name in args.probe if name not in PROBES]
    if unknown:
        parser.error("unknown probe: %s (choose from %s)" % (", ".join(unknown), ", ".join(PROBES)))
    if args.probe and not (args.live or args.intended):
        parser.error("naming probes needs --live or --intended")
    if args.check and not args.render:
        parser.error("--check needs --render")

    try:
        if args.list:
            sys.stdout.write(views.to_json(views.catalogue()) if args.format == "json"
                             else views.catalogue_text())
        elif args.render:
            render(args.check)
        elif args.live or args.intended:
            show(System(args.fixture), "live" if args.live else "intended", args.probe, args.format)
        else:
            generate(System(args.fixture), args.output)
    except ProbeError as error:
        sys.stderr.write("probe.sh: %s\n" % error)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
