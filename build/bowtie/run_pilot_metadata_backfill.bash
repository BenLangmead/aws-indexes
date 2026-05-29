#!/usr/bin/env bash
# Pilot metadata-only backfill: small genomes (yeast, fruit fly, C. elegans).
# Requires: samtools, curl, zip, aws (credentials for genome-idx), network.
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

for cmd in samtools curl zip aws; do
    command -v "$cmd" >/dev/null 2>&1 || {
        printf 'error: %s not on PATH\n' "$cmd" >&2
        exit 1
    }
done

exec ./build_indexes.bash --metadata-only --backfill \
    --from-s3-prefix "${FROM_S3_PREFIX:-s3://genome-idx/bt}" \
    --targets legacy_targets.tsv \
    --upload-prefix "${UPLOAD_PREFIX:-s3://genome-idx/bt}" \
    r6411 bdgp6 wbcel235
