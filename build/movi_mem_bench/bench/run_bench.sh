#!/bin/bash
#
# Granular PMU benchmarking of the Movi MEM query on a bare-metal (full-PMU) box.
# Runs as root so perf PEBS sampling + likwid uncore counters work.
#
# We profile the MEM query along two axes:
#   - binary/path: production SEQUENTIAL MEM (movi-regular-thresholds query --mem,
#                  the real optimization target) vs the coroutine (movi-co --mem)
#                  at best latency-hiding width W=8.
#   - ftab depth : ftab-k in {10,12} (deeper ftab => fewer extension steps/MEM).
#
# (Trimmed from the full matrix to ~half runtime: co W=1 and the likwid MEM
#  bandwidth group were dropped; per-line attribution kept in full.)
#
# For each case we collect:
#   - perf stat : IPC, L3-miss loads, DRAM-stall cycles, and MLP (offcore outstanding)
#   - likwid    : TMA top-down, CYCLE_STALLS
# And at the two most informative cases per ftab regime (prod_seq + co_w8):
#   - perf record (mem_load_retired.l3_miss:pp) -> per-SOURCE-LINE attribution of
#     the loads that miss to DRAM           (WHERE the misses are)
#   - perf record (cycles)                   -> per-SOURCE-LINE attribution of
#     where time is spent                    (WHERE the time goes -- the key signal
#     for a compute/scan-bound query; e.g. extend_bidirectional scans vs LF_move)
# A 1-read run (one453) per binary/regime bounds the index-load contribution.
#
# Env (exported by user data): BENCH CO PROD IDX MIN_MEM_LEN FTAB_KS READS_DIR
#                              RESULTS_S3 UPLOAD_PROFILE
# Results upload assumes the cross-account genome-idx upload role via the
# UPLOAD_PROFILE (credential_source=Ec2InstanceMetadata) -- no permanent creds.
set -u
: "${BENCH:?}"; : "${CO:?}"; : "${PROD:?}"; : "${IDX:?}"
: "${MIN_MEM_LEN:=25}"; : "${FTAB_KS:=10 12}"
: "${READS_DIR:?}"; : "${RESULTS_S3:?}"; : "${UPLOAD_PROFILE:=data-langmead}"

# Read files. NOTE: movi-co reads .gz via gzopen, but the production
# movi-regular-thresholds `-r` reader does NOT (it errors "unrecognized input
# query file type"). So we decompress the main reads to plain FASTA once and feed
# the plain file to BOTH binaries.
MAIN_READS="${MAIN_READS:-mem2k.fasta.gz}"   # ~2000 reads, main MEM workload
LOAD_READS="${LOAD_READS:-one453.fasta}"     # 1-read = index-load baseline

if [[ "$MAIN_READS" == *.gz ]]; then
  PLAIN="${MAIN_READS%.gz}"
  [ -s "$READS_DIR/$PLAIN" ] || gunzip -kc "$READS_DIR/$MAIN_READS" > "$READS_DIR/$PLAIN"
  MAIN_READS="$PLAIN"
fi

OUT="$BENCH/results"; mkdir -p "$OUT"
SINK="$BENCH/sink"; mkdir -p "$SINK"   # production -o MEM output; kept out of results/
LOG="$OUT/run.log"; exec > >(tee -a "$LOG") 2>&1
echo "=== run_bench (MEM) start $(date) on $(hostname) ==="

# --- make the PMU fully available (we are root on metal) ---
sysctl -w kernel.perf_event_paranoid=-1 >/dev/null
sysctl -w kernel.kptr_restrict=0 >/dev/null

# Pin everything to one physical core on NUMA node 0 (c5.metal is 2-socket; keep
# the 37 GB index and the worker on the same node so cross-socket latency can't
# confound).
CORE=2
PIN="numactl --cpunodebind=0 --membind=0 taskset -c $CORE"

lscpu | grep -E "Model name|Socket|NUMA node\(s\)|node0 CPU" || true
echo "perf_event_paranoid=$(cat /proc/sys/kernel/perf_event_paranoid)"
echo "MIN_MEM_LEN=$MIN_MEM_LEN  FTAB_KS=$FTAB_KS"

echo "warming index..."; cat "$IDX/index.movi" > /dev/null; echo "warm $(date)"

# Cascade Lake events. l3_miss / stalls / offcore-outstanding (MLP) are the key ones.
EVENTS="cycles,instructions,\
mem_load_retired.l1_hit,mem_load_retired.l2_hit,mem_load_retired.l3_hit,mem_load_retired.l3_miss,\
cycle_activity.stalls_l3_miss,cycle_activity.stalls_mem_any,cycle_activity.stalls_total,\
offcore_requests_outstanding.cycles_with_data_rd,offcore_requests_outstanding.all_data_rd"

