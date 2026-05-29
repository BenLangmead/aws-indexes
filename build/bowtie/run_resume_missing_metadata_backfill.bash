#!/usr/bin/env bash
# Resume metadata backfill for catalog rows still missing sidecars on S3.
# Runs one build_indexes.bash invocation per id so a single failure does not stop the batch.
set -u
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

export AWS_PROFILE="${AWS_PROFILE:-index-zone-s3}"
log="${RESUME_LOG:-${script_dir}/legacy_backfill_resume.log}"

missing=()
while IFS=$'\t' read -r status short _rest; do
    [[ "$status" == MISSING ]] || continue
    missing+=("$short")
done < <(python3 audit_s3.py --require-metadata 2>/dev/null || true)

if [[ "${#missing[@]}" -eq 0 ]]; then
    printf 'No MISSING rows from audit_s3.py; nothing to do.\n' | tee -a "$log"
    exit 0
fi

{
    echo ""
    echo "=== resume_missing $(date "+%Y-%m-%dT%H:%M:%S%z") count=${#missing[@]} ==="
    printf 'IDs: %s\n' "${missing[*]}"
} >>"$log"

ok=0
fail=0
for id in "${missing[@]}"; do
    printf '\n--- %s %s ---\n' "$(date "+%Y-%m-%dT%H:%M:%S%z")" "$id" >>"$log"
    cmd=(./build_indexes.bash --metadata-only --backfill
        --from-s3-prefix "${FROM_S3_PREFIX:-s3://genome-idx/bt}"
        --targets legacy_targets.tsv
        --upload-prefix "${UPLOAD_PREFIX:-s3://genome-idx/bt}")
    if [[ "$id" == grch37 ]]; then
        cmd+=(--force)
    fi
    cmd+=("$id")
    if "${cmd[@]}" >>"$log" 2>&1; then
        printf 'OK %s\n' "$id" >>"$log"
        ok=$((ok + 1))
    else
        ec=$?
        printf 'FAIL %s exit=%s\n' "$id" "$ec" >>"$log"
        fail=$((fail + 1))
    fi
done

{
    echo "=== resume_missing done $(date "+%Y-%m-%dT%H:%M:%S%z") ok=$ok fail=$fail ==="
    python3 audit_s3.py --require-metadata 2>&1 | awk '/^OK\t|^MISSING\t/' || true
} >>"$log" 2>&1

exit 0
