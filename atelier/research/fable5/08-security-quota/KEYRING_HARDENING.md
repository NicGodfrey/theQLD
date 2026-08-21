# Keyring Hardening Notes

How Atelier stores BYOK provider keys at rest. Companion to `THREAT_MODEL.md` (T1)
and `POLICY.md`.

## Baseline

Use the Python [`keyring`](https://pypi.org/project/keyring/) library so each OS
provides the encryption and unlock story:

| OS | Backend | At-rest protection |
|---|---|---|
| macOS | `keyring.backends.macOS.Keyring` (Keychain) | Encrypted, unlocked with login session; per-item ACLs |
| Windows | `keyring.backends.Windows.WinVaultKeyring` (Credential Locker) | DPAPI, scoped to the Windows user |
| Linux | `keyring.backends.SecretService.Keyring` (GNOME Keyring / KWallet via Secret Service) | Encrypted collection, unlocked with login session |

Naming: `service = "atelier"`, `username = "<provider>:<key-fingerprint>"`, e.g.
`openai:a1b2c3d4`. One entry per provider key; the fingerprint (first 8 hex of
SHA-256 of the key) lets us reference and rotate keys without ever printing them.

## The failure modes to actually worry about

1. **Silent plaintext fallback.** `keyring`'s chainer will happily select a weak
   backend if the platform one is unavailable — historically `keyrings.alt`'s
   `PlaintextKeyring` (base64 in a file, i.e. plaintext). If any dependency pulls
   in `keyrings.alt`, a headless or misconfigured machine quietly downgrades to
   plaintext on disk. **Pin the backend explicitly and fail closed:**

   ```python
   import keyring
   from keyring.backends import fail

   ALLOWED = (
       "keyring.backends.macOS.Keyring",
       "keyring.backends.Windows.WinVaultKeyring",
       "keyring.backends.SecretService.Keyring",
       "keyring.backends.kwallet.DBusKeyring",
   )

   def assert_secure_backend() -> None:
       kr = keyring.get_keyring()
       name = f"{type(kr).__module__}.{type(kr).__qualname__}"
       if isinstance(kr, fail.Keyring) or name not in ALLOWED:
           raise RuntimeError(
           f"No secure OS keyring available (got {name}). "
           "Refusing to store API keys. See docs/keyring.md for setup."
           )
   ```

   Run this at startup *and* immediately before any `set_password`. Do not ship
   `keyrings.alt`. Never honor `PYTHON_KEYRING_BACKEND` from the environment for
   the store path (an attacker-influenced env var could redirect writes).

2. **Headless / SSH Linux sessions.** Secret Service needs a DBus session and an
   unlocked collection; over SSH there usually isn't one. Options, in order:
   fail with instructions (`gnome-keyring-daemon --unlock` or `dbus-run-session`);
   or offer the explicit opt-in encrypted-file fallback below. Never auto-fallback.

3. **The keychain protects against A4, not co-resident processes.** Once the login
   keychain is unlocked, any process running as the user can read entries (on
   Linux, any app can enumerate Secret Service items). This is the OS trust model;
   document it, don't pretend otherwise. On macOS we get a little more: items
   created by the app get an ACL prompting when a *different* binary reads them —
   keep the app signed with a stable identity so the ACL remains stable across
   updates.

4. **WSL and containers.** WSL has no Secret Service by default; containers have
   none. Detect (`/proc/version` contains `microsoft`, `/.dockerenv` exists) and
   surface the encrypted-file fallback rather than a confusing DBus error.

## Explicit opt-in fallback: passphrase-encrypted file

Only when no OS keyring exists and the user explicitly opts in
(`atelier keys --file-store` prints a warning and requires confirmation):

- Format: single file `~/.config/atelier/keys.enc`, `0600` perms, containing
  `scrypt(n=2**15, r=8, p=1)`-derived key from a user passphrase + random 16-byte
  salt, encrypting a JSON map with AES-256-GCM (or `cryptography.Fernet` if we
  accept its AES-128-CBC+HMAC — either is fine at this threat level; GCM preferred).
- Passphrase is prompted per session (`getpass`), never cached to disk. The
  decrypted map lives only in backend memory.
- The file's directory is marked with `CACHEDIR.TAG`-style exclusion hints where
  supported and documented as "exclude from cloud sync".

## Runtime handling (in-memory hygiene)

- Read the key from keyring **once** at backend start (or first use), keep it in a
  module-private variable inside the key-broker; pass it only into HTTP client
  auth headers. Never into: browser responses, the ledger, subprocess argv or env,
  exception messages, or `__repr__` (wrap in a `Secret` class whose `__repr__`
  returns the fingerprint).
- Python cannot reliably zero memory (string interning, GC copies) — don't build
  elaborate zeroization theater; instead minimize copies: no f-string interpolation
  of the key, no `.strip()`-chains creating intermediates beyond the necessary, no
  logging of request objects that embed headers (see `POLICY.md`).
- Disable core dumps: `resource.setrlimit(resource.RLIMIT_CORE, (0, 0))` on POSIX.
- On key rotation: write new entry, verify a live API call succeeds with it, then
  `delete_password` the old entry. On "sign out": delete entries and drop the
  in-memory Secret.

## Verification checklist (CI + release)

- [ ] `assert_secure_backend()` unit-tested against a mocked `fail.Keyring` and a
      mocked plaintext backend (must raise).
- [ ] `pipdeptree | grep keyrings.alt` is empty; CI fails if it appears.
- [ ] Integration test on each OS runner: set/get/delete round-trip under service
      name `atelier-test`, then confirm deletion.
- [ ] Grep test: built artifact and logs from a full E2E run contain no string
      matching key regexes (`sk-[A-Za-z0-9_-]{20,}`, `AIza[0-9A-Za-z_-]{35}`).
- [ ] macOS: binary signed; keychain item ACL verified to not contain wildcard
      trusted apps.
