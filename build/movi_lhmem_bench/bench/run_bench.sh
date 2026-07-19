#!/bin/bash
#
# LH + MEM profiling on bare-metal (full-PMU) c5.metal, run as root.
# Index = movi2_hprc1_thresh (the ~94-haplotype HPRC pangenome, 37.6 GB).
#
# Exp1 (answers a/b): PML vanilla vs strand vs coroutine at W in {8,16,32}.
#   Question: why does strand LH beat coroutine LH for PML on the pangenome?
#   PML does NOT use the ftab (verified in source), so there is no ftab axis here.
#   PMU per cell + per-source-line (cycles & L3-miss) on strand vs coroutine.
#
# Exp2 (answers c/d): MEM vs k-mer vs PML decomposition + MEM cost sweep.
#   Question: why is --mem ~100x slower? Compute-bound O(#runs) bidirectional
#   scans vs the O(1)/base LF chase of pml/kmer. IPC + L3-miss/base is the
#   compute-vs-memory test; per-line shows extend_bidirectional / count() cost.
#   Sweep min_mem_length {12,20,31} at ftab-k 12 (isolates the L>ftab_k slow
#   path) plus an ftab-k 10 point.
#
# Env (exported by user data): BENCH CO PROD IDX READS_DIR RESULTS_S3 UPLOAD_PROFILE
set -u
: "${BENCH:?}"; : "${CO:?}"; : "${PROD:?}"; : "${IDX:?}"; : "${READS_DIR:?}"; : "${RESULTS_S3:?}"
: "${UPLOAD_PROFILE:=data-langmead}"

OUT="$BENCH/results"; mkdir -p "$OUT"
LOG="$OUT/run.log"; exec > >(tee -a "$LOG") 2>&1
echo "=== run_bench (LH+MEM) start $(date) on $(hostname) ==="
echo "PROD=$PROD"; echo "CO=$CO"; echo "IDX=$IDX"; "$PROD" 2>&1 | head -2 || true

sysctl -w kernel.perf_event_paranoid=-1 >/dev/null
sysctl -w kernel.kptr_restrict=0 >/dev/null
CORE=2
PIN="numactl --cpunodebind=0 --membind=0 taskset -c $CORE"
lscpu | grep -E "Model name|Socket\(s\)|NUMA node\(s\)" || true
echo "perf_event_paranoid=$(cat /proc/sys/kernel/perf_event_paranoid)"

# Cascade Lake PMU event set (reference.md). IPC, cache hit/miss ladder, stall
# cycles, MLP (outstanding offcore reads), branch mispredicts.
EV="cycles,instructions,mem_load_retired.l1_hit,mem_load_retired.l2_hit,mem_load_retired.l3_hit,mem_load_retired.l3_miss,cycle_activity.stalls_l3_miss,cycle_activity.stalls_mem_any,cycle_activity.stalls_total,offcore_requests_outstanding.cycles_with_data_rd,offcore_requests_outstanding.all_data_rd,br_misp_retired.all_branches"

# --- decompress reads (production movi -r does NOT read .gz; feed plain FASTA to
#     both PROD and CO so the comparison is apples-to-apples). ---
echo "=== preparing reads $(date) ==="
PML_GZ="$READS_DIR/real_100k.fasta.gz"
MEM_GZ="$READS_DIR/mem2k.fasta.gz"
PMLREADS="$READS_DIR/pml.fasta"; gunzip -c "$PML_GZ" > "$PMLREADS"
MEMSRC="$READS_DIR/mem2k.fasta"; gunzip -c "$MEM_GZ" > "$MEMSRC"
# MEM is ~100x slower -> cap it so each cell is ~tens of seconds (enough for PMU).
MEMREADS="$READS_DIR/mem256.fasta"; awk '/^>/{n++} n>256{exit} {print}' "$MEMSRC" > "$MEMREADS"
echo "PML reads: $(grep -c '^>' "$PMLREADS")   MEM reads: $(grep -c '^>' "$MEMREADS")"

echo "warming index..."; cat "$IDX/index.movi" > /dev/null; echo "warm $(date)"

# run one labeled cell under perf stat; capture the tool's own ns/base too.
# args: label  outprefix  cmd...
cell () {
  local label="$1" pfx="$2"; shift 2
  echo "--- CELL $label $(date) ---"
  $PIN perf stat -o "$OUT/$pfx.perfstat.txt" -e "$EV" -- "$@" >/dev/null 2>"$OUT/$pfx.tool.err"
  grep -oE 'processing the reads: [0-9.]+|elapsed: [0-9.]+ sec, [0-9.]+ ns/base|[0-9.]+ ns/base' "$OUT/$pfx.tool.err" | head -2 | tr '\n' ' '
  echo "  [$label]"
}

############################################################################
# Exp1 — PML: vanilla vs strand vs coroutine, W in {8,16,32}.  (no ftab)
############################################################################
echo "########## EXP1 PML (a/b) $(date) ##########"
cell "pml vanilla"      e1_pml_vanilla   $PROD query --index "$IDX" --read "$PMLREADS" --pml -t 1 --no-prefetch --no-output
for W in 8 16 32; do
  cell "pml strand W=$W"    e1_pml_strand_w$W  $PROD query --index "$IDX" --read "$PMLREADS" --pml -t 1 -s $W --no-output
  cell "pml coroutine W=$W" e1_pml_coro_w$W    $CO "$PMLREADS" "$IDX" $W
done

