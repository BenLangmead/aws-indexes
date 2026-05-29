#!/usr/bin/env bash
# Run metadata-only backfill for every row in legacy_targets.tsv (requires AWS CLI,
# samtools, curl, zip, and network access to S3 and FASTA URLs).
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

ids=()
while IFS=$'\t' read -r id _rest; do
    [[ -z "${id:-}" || "${id:0:1}" == "#" ]] && continue
    ids+=("$id")
done < legacy_targets.tsv

if [[ "${#ids[@]}" -eq 0 ]]; then
    printf 'error: no target ids found in legacy_targets.tsv\n' >&2
    exit 1
fi

exec ./build_indexes.bash --metadata-only --backfill \
    --from-s3-prefix "${FROM_S3_PREFIX:-s3://genome-idx/bt}" \
    --targets legacy_targets.tsv \
    --upload-prefix "${UPLOAD_PREFIX:-s3://genome-idx/bt}" \
    "${ids[@]}"
