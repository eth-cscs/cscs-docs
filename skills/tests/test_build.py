"""Tests of skills/build.py.

    python3 -m unittest discover -s skills/tests
"""

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import build  # noqa: E402

SKILL = """---
name: %s
description: %s
---

# A skill
"""


class Published(unittest.TestCase):
    """The skills of the repository, built into an empty site."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.site = os.path.join(cls.tmp, "site")
        os.makedirs(cls.site)
        build.build_skills(cls.site)
        build.build_results(cls.site)
        cls.out = os.path.join(cls.site, build.INDEX)
        with open(os.path.join(cls.out, "index.json")) as f:
            cls.index = json.load(f)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def archive(self, entry):
        with open(os.path.join(self.out, entry["url"]), "rb") as f:
            return f.read()

    def test_index_lists_every_skill_with_its_digest(self):
        self.assertEqual(self.index["$schema"], build.SCHEMA)
        self.assertEqual([entry["name"] for entry in self.index["skills"]], build.find(build.HERE))
        for entry in self.index["skills"]:
            self.assertEqual(entry["type"], "archive")
            self.assertEqual(entry["digest"],
                             "sha256:" + hashlib.sha256(self.archive(entry)).hexdigest())

    def test_archive_has_skill_at_its_root_and_no_build_files(self):
        for entry in self.index["skills"]:
            with tarfile.open(fileobj=io.BytesIO(self.archive(entry))) as tar:
                names = tar.getnames()
            self.assertIn("SKILL.md", names)
            self.assertNotIn("bundle.json", names)
            for name in names:
                self.assertFalse(name.startswith(("/", "..")), name)
                self.assertNotIn("__pycache__", name)

    def test_skill_can_be_read_before_it_is_installed(self):
        for entry in self.index["skills"]:
            with open(os.path.join(self.out, entry["name"], "SKILL.md")) as f:
                self.assertEqual(build.frontmatter(f.name)["description"], entry["description"])

    def test_building_again_gives_the_same_archives(self):
        site = os.path.join(self.tmp, "again")
        os.makedirs(site)
        build.build_skills(site)
        with open(os.path.join(site, build.INDEX, "index.json")) as f:
            self.assertEqual(json.load(f), self.index)

    def test_probes_run_from_the_installed_skill(self):
        archive = self.archive({"url": "cscs-cluster-probes.tar.gz"})
        installed = os.path.join(self.tmp, "installed")
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            # The "data" filter, which refuses unsafe archives, is in Python 3.12 and later.
            tar.extractall(installed, **({"filter": "data"} if hasattr(tarfile, "data_filter") else {}))
        result = subprocess.run([os.path.join(installed, "scripts", "probe.sh"), "--list"],
                                stdout=subprocess.PIPE, universal_newlines=True, check=True)
        self.assertIn("partitions", result.stdout)

    def test_results_of_every_cluster_are_published(self):
        with open(os.path.join(self.site, "generated", "clusters", "index.json")) as f:
            clusters = json.load(f)["clusters"]
        committed = sorted(os.listdir(os.path.join(build.REPO, "generated", "clusters")))
        self.assertEqual([cluster["name"] for cluster in clusters], committed)
        for cluster in clusters:
            path = os.path.join(self.site, "generated", "clusters", cluster["results"])
            with open(path) as f:
                self.assertEqual(json.load(f)["cluster"], cluster["name"])


class Invalid(unittest.TestCase):
    """Skills that the build refuses."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = self.tmp
        self.skills = os.path.join(self.tmp, "skills")
        self.page = os.path.join(self.tmp, "page.md")
        self.site = os.path.join(self.tmp, "site")
        os.makedirs(self.site)
        with open(self.page, "w") as f:
            f.write("| `good` | a skill |\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def skill(self, directory, name=None, description="Does a thing.", bundle=None):
        path = os.path.join(self.skills, directory)
        os.makedirs(path)
        with open(os.path.join(path, "SKILL.md"), "w") as f:
            f.write(SKILL % (name or directory, description))
        if bundle is not None:
            with open(os.path.join(path, "bundle.json"), "w") as f:
                json.dump(bundle, f)

    def build(self):
        build.build_skills(self.site, self.repo, self.skills, self.page)

    def assertRefused(self, message):
        with self.assertRaises(build.BuildError) as raised:
            self.build()
        self.assertIn(message, str(raised.exception))

    def test_a_valid_skill_is_built(self):
        self.skill("good")
        self.build()
        self.assertTrue(os.path.exists(os.path.join(self.site, build.INDEX, "good.tar.gz")))

    def test_name_must_be_the_directory(self):
        self.skill("good", name="other")
        self.assertRefused("must be the name of its directory")

    def test_name_must_be_lowercase(self):
        self.skill("Good")
        self.assertRefused("lowercase")

    def test_description_is_required_and_limited(self):
        self.skill("good", description="x" * (build.MAX_DESCRIPTION + 1))
        self.assertRefused("at most")

    def test_description_that_yaml_would_misread_must_be_quoted(self):
        self.skill("good", description="Use for CI: logs and pipelines.")
        self.assertRefused("must be quoted")

    def test_quoted_description_is_unquoted(self):
        self.skill("good", description='"Use for CI: logs and pipelines."')
        self.build()
        with open(os.path.join(self.site, build.INDEX, "index.json")) as f:
            self.assertEqual(json.load(f)["skills"][0]["description"], "Use for CI: logs and pipelines.")

    def test_skill_must_be_described_on_the_page(self):
        self.skill("good")
        self.skill("hidden")
        self.assertRefused("hidden: not described")

    def test_bundled_file_must_exist(self):
        self.skill("good", bundle={"files": {"scripts/tool.sh": "missing/tool.sh"}})
        self.assertRefused("missing/tool.sh does not exist")

    def test_bundled_file_must_stay_inside_the_skill(self):
        self.skill("good", bundle={"files": {"../tool.sh": "page.md"}})
        self.assertRefused("not a path inside the skill")

    def test_failing_smoke_test_stops_the_build(self):
        self.skill("good", bundle={"smoke_test": ["SKILL.md"]})
        self.assertRefused("smoke test failed")


if __name__ == "__main__":
    unittest.main()