# Command builders. $1=ftabK, ($2=W for co). Output goes to a per-case sink so the
# two binaries' text output is symmetric and out of the timed comparison's way.
prod_cmd () {  # ftabK readfile outprefix
  echo "$PROD query -i $IDX -r $READS_DIR/$2 --mem --ftab-k $1 -l $MIN_MEM_LEN -t 1 -o $3"
}
co_cmd () {    # ftabK W readfile
  echo "$CO --mem --ftab-k $1 --min-mem-length $MIN_MEM_LEN $READS_DIR/$3 $IDX $2"
}

perf_stat () { # tag cmd...
  local tag=$1; shift
  echo "--- perf stat $tag ---"
  $PIN perf stat -e "$EVENTS" -o "$OUT/$tag.perfstat.txt" -- "$@" \
       > "$OUT/$tag.stdout" 2> "$OUT/$tag.stderr"
}

likwid_case () { # tag group cmd...
  local tag=$1 grp=$2; shift 2
  echo "--- likwid $grp $tag ---"
  likwid-perfctr -C "$CORE" -g "$grp" -- "$@" > "$OUT/$tag.likwid.$grp.txt" 2>&1
}

perf_lines () { # tag cmd...  -> per-source-line DRAM-miss AND cycles attribution
  local tag=$1; shift
  echo "--- perf record (l3_miss:pp) $tag ---"
  $PIN perf record -o "$OUT/$tag.l3miss.data" -e mem_load_retired.l3_miss:pp -c 2003 \
       -- "$@" >/dev/null 2>>"$OUT/$tag.stderr"
  perf report -i "$OUT/$tag.l3miss.data" --stdio -g none --sort=srcline,symbol 2>/dev/null \
       | head -60 > "$OUT/$tag.l3miss.byline.txt"
  perf report -i "$OUT/$tag.l3miss.data" --stdio -g none --sort=symbol 2>/dev/null \
       | head -40 > "$OUT/$tag.l3miss.bysym.txt"
  gzip -f "$OUT/$tag.l3miss.data"

  echo "--- perf record (cycles) $tag ---"
  $PIN perf record -o "$OUT/$tag.cycles.data" -e cycles -F 999 -g \
       -- "$@" >/dev/null 2>>"$OUT/$tag.stderr"
  perf report -i "$OUT/$tag.cycles.data" --stdio -g none --sort=srcline,symbol 2>/dev/null \
       | head -60 > "$OUT/$tag.cycles.byline.txt"
  perf report -i "$OUT/$tag.cycles.data" --stdio -g none --sort=symbol 2>/dev/null \
       | head -40 > "$OUT/$tag.cycles.bysym.txt"
  gzip -f "$OUT/$tag.cycles.data"
}

for ftabK in $FTAB_KS; do
  P="f${ftabK}"

  # production sequential MEM (the optimization target)
  perf_stat   "prod_seq_${P}"                $(prod_cmd "$ftabK" "$MAIN_READS" "$SINK/prod_seq_${P}")
  likwid_case "prod_seq_${P}" TMA            $(prod_cmd "$ftabK" "$MAIN_READS" "$SINK/prod_seq_${P}")
  likwid_case "prod_seq_${P}" CYCLE_STALLS   $(prod_cmd "$ftabK" "$MAIN_READS" "$SINK/prod_seq_${P}")

  # coroutine MEM at best width only (W=8); W=1 dropped to halve runtime
  for W in 8; do
    tag="co_w${W}_${P}"
    perf_stat   "$tag"              $(co_cmd "$ftabK" "$W" "$MAIN_READS")
    likwid_case "$tag" TMA          $(co_cmd "$ftabK" "$W" "$MAIN_READS")
    likwid_case "$tag" CYCLE_STALLS $(co_cmd "$ftabK" "$W" "$MAIN_READS")
  done

  # index-load baselines (1 read) for differencing out the deserialize cost
  perf_stat "prod_load_${P}" $(prod_cmd "$ftabK" "$LOAD_READS" "$SINK/prod_load_${P}")
  perf_stat "co_load_${P}"   $(co_cmd "$ftabK" "1" "$LOAD_READS")

  # per-source-line attribution (misses + cycles) at the two key cases
  perf_lines "prod_seq_${P}_lines" $(prod_cmd "$ftabK" "$MAIN_READS" "$SINK/prod_seq_${P}_lines")
  perf_lines "co_w8_${P}_lines"    $(co_cmd "$ftabK" "8" "$MAIN_READS")
done

echo "=== run_bench (MEM) done $(date) ==="
# Only the PMU artifacts in results/ go in the tarball (production -o MEM output
# was written to $SINK, outside results/).
tar czf "$BENCH/movi_mem_pmu_results.tar.gz" -C "$BENCH" results
AWS="aws --profile $UPLOAD_PROFILE s3 cp"
$AWS "$BENCH/movi_mem_pmu_results.tar.gz" "$RESULTS_S3/movi_mem_pmu_results.tar.gz"
$AWS "$LOG" "$RESULTS_S3/run.log"
echo "DONE $(date)" | $AWS - "$RESULTS_S3/SENTINEL_DONE"
echo "=== uploaded to $RESULTS_S3 ==="
