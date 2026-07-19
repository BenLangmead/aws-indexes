#!/bin/bash
# bench_lg_vs_grlbwt.sh -- compare lyndon-grammar (lg) vs grlBWT for the RLBWT
# construction step of the Movi pipeline. Measures, on the SAME prepared input:
#   * peak RAM   (/usr/bin/time -v Maximum resident set size)
#   * peak temp DISK  (background du sampler on each tool's work subdir; grlBWT's
#                      recursion temp `grltmp` is the thing that blew past 1.8 TB)
#   * wall time
#   * correctness: plain BWTs byte-identical (lg --mdolbwt == grlBWT, per lg README)
#
# Input is built the same way the production grlBWT path builds it:
#   agc getset <haps> -> movi-prepare-ref ... separators -> one %-separated, revcomp
#   string per line (grl_in.txt) with a trailing newline as the sentinel.
#
# Run detached:  nohup bash bench_lg_vs_grlbwt.sh >LOG 2>&1 &

set -uo pipefail

ARCHIVE="${ARCHIVE:-/data/blangme2/fasta/hprc-yr1/HPRC-yr1.agc}"
HAPS="${HAPS:?set HAPS to a comma/space list of agc sample names}"
TAG="${TAG:-lgbench}"
THREADS="${THREADS:-24}"
WORK="${WORK:-/tmp/lgbench/$TAG}"

LG="${LG:-$HOME/git/lyndongrammar/build/lg}"
GRL="${GRL:-$HOME/git/grlBWT/build/grlbwt-cli}"
GRL2PLAIN="${GRL2PLAIN:-$HOME/git/grlBWT/build/grl2plain}"
PREP="${PREP:-$HOME/git/movi-langmead/build/bin/movi-prepare-ref}"
AGC="${AGC:-$HOME/bin/agc}"
GNUTIME=/usr/bin/time

mkdir -p "$WORK"; LOG="$WORK/logs"; mkdir -p "$LOG"
STATUS="$LOG/STATUS.txt"; SUMMARY="$LOG/SUMMARY.txt"
exec 3>&1
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$STATUS" >&3; }
rss_kb(){ awk -F': ' '/Maximum resident set size/{print $2}' "$LOG/time.$1.txt" 2>/dev/null; }
human(){ awk -v b="$1" 'BEGIN{printf "%.1f", b/1073741824}'; }   # bytes -> GiB

# run LABEL SAMPLEDIR -- cmd... : time the cmd, disk-sample SAMPLEDIR while it runs.
run(){
    local label="$1" sdir="$2"; shift 2; [[ "${1:-}" == "--" ]] && shift
    say "START $label  (sampling $sdir)"
    local t0; t0=$(date +%s)
    setsid "$GNUTIME" -v -o "$LOG/time.$label.txt" "$@" \
        >"$LOG/$label.out" 2>"$LOG/$label.err" &
    local pid=$!
    ( local peak=0 b; while kill -0 "$pid" 2>/dev/null; do
         b=$(du -sb "$sdir" 2>/dev/null | awk '{print $1+0}')
         (( b > peak )) && { peak=$b; echo "$peak" > "$LOG/disk.$label"; }
         sleep 5
      done ) &
    local sp=$!
    wait "$pid"; local rc=$?
    kill "$sp" 2>/dev/null || true
    local t1; t1=$(date +%s); echo "$((t1-t0))" > "$LOG/wall.$label"
    say "DONE  $label rc=$rc  wall=$((t1-t0))s  peakRSS=$(human $(( $(rss_kb $label)*1024 )) )GiB  peakDisk=$(human $(cat $LOG/disk.$label 2>/dev/null||echo 0))GiB"
    return $rc
}

cd "$WORK"
say "=== bench start: $TAG (threads=$THREADS) ==="

