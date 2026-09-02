import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import google_workspace_admin as admin


class SetupCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.secrets = self.root / ".secrets"
        self.secrets.mkdir(mode=0o700)
        self.token = self.secrets / "token.json"
        self.client = self.secrets / "client_secret.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_check(self):
        lines = []
        with patch.dict(os.environ, {}, clear=False):
            status = admin.check_setup(self.secrets, self.token, lines.append)
        return status, "\n".join(lines)

    def add_valid_files(self, scopes=None):
        self.client.write_text(json.dumps({"installed": {
            "client_id": "redacted-test-id",
            "client_secret": "redacted-test-secret",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }}))
        self.token.write_text(json.dumps({"scopes": scopes or admin.SCOPES}))
        self.client.chmod(0o600)
        self.token.chmod(0o600)

    def test_valid_setup_passes(self):
        self.add_valid_files()
        status, output = self.run_check()
        self.assertEqual(status, 0)
        self.assertIn("Ready", output)

    def test_missing_token_fails_without_secret_output(self):
        self.client.write_text(json.dumps({"installed": {
            "client_id": "secret-client-id", "client_secret": "secret-client-secret",
            "auth_uri": "auth", "token_uri": "token"
        }}))
        self.client.chmod(0o600)
        status, output = self.run_check()
        self.assertNotEqual(status, 0)
        self.assertIn("authorization is not complete", output)
        self.assertNotIn("secret-client-secret", output)

    def test_missing_scope_fails(self):
        self.add_valid_files(admin.SCOPES[:-1])
        status, output = self.run_check()
        self.assertNotEqual(status, 0)
        self.assertIn(admin.SCOPES[-1], output)

    def test_secret_permissions_fail(self):
        self.add_valid_files()
        self.secrets.chmod(0o755)
        status, output = self.run_check()
        self.assertNotEqual(status, 0)
        self.assertIn(".secrets is accessible", output)


if __name__ == "__main__":
    unittest.main()