# per-source-line attribution at W=16: where coroutine spends cycles strand doesn't.
echo "=== EXP1 per-line (cycles + L3-miss), W=16 $(date) ==="
perfline () { # tag  cmd...
  local tag="$1"; shift
  $PIN perf record -o "$OUT/$tag.cycles.data" -e cycles -F 1999 -- "$@" >/dev/null 2>>"$OUT/$tag.rec.err"
  perf report -i "$OUT/$tag.cycles.data" --stdio -g none --sort=srcline,symbol 2>/dev/null | head -50 > "$OUT/$tag.cycles.byline.txt"
  perf report -i "$OUT/$tag.cycles.data" --stdio -g none --sort=symbol        2>/dev/null | head -25 > "$OUT/$tag.cycles.bysym.txt"
  $PIN perf record -o "$OUT/$tag.l3.data" -e mem_load_retired.l3_miss:pp -c 2003 -- "$@" >/dev/null 2>>"$OUT/$tag.rec.err"
  perf report -i "$OUT/$tag.l3.data" --stdio -g none --sort=srcline,symbol 2>/dev/null | head -40 > "$OUT/$tag.l3.byline.txt"
  gzip -f "$OUT/$tag.cycles.data" "$OUT/$tag.l3.data" 2>/dev/null || true
}
perfline e1_line_strand   $PROD query --index "$IDX" --read "$PMLREADS" --pml -t 1 -s 16 --no-output
perfline e1_line_coro     $CO "$PMLREADS" "$IDX" 16

############################################################################
# Exp2 — MEM vs k-mer vs PML decomposition + MEM cost sweep.
############################################################################
echo "########## EXP2 MEM/kmer/pml decomposition (c/d) $(date) ##########"
K=31           # k-mer length
# Same (small) read set for all three so per-base comparison is apples-to-apples.
cell "e2 pml"   e2_pml    $PROD query --index "$IDX" --read "$MEMREADS" --pml -t 1 --no-output
cell "e2 kmer"  e2_kmer   $PROD query --index "$IDX" --read "$MEMREADS" --kmer -k $K -t 1 --ftab-k 12 --multi-ftab --no-output
cell "e2 mem L31 ftab12" e2_mem_l31_f12 $PROD query --index "$IDX" --read "$MEMREADS" --mem -l 31 -t 1 --ftab-k 12 --no-output

# MEM slow-path sweep: L in {12,20,31} at ftab-k 12 (L<=ftab_k=12 is the fast path).
for L in 12 20; do
  cell "e2 mem L$L ftab12" e2_mem_l${L}_f12 $PROD query --index "$IDX" --read "$MEMREADS" --mem -l $L -t 1 --ftab-k 12 --no-output
done
# and an ftab-k 10 point at L31 (deeper into the slow path).
cell "e2 mem L31 ftab10" e2_mem_l31_f10 $PROD query --index "$IDX" --read "$MEMREADS" --mem -l 31 -t 1 --ftab-k 10 --no-output

# per-source-line on MEM (cycles) — expect extend_bidirectional scan + count().
echo "=== EXP2 per-line (cycles) MEM vs kmer $(date) ==="
perfcycles () { local tag="$1"; shift
  $PIN perf record -o "$OUT/$tag.cycles.data" -e cycles -F 1999 -- "$@" >/dev/null 2>>"$OUT/$tag.rec.err"
  perf report -i "$OUT/$tag.cycles.data" --stdio -g none --sort=srcline,symbol 2>/dev/null | head -60 > "$OUT/$tag.cycles.byline.txt"
  perf report -i "$OUT/$tag.cycles.data" --stdio -g none --sort=symbol        2>/dev/null | head -30 > "$OUT/$tag.cycles.bysym.txt"
  gzip -f "$OUT/$tag.cycles.data" 2>/dev/null || true
}
perfcycles e2_line_mem   $PROD query --index "$IDX" --read "$MEMREADS" --mem -l 31 -t 1 --ftab-k 12 --no-output
perfcycles e2_line_kmer  $PROD query --index "$IDX" --read "$MEMREADS" --kmer -k $K -t 1 --ftab-k 12 --multi-ftab --no-output

# likwid top-down (compute vs memory bound) on MEM and PML for the headline (c) claim.
echo "=== likwid TMA (MEM vs PML) $(date) ==="
likwid-perfctr -C $CORE -g TMA -- $PROD query --index "$IDX" --read "$MEMREADS" --mem -l 31 -t 1 --ftab-k 12 --no-output > "$OUT/likwid_mem_tma.txt" 2>&1 || echo "likwid mem failed" >> "$OUT/likwid_mem_tma.txt"
likwid-perfctr -C $CORE -g TMA -- $PROD query --index "$IDX" --read "$MEMREADS" --pml -t 1 --no-output > "$OUT/likwid_pml_tma.txt" 2>&1 || echo "likwid pml failed" >> "$OUT/likwid_pml_tma.txt"

echo "=== run_bench done $(date) ==="
cp "$PROD" "$OUT/movi-regular-thresholds" 2>/dev/null || true
cp "$CO" "$OUT/movi-co" 2>/dev/null || true
tar czf "$BENCH/movi_lhmem_pmu_results.tar.gz" -C "$BENCH" results
AWS="aws --profile $UPLOAD_PROFILE s3 cp"
$AWS "$BENCH/movi_lhmem_pmu_results.tar.gz" "$RESULTS_S3/movi_lhmem_pmu_results.tar.gz"
$AWS "$LOG" "$RESULTS_S3/run.log"
echo "DONE $(date)" | $AWS - "$RESULTS_S3/SENTINEL_DONE"
echo "=== uploaded to $RESULTS_S3 ==="
