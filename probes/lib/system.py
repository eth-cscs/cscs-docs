"""Access to the system that is probed.

Every command that a collector runs, and every file and environment variable
that it reads, goes through a System. A System can be backed by a directory of
saved outputs (a fixture) instead of a cluster, which is how the tests run
without access to one.

Runs on the login nodes, which provide Python 3.6: no f-strings.
"""
import getpass
import grp
import json
import os
import re
import subprocess


class ProbeError(Exception):
    """A probe could not describe the system. The message is for the person or
    agent that ran it."""


class System(object):
    def __init__(self, fixture=None):
        self.fixture = fixture
        self._facts = None
        self._config = None
        if fixture:
            with open(os.path.join(fixture, "facts.json")) as handle:
                self._facts = json.load(handle)

    # -- commands and files ---------------------------------------------------

    def run(self, name, argv, required=True):
        """The output of a command. `name` identifies it in a fixture, where
        the output is read from <name>.txt. A command that is not required
        returns an empty string when it is missing or fails."""
        if self.fixture:
            path = os.path.join(self.fixture, name + ".txt")
            if os.path.exists(path):
                with open(path) as handle:
                    return handle.read()
            if required:
                raise ProbeError("fixture has no %s.txt" % name)
            return ""
        try:
            done = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
        except OSError as error:
            if required:
                raise ProbeError("cannot run %s: %s" % (argv[0], error))
            return ""
        if done.returncode != 0:
            if required:
                raise ProbeError("%s failed: %s" % (" ".join(argv), done.stderr.strip()))
            return ""
        return done.stdout

    def read(self, name, path):
        """The contents of a file, or an empty string if it cannot be read."""
        if self.fixture:
            path = os.path.join(self.fixture, name + ".txt")
        try:
            with open(path) as handle:
                return handle.read()
        except OSError:
            return ""

    def exists(self, path):
        return True if self.fixture else os.path.exists(path)

    # -- who and where --------------------------------------------------------

    def env(self, variable):
        if self.fixture:
            return self._facts.get("env", {}).get(variable, "")
        return os.environ.get(variable, "")

    def user(self):
        return self._facts["user"] if self.fixture else getpass.getuser()

    def group(self):
        """The primary group of the user."""
        return self._facts["groups"][0] if self.fixture else grp.getgrgid(os.getgid()).gr_name

    def groups(self):
        if self.fixture:
            return list(self._facts["groups"])
        return self.run("id-groups", ["id", "-Gn"]).split()

    def cluster(self):
        """The name of the cluster. Ranked by robustness across execution
        contexts: /etc/xthostname is a root-owned file and is present
        regardless of shell type, whereas $CLUSTER_NAME is set by
        /etc/profile.d/cscs.sh and is empty in a non-login shell (as used by
        `ssh host 'command'` and by FirecREST)."""
        if self.fixture:
            return self._facts["cluster"]
        name = re.sub(r"^alps-", "", self.read("xthostname", "/etc/xthostname").strip())
        if not name:
            name = os.environ.get("CLUSTER_NAME", "")
        if not name:
            match = re.search(r"(?m)^system_name *= *'(.*)'",
                              self.read("uenv", "/etc/uenv/config.toml"))
            name = match.group(1) if match else ""
        # An empty name would write the artifacts into probes/generated/ itself.
        if not re.match(r"^[a-z][a-z0-9-]*$", name):
            raise ProbeError("cannot determine the cluster (got '%s')" % name)
        return name

    # -- Slurm ----------------------------------------------------------------

    def slurm_config(self):
        """`scontrol show config` as a dictionary."""
        if self._config is None:
            self._config = {}
            for line in self.run("scontrol-config", ["scontrol", "show", "config"]).splitlines():
                key, separator, value = line.partition("=")
                if separator:
                    self._config[key.strip()] = value.strip()
        return self._config

    def slurm_conf(self):
        """The slurm.conf that the Slurm commands on this node use. There is no
        fallback to the running configuration: the documentation must not be
        generated from it by accident."""
        if self.fixture:
            path = os.path.join(self.fixture, "slurm.conf")
        else:
            path = self.slurm_config().get("SLURM_CONF", "")
        if not os.access(path, os.R_OK):
            raise ProbeError("cannot read slurm.conf (got '%s')" % path)
        return path
