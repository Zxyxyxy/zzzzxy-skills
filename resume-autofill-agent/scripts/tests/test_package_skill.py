import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location("package_skill", Path(__file__).parents[1] / "package_skill.py")
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)

class PackageTests(unittest.TestCase):
    def test_private_files_and_symlinks_are_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "resume-autofill-agent"
            root.mkdir()
            (root / "SKILL.md").write_text("source")
            for relative in (".env", "candidate-profile.json", "assets/private.json", "node_modules/dependency.js"):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("private")
            (root / "LICENSE.md").symlink_to(root / ".env")
            output = root / "package.zip"
            self.assertEqual(pack.build_zip(root, output), 1)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(archive.namelist(), ["resume-autofill-agent/SKILL.md"])

    def test_symlinked_source_directory_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "resume-autofill-agent"
            root.mkdir()
            (root / "SKILL.md").write_text("source")
            target = Path(directory) / "private"
            target.mkdir()
            (target / "candidate-profile-template.json").write_text("private")
            (root / "assets").symlink_to(target, target_is_directory=True)
            output = Path(directory) / "package.zip"
            self.assertEqual(pack.build_zip(root, output), 1)

if __name__ == "__main__":
    unittest.main()
