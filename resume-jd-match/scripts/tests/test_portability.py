import contextlib
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]


class PortabilityTests(unittest.TestCase):
    def test_missing_database_is_not_created(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / 'missing.db'
            result = subprocess.run([sys.executable, str(SCRIPTS/'pick_jds.py'), '--db', str(db)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(db.exists())

    def test_database_is_read_without_modification(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / 'example.db'
            output = Path(directory) / 'output.json'
            with sqlite3.connect(db) as conn:
                conn.execute('CREATE TABLE jobs (company TEXT, title TEXT, location TEXT, requirement TEXT, url TEXT)')
            before = hashlib.sha256(db.read_bytes()).hexdigest()
            result = subprocess.run([sys.executable, str(SCRIPTS/'pick_jds.py'), '--db', str(db), '--output', str(output)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(before, hashlib.sha256(db.read_bytes()).hexdigest())
            self.assertEqual(output.read_text(), '[]')

    def test_key_and_response_fragments_are_not_logged(self):
        spec = importlib.util.spec_from_file_location('check_key', SCRIPTS/'check_key.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        secret = 'sk-' + 'synthetic-do-not-print-123456789'
        for failure in (False, True):
            def call(*args):
                if failure:
                    raise RuntimeError('401 ' + secret)
                return {'echo': secret}, {}
            fake = types.SimpleNamespace(BASE_URL='https://example.com/'+secret, MODEL=secret, chat_json=call)
            output = io.StringIO()
            with patch.dict(os.environ, {'DASHSCOPE_API_KEY': secret}), patch.dict(sys.modules, {'llm': fake}), contextlib.redirect_stdout(output):
                self.assertEqual(module.main(), 1 if failure else 0)
            self.assertNotIn(secret, output.getvalue())
            self.assertNotIn(secret[:6], output.getvalue())
            self.assertNotIn(secret[-4:], output.getvalue())


if __name__ == '__main__':
    unittest.main()
