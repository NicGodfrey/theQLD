"""Tests for keyring.py: permissions, env override, atomic writes."""
import json
import os
import shutil
import stat
import tempfile
import unittest

import fakes  # noqa: F401  (path bootstrap)

from keyring import ENV_VARS, Keyring, KeyringError, mask


def file_mode(path):
    return stat.S_IMODE(os.stat(path).st_mode)


class KeyringTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.path = os.path.join(self.tmp, "vault", "keyring.json")

    def make(self, env=None):
        return Keyring(path=self.path, env=env if env is not None else {})

    # -- storage & permissions ------------------------------------------------

    def test_set_get_round_trip(self):
        kr = self.make()
        kr.set_key("openai", "sk-round-trip")
        self.assertEqual(kr.get_key("openai"), "sk-round-trip")
        creds = kr.get("openai")
        self.assertEqual(creds.source, "file")

    def test_file_is_0600_and_dir_is_0700(self):
        kr = self.make()
        kr.set_key("openai", "sk-perms")
        self.assertEqual(file_mode(self.path), 0o600)
        self.assertEqual(file_mode(os.path.dirname(self.path)), 0o700)

    def test_loose_permissions_are_tightened_on_read(self):
        kr = self.make()
        kr.set_key("openai", "sk-loose")
        os.chmod(self.path, 0o644)
        kr.get_key("openai")
        self.assertEqual(file_mode(self.path), 0o600)

    def test_symlinked_keyring_is_refused(self):
        real = os.path.join(self.tmp, "elsewhere.json")
        with open(real, "w") as fh:
            json.dump({"version": 1, "providers": {}}, fh)
        os.makedirs(os.path.dirname(self.path))
        os.symlink(real, self.path)
        with self.assertRaises(KeyringError):
            self.make().get_key("openai")

    def test_corrupt_file_raises_keyring_error(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as fh:
            fh.write("{not json")
        os.chmod(self.path, 0o600)
        with self.assertRaises(KeyringError):
            self.make().get_key("openai")

    def test_empty_key_is_refused(self):
        with self.assertRaises(ValueError):
            self.make().set_key("openai", "   ")

    def test_delete(self):
        kr = self.make()
        kr.set_key("openai", "sk-gone")
        self.assertTrue(kr.delete("openai"))
        self.assertIsNone(kr.get_key("openai"))
        self.assertFalse(kr.delete("openai"))

    def test_base_url_only_entry(self):
        kr = self.make()
        kr.set_key("ollama", None, base_url="http://127.0.0.1:11434/v1")
        creds = kr.get("ollama")
        self.assertIsNone(creds.api_key)
        self.assertEqual(creds.base_url, "http://127.0.0.1:11434/v1")

    def test_set_key_none_preserves_existing_key(self):
        kr = self.make()
        kr.set_key("openai_compatible", "sk-keep")
        kr.set_key("openai_compatible", None,
                   base_url="https://llm.example/v1")
        creds = kr.get("openai_compatible")
        self.assertEqual(creds.api_key, "sk-keep")
        self.assertEqual(creds.base_url, "https://llm.example/v1")

    # -- env override -----------------------------------------------------------

    def test_env_beats_file(self):
        kr = self.make(env={"OPENAI_API_KEY": "sk-from-env"})
        kr.set_key("openai", "sk-from-file")
        creds = kr.get("openai")
        self.assertEqual(creds.api_key, "sk-from-env")
        self.assertEqual(creds.source, "env:OPENAI_API_KEY")

    def test_atelier_scoped_env_beats_conventional_env(self):
        kr = self.make(env={"OPENAI_API_KEY": "sk-generic",
                            "ATELIER_OPENAI_API_KEY": "sk-scoped"})
        self.assertEqual(kr.get_key("openai"), "sk-scoped")

    def test_gemini_falls_back_to_google_api_key(self):
        kr = self.make(env={"GOOGLE_API_KEY": "AIza-google"})
        creds = kr.get("gemini")
        self.assertEqual(creds.api_key, "AIza-google")
        self.assertEqual(creds.source, "env:GOOGLE_API_KEY")

    def test_base_url_env_override(self):
        kr = self.make(env={"ATELIER_COMPAT_BASE_URL": "https://env.example/v1"})
        kr.set_key("openai_compatible", "sk-x",
                   base_url="https://file.example/v1")
        self.assertEqual(kr.get("openai_compatible").base_url,
                         "https://env.example/v1")

    def test_providers_lists_file_and_env_sources(self):
        kr = self.make(env={"GEMINI_API_KEY": "AIza-x"})
        kr.set_key("openai", "sk-x")
        self.assertEqual(kr.providers(), ["gemini", "openai"])

    # -- hygiene -----------------------------------------------------------------

    def test_mask_never_shows_middle(self):
        self.assertEqual(mask("sk-abcdefghijklmnop"), "sk-a\u2026mnop")
        self.assertEqual(mask("short"), "\u2026")
        self.assertEqual(mask(None), "(none)")

    def test_repr_masks_key(self):
        kr = self.make()
        kr.set_key("openai", "sk-secret-secret-secret")
        text = repr(kr.get("openai"))
        self.assertNotIn("sk-secret-secret-secret", text)

    def test_every_known_provider_has_env_slots(self):
        for provider in ("openai", "gemini", "anthropic", "ollama",
                         "openai_compatible"):
            self.assertIn(provider, ENV_VARS)


if __name__ == "__main__":
    unittest.main()
