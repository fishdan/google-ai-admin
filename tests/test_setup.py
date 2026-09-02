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


class ProfileClientTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.secrets = Path(self.temp_dir.name) / ".secrets"
        self.secrets.mkdir(mode=0o700)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_client(self, name):
        path = self.secrets / name
        path.write_text(json.dumps({"installed": {
            "client_id": "redacted-test-id",
            "client_secret": "redacted-test-secret",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }}))
        path.chmod(0o600)
        return path

    def test_named_profile_uses_its_own_client(self):
        self.write_client("client_secret-tenantb.json")
        resolved = admin.client_secret_path("tenantb", self.secrets)
        self.assertEqual(resolved.name, "client_secret-tenantb.json")

    def test_missing_profile_client_names_the_expected_path(self):
        with self.assertRaises(FileNotFoundError) as caught:
            admin.client_secret_path("tenantb", self.secrets)
        self.assertIn("client_secret-tenantb.json", str(caught.exception))

    def test_profile_client_is_not_counted_as_a_default_client(self):
        default = self.write_client("client_secret_876740.apps.googleusercontent.com.json")
        self.write_client("client_secret-tenantb.json")
        self.assertEqual(admin.client_secret_path(secrets_dir=self.secrets), default)

    def test_two_default_clients_are_still_ambiguous(self):
        self.write_client("client_secret_one.json")
        self.write_client("client_secret_two.json")
        with self.assertRaises(RuntimeError):
            admin.client_secret_path(secrets_dir=self.secrets)

    def test_unsafe_profile_name_is_rejected_before_building_a_path(self):
        with self.assertRaises(ValueError):
            admin.client_secret_path("../escape", self.secrets)

    def test_readiness_validates_the_profile_client_and_token(self):
        self.write_client("client_secret-tenantb.json")
        token = self.secrets / "token-tenantb.json"
        token.write_text(json.dumps({"scopes": [admin.USER_SCOPE]}))
        token.chmod(0o600)
        lines = []
        status = admin.check_setup(
            self.secrets, token, lines.append, profile="tenantb"
        )
        output = "\n".join(lines)
        self.assertEqual(status, 0)
        self.assertIn("profile: tenantb", output)
        self.assertIn("Desktop OAuth client: present and private", output)
        self.assertIn("list-users: ready", output)
        # The client filename can embed the client ID, so it is never printed.
        self.assertNotIn("client_secret-tenantb.json", output)

    def test_readiness_reports_a_missing_profile_client(self):
        token = self.secrets / "token-tenantb.json"
        token.write_text(json.dumps({"scopes": [admin.USER_SCOPE]}))
        token.chmod(0o600)
        lines = []
        status = admin.check_setup(
            self.secrets, token, lines.append, profile="tenantb"
        )
        output = "\n".join(lines)
        self.assertNotEqual(status, 0)
        self.assertIn("client_secret-tenantb.json", output)
        self.assertNotIn("redacted-test-secret", output)


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


class OAuthFlowTests(unittest.TestCase):
    def test_default_timeout_is_longer_than_five_minutes(self):
        self.assertGreater(admin.oauth_timeout_seconds({}), 300)

    def test_timeout_is_overridable(self):
        self.assertEqual(
            admin.oauth_timeout_seconds({"GOOGLE_OAUTH_TIMEOUT": "1200"}), 1200
        )

    def test_blank_timeout_falls_back_to_the_default(self):
        self.assertEqual(
            admin.oauth_timeout_seconds({"GOOGLE_OAUTH_TIMEOUT": ""}),
            admin.DEFAULT_OAUTH_TIMEOUT_SECONDS,
        )

    def test_invalid_timeout_is_rejected_clearly(self):
        for value in ("soon", "0", "-30", "5.5"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    admin.oauth_timeout_seconds({"GOOGLE_OAUTH_TIMEOUT": value})

    def test_wsl_is_detected_from_the_kernel_release(self):
        self.assertTrue(admin._is_wsl("6.18.33.2-microsoft-standard-WSL2"))
        self.assertFalse(admin._is_wsl("6.8.0-generic"))

    def test_explicit_browser_setting_wins(self):
        chosen = admin.register_host_browser(
            {"BROWSER": "firefox"}, candidates=("/nonexistent",)
        )
        self.assertIsNone(chosen)

    def test_missing_windows_browser_falls_back_silently(self):
        self.assertIsNone(
            admin.register_host_browser({}, candidates=("/nonexistent/chrome.exe",))
        )

    def test_timeout_error_is_an_attribute_error_subclass(self):
        # main() catches RuntimeError, so the flow must convert it rather than
        # let an AttributeError subclass escape as a traceback.
        self.assertTrue(issubclass(admin.WSGITimeoutError, AttributeError))


if __name__ == "__main__":
    unittest.main()