# ---------- stage the shared, prepared input ----------
read -r -a _h <<< "${HAPS//,/ }"
say "staging ${#_h[@]} haplotypes via agc getset: ${_h[*]}"
"$AGC" getset -t "$THREADS" "$ARCHIVE" "${_h[@]}" > input.fa 2>"$LOG/getset.err"
say "input.fa $(du -h input.fa|cut -f1), $(grep -c '^>' input.fa) records"
"$PREP" input.fa clean.fa separators >"$LOG/prepare.out" 2>&1 || { say "prepare-ref FAILED"; exit 1; }
{ grep -v '^>' clean.fa | tr -d '\n'; echo; } > grl_in.txt
rm -f input.fa clean.fa clean.fa.doc_offsets
GRLIN_BYTES=$(wc -c < grl_in.txt)
say "grl_in.txt $(human $GRLIN_BYTES)GiB (~$((GRLIN_BYTES-1)) bp incl revcomp+separators)"

# ---------- grlBWT (BCR exact RLBWT) ----------
mkdir -p gbench/grltmp
run grlbwt gbench -- "$GRL" grl_in.txt -o gbench/grl_out -t "$THREADS" -T "$WORK/gbench/grltmp"
GRL_RC=$?
# isolate the recursion-temp peak we actually care about (separate from outputs)
GRLTMP_PEAK=$(cat "$LOG/disk.grlbwt" 2>/dev/null || echo 0)
if [[ $GRL_RC -eq 0 ]]; then
    "$GRL2PLAIN" gbench/grl_out.rl_bwt gbench/grl_plain.bwt >"$LOG/grl2plain.out" 2>&1 || say "grl2plain failed"
fi
rm -rf gbench/grltmp; say "removed grlBWT recursion temp"

# ---------- lyndon-grammar (plain BWT, mdolBWT == grlBWT) ----------
mkdir -p lgbench
run lg lgbench -- "$LG" --i grl_in.txt --lines --mdolbwt --terminal $'\n' --ob "$WORK/lgbench/lg_plain.bwt"
LG_RC=$?

# ---------- correctness: byte-identical plain BWTs ----------
BWTOK="n/a"
if [[ $GRL_RC -eq 0 && $LG_RC -eq 0 && -f gbench/grl_plain.bwt && -f lgbench/lg_plain.bwt ]]; then
    if cmp -s lgbench/lg_plain.bwt gbench/grl_plain.bwt; then BWTOK="IDENTICAL"; else BWTOK="DIFFER"; fi
fi

# ---------- summary ----------
gw=$(cat "$LOG/wall.grlbwt" 2>/dev/null||echo ?); lw=$(cat "$LOG/wall.lg" 2>/dev/null||echo ?)
gr=$(( $(rss_kb grlbwt 2>/dev/null||echo 0)*1024 )); lr=$(( $(rss_kb lg 2>/dev/null||echo 0)*1024 ))
gd=$(cat "$LOG/disk.grlbwt" 2>/dev/null||echo 0); ld=$(cat "$LOG/disk.lg" 2>/dev/null||echo 0)
{
    echo "lg vs grlBWT bench -- $TAG"
    echo "================================"
    echo "Input      : ${#_h[@]} haplotypes, grl_in.txt $(human $GRLIN_BYTES)GiB (revcomp+separators)"
    echo "Threads    : $THREADS    Host: $(hostname)"
    echo
    printf "%-10s %14s %14s %12s\n" "tool" "peakRSS_GiB" "peakDisk_GiB" "wall_s"
    printf "%-10s %14s %14s %12s\n" "grlBWT" "$(human $gr)" "$(human $gd)" "$gw"
    printf "%-10s %14s %14s %12s\n" "lg"     "$(human $lr)" "$(human $ld)" "$lw"
    echo
    echo "grlBWT recursion-temp peak (grltmp+outputs) : $(human $GRLTMP_PEAK)GiB"
    echo "BWT correctness (plain, byte-identical)      : $BWTOK"
    echo
    echo "Note: both tools' peakDisk includes the ~$(human $GRLIN_BYTES)GiB plain BWT output;"
    echo "the meaningful delta is grlBWT's recursion temp vs lg's (grammar in RAM)."
} | tee "$SUMMARY"
say "=== bench done ==="
