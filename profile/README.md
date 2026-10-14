# Welcome to Smart Social Contracts 👋

Decentralized free software for social cooperation.

## Contact

**Email:** contact@smartsocialcontracts.org

**PGP Fingerprint:** `6B7B 038D EB77 849F 1F61  5E67 CA38 8313 14D6 AA09`

To send an encrypted message, import our public key and encrypt with GPG:

```bash
curl -sL https://raw.githubusercontent.com/smart-social-contracts/.github/main/pgp-key.asc | gpg --import
gpg --encrypt --sign --armor -r contact@smartsocialcontracts.org message.txt
```

## Security

This section applies to every Smart Social Contracts repository. A repository's
own `SECURITY.md` adds only what is specific to it (security model, scope).

### Reporting a vulnerability

**Do not open a public GitHub issue for a security vulnerability.** Report it
privately, in either of these ways:

- GitHub: the repository's **Security** tab → **Report a vulnerability**
  (private vulnerability reporting).
- Encrypted email to contact@smartsocialcontracts.org, with the PGP key above.

Please include the repository and version (release tag or commit), what an
attacker needs (anonymous caller, signed-in user, a given permission, a
canister controller), and steps to reproduce, on a local replica rather than a
live deployment. Only the latest release of each project gets security fixes.

### Verifying a release

Releases of Casals, gos-as-a-service, realms-gos, file-registry, basilisk and
ic-basilisk-toolkit ship a checksum file signed with the key above, on a
hardware token. CI builds
each release as a draft; it is published only once the checksum file is signed,
and a published release whose signature does not verify goes back to draft.
Replace `<REPO>` and `<TAG>`:

```bash
curl -sL https://raw.githubusercontent.com/smart-social-contracts/.github/main/pgp-key.asc | gpg --import
cd "$(mktemp -d)"
gh release download <TAG> -R smart-social-contracts/<REPO>
gpg --verify checksums.txt.asc checksums.txt
grep -v ' (' checksums.txt | sha256sum -c
```

`gpg` must report a good signature from fingerprint
`6B7B 038D EB77 849F 1F61  5E67 CA38 8313 14D6 AA09`, and every file must be `OK`.
On realms-gos the files are `checksums-<TAG>.txt` and `checksums-<TAG>.txt.asc`.
Lines ending in `(module)` or `(bundle)` are derived hashes (decompressed wasm,
Casals bundle hash) used as deployment pins, not file names; `grep` skips them.

GitHub also attests each published release ("Release attestation" in its
assets): the tag's commit and the hash of every asset. To check that a file is
the one in the release:

```bash
gh release verify <TAG> -R smart-social-contracts/<REPO>
gh release verify-asset <TAG> <FILE> -R smart-social-contracts/<REPO>
```

