#!/usr/bin/env python3
"""Check a downloaded release directory against its checksum file.

    check-release-assets.py DIR

DIR holds every asset of one GitHub release. Exactly one checksum file must be
present (checksums.txt or checksums-<tag>.txt). Every `<sha256>  <file>` line
must match the file's bytes, and every asset except the checksum file and its
`.asc` signature must be listed. Lines with a trailing `(bundle)`, `(module)`
or `(tar)` are derived hashes (Casals bundle hash, decompressed wasm, the tar
inside a source `.tar.gz`) and are not file hashes. Releases cut before
manifests were listed leave `*.manifest.json` uncovered; that is reported as a
warning.

Prints the checksum file name on success; exits 1 on any mismatch.
"""

import gzip
import hashlib
import re
import sys
from pathlib import Path

LINE = re.compile(r"^([0-9a-f]{64})\s+\*?(\S+)\s*(\((bundle|module|tar)\))?\s*$")


def main(directory: str) -> int:
    root = Path(directory)
    names = sorted(p.name for p in root.iterdir() if p.is_file())
    sums = [n for n in names if re.fullmatch(r"checksums(-v[0-9][^/]*)?\.txt", n)]
    if len(sums) != 1:
        print(f"expected one checksum file, found {sums or 'none'}", file=sys.stderr)
        return 1
    sums_name = sums[0]

    listed, errors = set(), []
    for raw in (root / sums_name).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = LINE.match(line)
        if not m:
            errors.append(f"unparsable line: {raw!r}")
            continue
        digest, name, derived = m.group(1), m.group(2), m.group(4)
        if derived == "tar":
            # A .tar.gz is not byte-reproducible -- the deflate stream differs by
            # zlib version -- but the tar inside it is. This line is the hash we
            # attest for the source, so unlike the other derived hashes it is
            # checked here: a wrong one would otherwise be signed unnoticed.
            path = root / name
            if not path.is_file():
                errors.append(f"{name}: a (tar) line names an archive not attached to the release")
                continue
            try:
                inner = gzip.decompress(path.read_bytes())
            except (OSError, EOFError) as exc:
                errors.append(f"{name}: a (tar) line names something that is not gzip ({exc})")
                continue
            actual = hashlib.sha256(inner).hexdigest()
            if actual != digest:
                errors.append(f"{name}: the tar inside it is sha256 {actual}, not {digest}")
            continue
        if derived:
            continue
        path = root / name
        if not path.is_file():
            errors.append(f"{name}: listed but not attached to the release")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"{name}: sha256 {actual} does not match {digest}")
        listed.add(name)

    for name in names:
        if name in listed or name in (sums_name, f"{sums_name}.asc"):
            continue
        if name.endswith(".manifest.json"):
            print(f"warning: {name} is not covered by {sums_name}", file=sys.stderr)
        else:
            errors.append(f"{name}: attached but not covered by {sums_name}")

    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        return 1
    print(sums_name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
