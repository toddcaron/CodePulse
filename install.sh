#!/usr/bin/env bash
set -Eeuo pipefail

target_dir="${1:-${HOME}/.agents/skills}"
repository_url="${CODEPULSE_REPOSITORY_URL:-https://github.com/Todd-Caron_Taylor/CodePulse.git}"
mkdir -p "$(dirname "$target_dir")"
target_dir="$(cd "$(dirname "$target_dir")" && pwd)/$(basename "$target_dir")"
staging_dir="$(mktemp -d "${TMPDIR:-/tmp}/codepulse.XXXXXX")"

cleanup() {
    rm -rf "$staging_dir"
}
trap cleanup EXIT

mkdir -p "$target_dir"
git clone --depth 1 "$repository_url" "$staging_dir/repository"

for source_dir in "$staging_dir/repository"/*/; do
    [ -d "$source_dir" ] || continue
    cp -R "$source_dir" "$target_dir/"
done

printf 'CodePulse installed to %s\n' "$target_dir"