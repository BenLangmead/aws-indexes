#!/bin/bash
#
# Granular PMU benchmarking of the movi-co k-mer coroutine query on a bare-metal
# (full-PMU) box. Runs as root so perf PEBS sampling + likwid uncore counters work.
#
# Two regimes (no-ftab = compute-heavy; ftab-10 = the realistic, memory-bound one)
# x latency-hiding width W in {1,8}. For each we collect:
#   - perf stat : IPC, L3-miss loads, DRAM-stall cycles, and MLP (offcore outstanding)
#   - perf record (mem_load_retired.l3_miss:pp) -> per-SOURCE-LINE attribution of the
#     loads that actually miss to DRAM  (the thing we could not get on Rockfish)
#   - likwid    : TMA top-down, CYCLE_STALLS, MEM (DRAM bandwidth)
# A 1-read run (one453) per regime bounds the index-load contribution for differencing.
#
# Env (exported by user data): BENCH CO IDX K FTABK READS_DIR RESULTS_S3 UPLOAD_PROFILE
# Results upload assumes the cross-account genome-idx upload role via the
# UPLOAD_PROFILE (credential_source=Ec2InstanceMetadata) -- no permanent creds.
set -u
: "${BENCH:?}"; : "${CO:?}"; : "${IDX:?}"; : "${K:=31}"; : "${FTABK:=10}"
: "${READS_DIR:?}"; : "${RESULTS_S3:?}"; : "${UPLOAD_PROFILE:=data-langmead}"

# Read files (movi-co reads .gz transparently via gzopen).
MAIN_READS="${MAIN_READS:-real_100k.fasta.gz}"   # main workload
LOAD_READS="${LOAD_READS:-one453.fasta}"         # 1-read = index-load baseline

OUT="$BENCH/results"; mkdir -p "$OUT"
LOG="$OUT/run.log"; exec > >(tee -a "$LOG") 2>&1
echo "=== run_bench start $(date) on $(hostname) ==="

# --- make the PMU fully available (we are root on metal) ---
sysctl -w kernel.perf_event_paranoid=-1 >/dev/null
sysctl -w kernel.kptr_restrict=0 >/dev/null

# Pin everything to one physical core on NUMA node 0 (c5.metal is 2-socket; keep the
# 37 GB index and the worker on the same node so cross-socket latency can't confound).
CORE=2
PIN="numactl --cpunodebind=0 --membind=0 taskset -c $CORE"

lscpu | grep -E "Model name|Socket|NUMA node\(s\)|node0 CPU" || true
echo "perf_event_paranoid=$(cat /proc/sys/kernel/perf_event_paranoid)"

echo "warming index..."; cat "$IDX/index.movi" > /dev/null; echo "warm $(date)"

# Cascade Lake events. l3_miss / stalls / offcore-outstanding (MLP) are the key ones.
EVENTS="cycles,instructions,\
mem_load_retired.l1_hit,mem_load_retired.l2_hit,mem_load_retired.l3_hit,mem_load_retired.l3_miss,\
cycle_activity.stalls_l3_miss,cycle_activity.stalls_mem_any,cycle_activity.stalls_total,\
offcore_requests_outstanding.cycles_with_data_rd,offcore_requests_outstanding.all_data_rd"

# args for movi-co given a regime
co_args () { # regime W readfile
  local regime=$1 W=$2 rf=$3
  if [ "$regime" = "ftab10" ]; then
    echo "--kmer --ftab-k $FTABK -k $K $READS_DIR/$rf $IDX $W"
  else
    echo "--kmer -k $K $READS_DIR/$rf $IDX $W"
  fi
}

perf_stat () { # tag regime W readfile
  local tag=$1; local a; a=$(co_args "$2" "$3" "$4")
  echo "--- perf stat $tag ---"
  $PIN perf stat -e "$EVENTS" -o "$OUT/$tag.perfstat.txt" -- "$CO" $a > "$OUT/$tag.stdout" 2> "$OUT/$tag.stderr"
}

perf_lines () { # tag regime W readfile  -> per-source-line DRAM-miss attribution
  local tag=$1; local a; a=$(co_args "$2" "$3" "$4")
  echo "--- perf record (l3_miss:pp) $tag ---"
  $PIN perf record -o "$OUT/$tag.l3miss.data" -e mem_load_retired.l3_miss:pp -c 2003 \
       -- "$CO" $a >/dev/null 2>>"$OUT/$tag.stderr"
  # per-source-line and per-symbol histograms (needs the RelWithDebInfo build)
  perf report -i "$OUT/$tag.l3miss.data" --stdio -g none --sort=srcline,symbol 2>/dev/null \
       | head -60 > "$OUT/$tag.l3miss.byline.txt"
  perf report -i "$OUT/$tag.l3miss.data" --stdio -g none --sort=symbol 2>/dev/null \
       | head -40 > "$OUT/$tag.l3miss.bysym.txt"
  gzip -f "$OUT/$tag.l3miss.data"
}

likwid_case () { # tag regime W readfile group
  local tag=$1; local grp=$5; local a; a=$(co_args "$2" "$3" "$4")
  echo "--- likwid $grp $tag ---"
  likwid-perfctr -C "$CORE" -g "$grp" -- "$CO" $a > "$OUT/$tag.likwid.$grp.txt" 2>&1
}

for regime in noftab ftab10; do
  for W in 1 8; do
    tag="${regime}_w${W}"
    perf_stat   "$tag"          "$regime" "$W" "$MAIN_READS"
    likwid_case "$tag" "$regime" "$W" "$MAIN_READS" TMA
    likwid_case "$tag" "$regime" "$W" "$MAIN_READS" CYCLE_STALLS
    likwid_case "$tag" "$regime" "$W" "$MAIN_READS" MEM
  done
  # deserialize/startup baseline (1 read) for differencing out the index load
  perf_stat "${regime}_load" "$regime" 1 "$LOAD_READS"
  # per-line DRAM-miss attribution at the best width (and W1 for contrast)
  perf_lines "${regime}_w8_lines" "$regime" 8 "$MAIN_READS"
  perf_lines "${regime}_w1_lines" "$regime" 1 "$MAIN_READS"
done

echo "=== run_bench done $(date) ==="
tar czf "$BENCH/movi_kmer_pmu_results.tar.gz" -C "$BENCH" results
AWS="aws --profile $UPLOAD_PROFILE s3 cp"
$AWS "$BENCH/movi_kmer_pmu_results.tar.gz" "$RESULTS_S3/movi_kmer_pmu_results.tar.gz"
$AWS "$LOG" "$RESULTS_S3/run.log"
echo "DONE $(date)" | $AWS - "$RESULTS_S3/SENTINEL_DONE"
echo "=== uploaded to $RESULTS_S3 ==="
