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
        self.token.write_text(json.dumps({"scopes": list(scopes) if scopes is not None else admin.SCOPES}))
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

    def test_partial_scopes_pass_and_name_the_unavailable_command(self):
        self.add_valid_files([admin.GMAIL_SETTINGS_SCOPE])
        status, output = self.run_check()
        self.assertEqual(status, 0)
        self.assertIn("inspect-gmail-routing: ready", output)
        self.assertIn("list-users: not authorized", output)
        self.assertIn(admin.USER_SCOPE, output)

    def test_token_granting_no_supported_command_fails(self):
        self.add_valid_files([])
        status, output = self.run_check()
        self.assertNotEqual(status, 0)
        self.assertIn("grants no supported command", output)

    def test_all_scopes_report_every_command_ready(self):
        self.add_valid_files()
        status, output = self.run_check()
        self.assertEqual(status, 0)
        for command in admin.COMMAND_SCOPES:
            self.assertIn(f"{command}: ready", output)

    def test_secret_permissions_fail(self):
        self.add_valid_files()
        self.secrets.chmod(0o755)
        status, output = self.run_check()
        self.assertNotEqual(status, 0)
        self.assertIn(".secrets is accessible", output)


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.secrets = Path(self.temp_dir.name) / ".secrets"
        self.secrets.mkdir(mode=0o700)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_profile_keeps_original_token_path(self):
        self.assertEqual(
            admin.token_path(secrets_dir=self.secrets).name, "token.json"
        )

    def test_named_profile_uses_separate_token_file(self):
        self.assertEqual(
            admin.token_path("work", secrets_dir=self.secrets).name,
            "token-work.json",
        )

    def test_unsafe_profile_names_are_rejected(self):
        for name in ("../escape", "a/b", "", "with space", "-leading", "x" * 40):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    admin.validate_profile(name)

    def test_profile_tokens_are_not_mistaken_for_client_files(self):
        for name in ("token.json", "token-work.json", "token-home.json"):
            (self.secrets / name).write_text("{}")
        (self.secrets / "client_secret.json").write_text("{}")
        clients = [
            path
            for path in sorted(self.secrets.glob("*.json"))
            if not admin._is_token_file(path)
        ]
        self.assertEqual([path.name for path in clients], ["client_secret.json"])


class ScopeSelectionTests(unittest.TestCase):
    def test_each_command_declares_only_the_scopes_it_uses(self):
        self.assertEqual(admin.COMMAND_SCOPES["list-users"], [admin.USER_SCOPE])
        self.assertEqual(admin.COMMAND_SCOPES["list-groups"], [admin.GROUP_SCOPE])
        self.assertEqual(
            admin.COMMAND_SCOPES["inspect-gmail-routing"],
            [admin.GMAIL_SETTINGS_SCOPE],
        )

    def test_consent_preserves_previously_granted_scopes(self):
        requested = admin.requested_scopes(
            [admin.GMAIL_SETTINGS_SCOPE], {admin.USER_SCOPE, admin.GROUP_SCOPE}
        )
        self.assertEqual(
            requested,
            sorted({admin.GMAIL_SETTINGS_SCOPE, admin.USER_SCOPE, admin.GROUP_SCOPE}),
        )

    def test_consent_for_a_fresh_token_requests_one_scope(self):
        self.assertEqual(
            admin.requested_scopes([admin.GMAIL_SETTINGS_SCOPE], set()),
            [admin.GMAIL_SETTINGS_SCOPE],
        )


if __name__ == "__main__":
    unittest.main()
