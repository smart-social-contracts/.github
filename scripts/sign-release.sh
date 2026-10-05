#!/usr/bin/env bash
# Sign a GitHub release with the release key and publish it.
#
#   sign-release.sh OWNER/REPO TAG
#
# Downloads every asset, checks them against the checksum file, writes a
# detached signature with the OpenPGP key on the prod YubiKey (PIN, then one
# touch), and uploads it. A draft is then published, which runs the repo's
# release-verify.yml; an already published release gets that check started by
# hand.
set -euo pipefail

FPR=6B7B038DEB77849F1F615E67CA38831314D6AA09

if [ $# -ne 2 ]; then
  sed -n '2,10p' "$0" >&2
  exit 2
fi
repo=$1
tag=$2
here=$(dirname "$(readlink -f "$0")")
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

draft=$(gh release view "$tag" -R "$repo" --json isDraft -q .isDraft)
gh release download "$tag" -R "$repo" -D "$work"
sums=$(python3 "$here/check-release-assets.py" "$work")
if [ -e "$work/$sums.asc" ]; then
  echo "$repo $tag already has $sums.asc" >&2
  exit 1
fi

echo "Signing $repo $tag $sums with $FPR"
gpg --local-user "$FPR" --armor --detach-sign --output "$work/$sums.asc" "$work/$sums"
signer=$(gpg --batch --status-fd 1 --verify "$work/$sums.asc" "$work/$sums" 2>/dev/null | awk '$2 == "VALIDSIG" { print $NF }')
if [ "$signer" != "$FPR" ]; then
  echo "the new signature does not verify against $FPR" >&2
  exit 1
fi

gh release upload "$tag" "$work/$sums.asc" -R "$repo"
if [ "$draft" = "true" ]; then
  gh release edit "$tag" -R "$repo" --draft=false
  echo "Published $repo $tag; release-verify.yml runs on the publish event."
else
  gh workflow run release-verify.yml -R "$repo" -f tag="$tag"
  echo "Signed the published $repo $tag; started release-verify.yml."
fi
