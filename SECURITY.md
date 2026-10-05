# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in any Smart Social Contracts project, please report it responsibly via encrypted email.

**Email:** contact@smartsocialcontracts.org

**PGP Fingerprint:** `6B7B 038D EB77 849F 1F61  5E67 CA38 8313 14D6 AA09`

**PGP Public Key:** [`pgp-key.asc`](pgp-key.asc)

Please **do not** open a public GitHub issue for security vulnerabilities.

## Verifying a release

Releases of Casals, gos-as-a-service, realms-gos and file-registry ship a
checksum file (`checksums.txt`, or `checksums-<tag>.txt` on realms-gos) and its
detached signature (`<checksum file>.asc`), made with the key above on a
hardware token. CI builds the release as a draft; it is published only after
the checksum file is signed, and a published release whose signature does not
verify is returned to draft.

```bash
gpg --import pgp-key.asc
gpg --verify checksums.txt.asc checksums.txt
sha256sum --ignore-missing -c checksums.txt
```

`gpg` must report a good signature from fingerprint
`6B7B 038D EB77 849F 1F61  5E67 CA38 8313 14D6 AA09`. Lines marked `(bundle)` or
`(module)` are derived hashes (Casals bundle hash, decompressed wasm) and are
skipped by `sha256sum -c`.
