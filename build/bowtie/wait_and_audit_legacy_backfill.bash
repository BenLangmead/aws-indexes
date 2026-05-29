#!/usr/bin/env bash
# Wait for legacy_backfill_remaining.log to get an EXIT: line (or build_indexes to
# disappear without EXIT — then annotate), append progress periodically, then run
# audit_s3.py --require-metadata --strict.  Intended to be started after the main
# backfill is already running:  nohup ./wait_and_audit_legacy_backfill.bash &
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"
repo_root="$(cd "$script_dir/../.." && pwd)"
log="$script_dir/legacy_backfill_remaining.log"
watch_log="$script_dir/legacy_backfill_watch.log"

{
  echo "=== $(date "+%Y-%m-%dT%H:%M:%S%z") wait_and_audit started ==="
  while true; do
    if [[ -f "$log" ]] && grep -q '^EXIT:' "$log" 2>/dev/null; then
      echo "=== $(date "+%Y-%m-%dT%H:%M:%S%z") saw EXIT in main log ==="
      grep '^EXIT:' "$log" || true
      break
    fi
    if ! pgrep -f '[b]uild_indexes.bash --metadata-only' >/dev/null 2>&1; then
      sleep 15
      if [[ -f "$log" ]] && grep -q '^EXIT:' "$log" 2>/dev/null; then
        echo "=== $(date "+%Y-%m-%dT%H:%M:%S%z") EXIT after process exit ==="
        break
      fi
      echo "=== $(date "+%Y-%m-%dT%H:%M:%S%z") build_indexes gone but no EXIT line; check $log ===" >&2
      break
    fi
    n=$(grep -c 'Finished metadata backfill for' "$log" 2>/dev/null || echo 0)
    echo "$(date "+%Y-%m-%dT%H:%M:%S%z") completed_targets=$n"
    sleep 300
  done

  echo "=== $(date "+%Y-%m-%dT%H:%M:%S%z") running audit_s3.py --require-metadata --strict ==="
  cd "$repo_root"
  AWS_PROFILE="${AWS_PROFILE:-index-zone-s3}" python3 build/bowtie/audit_s3.py --require-metadata --strict || true
  echo "=== $(date "+%Y-%m-%dT%H:%M:%S%z") audit finished (exit above may be non-zero if gaps remain) ==="
} >>"$watch_log" 2>&1
