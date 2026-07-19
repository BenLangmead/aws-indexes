#!/bin/bash
#
# PML coroutine A/B on bare-metal (full-PMU) c5.metal, run as root.
#
# Question: the primitive-REUSING query_pml_coroutine (reposition_thresholds /
# get_id / LF_move) measured ~14% slower than the hand-INLINED loop on a noisy
# shared box. Does LTO (cross-TU inlining of those primitives) close the gap, and
# if not, WHERE does the residual time go?
#
# We build three movi-co variants from the same source and time PML at W=8:
#   lto_reuse    : reuse primitives + LTO        (the candidate)
#   lto_inline   : hand-inlined loop + LTO       (best case, LTO held constant)
#   nolto_inline : hand-inlined loop, no LTO     (the currently-shipped binary)
# Then perf record (cycles) -> per-source-line attribution on the two LTO binaries
# to see exactly what the reuse path spends that the inline path doesn't (the
# hypothesis: LF_move's per-call is_logs()/ff_counts/bounds-throw bookkeeping).
#
# Env (exported by user data): BENCH IDX READS_DIR RESULTS_S3 UPLOAD_PROFILE
set -u
: "${BENCH:?}"; : "${IDX:?}"; : "${READS_DIR:?}"; : "${RESULTS_S3:?}"
: "${UPLOAD_PROFILE:=data-langmead}"
SRC="${SRC:-$(dirname "$(find "$BENCH/Movi" -maxdepth 3 -name CMakeLists.txt | head -1)")}"
READS="${READS:-real_100k.fasta.gz}"   # movi-co reads .gz directly via gzopen
W=8
NREPS=7

OUT="$BENCH/results"; mkdir -p "$OUT"
LOG="$OUT/run.log"; exec > >(tee -a "$LOG") 2>&1
echo "=== run_bench (PML A/B) start $(date) on $(hostname) ==="
echo "SRC=$SRC  READS=$READS  W=$W  NREPS=$NREPS"

sysctl -w kernel.perf_event_paranoid=-1 >/dev/null
sysctl -w kernel.kptr_restrict=0 >/dev/null
CORE=2
PIN="numactl --cpunodebind=0 --membind=0 taskset -c $CORE"
lscpu | grep -E "Model name|Socket\(s\)|NUMA node\(s\)" || true
echo "perf_event_paranoid=$(cat /proc/sys/kernel/perf_event_paranoid)"

# --- build the three variants (RelWithDebInfo => -O2 -g, so perf maps to source) ---
declare -A BIN
build_variant () { # name  src_basename  lto(ON/OFF)  flatten(ON/OFF)
  local name=$1 srcfile=$2 lto=$3
  local bd="$BENCH/build_$name"
  echo "--- building $name (src=$srcfile MOVI_CO_LTO=$lto) $(date) ---"
  rm -rf "$bd"; mkdir -p "$bd"
  cp "$SRC/src/$srcfile" "$SRC/src/movi_co.cpp"
  ( cd "$bd" && cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DMOVI_CO_LTO="$lto" -DMOVI_PML_FLATTEN="${4:-OFF}" "$SRC" >cmake.log 2>&1 \
       && cmake --build . --target movi-co -j"$(nproc)" >build.log 2>&1 )
  BIN[$name]="$(find "$bd" -name movi-co -type f | head -1)"
  echo "$name -> ${BIN[$name]}"
  cp "${BIN[$name]}" "$OUT/movi-co-$name" 2>/dev/null || true
}
build_variant lto_reuse         movi_co.cpp         ON  OFF
build_variant lto_reuse_flatten movi_co.cpp         ON  ON
build_variant lto_inline        movi_co_inline.cpp  ON  OFF
build_variant nolto_inline      movi_co_inline.cpp  OFF OFF

echo "warming index..."; cat "$IDX/index.movi" > /dev/null; echo "warm $(date)"

# --- timing: ns/base at W=8, NREPS reps, variants interleaved per rep ---
echo "=== TIMING (ns/base, W=$W) ==="
for rep in $(seq 1 "$NREPS"); do
  for v in lto_reuse lto_reuse_flatten lto_inline nolto_inline; do
    $PIN "${BIN[$v]}" "$READS_DIR/$READS" "$IDX" "$W" >/dev/null 2>"$OUT/t_${v}_r${rep}.err"
    ns=$(grep -oE '[0-9.]+ ns/base' "$OUT/t_${v}_r${rep}.err" | head -1)
    echo "TIME rep$rep $v = ${ns:-NA}"
  done
done

# --- per-source-line PEBS (cycles) on the two LTO binaries ---
for v in lto_reuse_flatten lto_inline; do
  echo "--- perf record cycles $v $(date) ---"
  ${PIN} perf record -o "$OUT/$v.cycles.data" -e cycles -F 1999 \
       -- "${BIN[$v]}" "$READS_DIR/$READS" "$IDX" "$W" >/dev/null 2>>"$OUT/$v.perf.err"
  perf report -i "$OUT/$v.cycles.data" --stdio -g none --sort=srcline,symbol 2>/dev/null | head -60 > "$OUT/$v.cycles.byline.txt"
  perf report -i "$OUT/$v.cycles.data" --stdio -g none --sort=symbol  2>/dev/null | head -30 > "$OUT/$v.cycles.bysym.txt"
  gzip -f "$OUT/$v.cycles.data"
done

echo "=== run_bench (PML A/B) done $(date) ==="
tar czf "$BENCH/movi_pml_pmu_results.tar.gz" -C "$BENCH" results
AWS="aws --profile $UPLOAD_PROFILE s3 cp"
$AWS "$BENCH/movi_pml_pmu_results.tar.gz" "$RESULTS_S3/movi_pml_pmu_results.tar.gz"
$AWS "$LOG" "$RESULTS_S3/run.log"
echo "DONE $(date)" | $AWS - "$RESULTS_S3/SENTINEL_DONE"
echo "=== uploaded to $RESULTS_S3 ==="
