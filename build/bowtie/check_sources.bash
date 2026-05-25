#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
targets_file="${TARGETS_FILE:-${script_dir}/targets.tsv}"
curl_bin="${CURL:-curl}"

if [[ "${1:-}" == "--targets" ]]; then
    targets_file="$2"
    shift 2
fi

if [[ ! -f "$targets_file" ]]; then
    printf 'error: target file does not exist: %s\n' "$targets_file" >&2
    exit 1
fi

if ! command -v "$curl_bin" >/dev/null 2>&1; then
    printf 'error: required command not found: %s\n' "$curl_bin" >&2
    exit 1
fi

failures=0
while IFS=$'\t' read -r id index_base species assembly source url expected_ext notes; do
    [[ -z "${id:-}" || "${id:0:1}" == "#" ]] && continue
    printf 'Checking %-12s %s\n' "$id" "$url"
    if ! "$curl_bin" --fail --location --head --silent --show-error "$url" >/dev/null; then
        printf 'FAILED: %s\n' "$id" >&2
        failures=$((failures + 1))
    fi
done < "$targets_file"

if [[ "$failures" -ne 0 ]]; then
    printf 'error: %s source URL check(s) failed\n' "$failures" >&2
    exit 1
fi
