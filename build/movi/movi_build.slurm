#!/bin/bash
#SBATCH --job-name=movi-build
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
# Resources (partition, --time, --mem, --cpus-per-task, --account) are supplied
# by submit.sh on the sbatch command line; do not hard-code them here.
#
# Movi index builder for Rockfish/Slurm.
#
# Runs the validated TeraLCP -> Movi separator (grlBWT) path end-to-end and
# produces a finished, query-validated Movi index. This mirrors the EC2 build/tera
# stack but targets Slurm instead of CDK. The pipeline is the one proven byte-
# identical to stock pfp/Movi in TeraTools test/validate_against_movi.sh.
#
# Pipeline (separator / grlBWT path -- the default; feeds ALL Movi query modes):
#   movi-prepare-ref <in> clean.fa separators
#   grlbwt-cli  -> grlbwt2rle -> grlbwt2teralcp -> TeraLCP -f rlbwt -othresholds
#   grlbwt2teralcp --movi-sentinel  (heads/len with 0x00 end marker for movi)
#   movi build --separators --preprocessed --skip-prepare --skip-pfp
#
# All configuration arrives via environment variables (see submit.sh):
#   COLLECTION   logical name of the collection (used in output paths)        [required]
#   IN_KIND      fasta | list | agc                                           [required]
#   IN_PATH      path to the FASTA, the list-of-FASTAs file, or the .agc file [required]
#   IN_HAPS      (agc only) comma/space list of sample names, or "ALL"        [agc only]
#   FTABK        ftab k for `movi build`/query (DNA default 16; tiny refs ~5) [default 16]
#   THREADS      worker threads for grlbwt-cli / TeraLCP                       [default $SLURM_CPUS_PER_TASK or 8]
#   WORK_BASE    scratch root for the per-job work dir                        [default /scratch16/blangme2/movi-build]
#   OUT_BASE     durable root for the finished index + logs                   [default /data/blangme2/movi]
#   VALIDATE_FULL  1 => also build a stock-pfp index and diff --count         [default 0]
#   KEEP_WORK    1 => keep the scratch work dir after success                 [default 0]
#
#   MOVI / TERALCP / ADAPTER / GRLBWT_CLI / GRLBWT2RLE / AGC  tool overrides
#   (defaults point at the prebuilt binaries on shared /home; see below)

set -euo pipefail

# --------------------------------------------------------------------------
# Configuration & tool resolution
# --------------------------------------------------------------------------
COLLECTION="${COLLECTION:?COLLECTION is required}"
IN_KIND="${IN_KIND:?IN_KIND is required (fasta|list|agc)}"
IN_PATH="${IN_PATH:?IN_PATH is required}"
IN_HAPS="${IN_HAPS:-ALL}"
FTABK="${FTABK:-16}"
THREADS="${THREADS:-${SLURM_CPUS_PER_TASK:-8}}"
WORK_BASE="${WORK_BASE:-/scratch16/blangme2/movi-build}"
OUT_BASE="${OUT_BASE:-/data/blangme2/movi}"
VALIDATE_FULL="${VALIDATE_FULL:-0}"
KEEP_WORK="${KEEP_WORK:-0}"

MOVI="${MOVI:-$HOME/git/movi-langmead/build/movi}"
PREPARE="${PREPARE:-$(dirname "$MOVI")/bin/movi-prepare-ref}"
TERALCP="${TERALCP:-$HOME/git/TeraTools-pr/src/TeraLCP/TeraLCP}"
ADAPTER="${ADAPTER:-$HOME/git/TeraTools-pr/src/TeraLCP/tools/grlbwt2teralcp}"
GRLBWT_CLI="${GRLBWT_CLI:-$HOME/git/grlBWT/build/grlbwt-cli}"
GRLBWT2RLE="${GRLBWT2RLE:-$HOME/git/grlBWT/build/grlbwt2rle}"
AGC="${AGC:-$HOME/bin/agc}"

export OMP_NUM_THREADS="$THREADS"

DATE="$(date +%Y%m%d)"
JOBID="${SLURM_JOB_ID:-local$$}"
WORK="$WORK_BASE/$COLLECTION/$DATE.$JOBID"
OUTDIR="$OUT_BASE/$COLLECTION/$DATE"
LOGDIR="$OUTDIR/logs"
INDEXDIR="$OUTDIR/index"

mkdir -p "$WORK" "$LOGDIR" "$INDEXDIR"
SUMMARY="$LOGDIR/summary.txt"
TIMELOG="$LOGDIR/step_times.log"
: > "$TIMELOG"

log()  { echo "[$(date +%H:%M:%S)] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

for t in MOVI PREPARE TERALCP ADAPTER GRLBWT_CLI GRLBWT2RLE; do
    p="${!t}"
    [[ -x "$p" ]] || fail "$t not executable: $p"
done

# `step LABEL -- cmd...` : time a labeled pipeline step with /usr/bin/time -v.
GNUTIME="$(command -v time)"; [[ -x /usr/bin/time ]] && GNUTIME=/usr/bin/time
step() {
    local label="$1"; shift
    [[ "$1" == "--" ]] && shift
    log "START $label"
    local t0 t1
    t0=$(date +%s)
    "$GNUTIME" -v -o "$LOGDIR/time.$label.txt" "$@"
    t1=$(date +%s)
    echo "$label $((t1 - t0))s" >> "$TIMELOG"
    log "DONE  $label ($((t1 - t0))s)"
}

# Background disk-usage sampler over the work dir -> peak bytes.
DISKLOG="$LOGDIR/disk_usage_samples.log"
: > "$DISKLOG"
( while true; do du -sb "$WORK" 2>/dev/null | awk -v ts="$(date +%s)" '{print ts, $1}'; sleep 15; done ) >> "$DISKLOG" &
SAMPLER_PID=$!
cleanup() {
    kill "$SAMPLER_PID" 2>/dev/null || true
    if [[ "$KEEP_WORK" != "1" && -n "${WORK:-}" && "$WORK" == "$WORK_BASE"/* ]]; then
        log "Removing work dir $WORK (set KEEP_WORK=1 to keep)"
        rm -rf "$WORK"
    fi
}
trap cleanup EXIT

WALL0=$(date +%s)
cd "$WORK"

# --------------------------------------------------------------------------
# 1. Input acquisition -> single FASTA (input.fa)
# --------------------------------------------------------------------------
log "Acquiring input ($IN_KIND): $IN_PATH"
case "$IN_KIND" in
    fasta)
        [[ -f "$IN_PATH" ]] || fail "FASTA not found: $IN_PATH"
        ln -sf "$(readlink -f "$IN_PATH")" "$WORK/input.fa"
        ;;
    list)
        [[ -f "$IN_PATH" ]] || fail "list not found: $IN_PATH"
        : > "$WORK/input.fa"
        while IFS= read -r f; do
            [[ -z "$f" || "$f" == \#* ]] && continue
            [[ -f "$f" ]] || fail "list member not found: $f"
            cat "$f" >> "$WORK/input.fa"
        done < "$IN_PATH"
        ;;
    agc)
        [[ -x "$AGC" ]] || fail "agc not executable: $AGC"
        [[ -f "$IN_PATH" ]] || fail "agc archive not found: $IN_PATH"
        if [[ "$IN_HAPS" == "ALL" ]]; then
            # whole collection (every sample, incl. reference) -> one FASTA on stdout
            step agc_getcol -- "$AGC" getcol -t "$THREADS" "$IN_PATH" > "$WORK/input.fa"
        else
            # selected samples by name (comma/space separated); one getset call
            read -r -a _haps <<< "${IN_HAPS//,/ }"
            log "AGC samples: ${_haps[*]}"
            step agc_getset -- "$AGC" getset -t "$THREADS" "$IN_PATH" "${_haps[@]}" > "$WORK/input.fa"
        fi
        [[ -s "$WORK/input.fa" ]] || fail "agc produced an empty FASTA -- check sample names with: $AGC listset $IN_PATH"
        ;;
    *) fail "unknown IN_KIND: $IN_KIND" ;;
esac
IN_BP=$(grep -v '^>' "$WORK/input.fa" | tr -d '\n' | wc -c)
log "Input sequence: $IN_BP bp"

# --------------------------------------------------------------------------
# 2. grlBWT separator path -> thresholds + heads/len
# --------------------------------------------------------------------------
step prepare_ref -- "$PREPARE" "$WORK/input.fa" "$WORK/clean.fa" separators
# pfp concatenates the %-separated cleaned records into one string whose trailing
# newline is the smallest byte -> grlBWT uses it as the sentinel (ranks like '$').
{ grep -v '^>' "$WORK/clean.fa" | tr -d '\n'; echo; } > "$WORK/grl_in.txt"

mkdir -p "$WORK/grltmp"   # grlbwt-cli -T requires the tmp dir to already exist
step grlbwt -- "$GRLBWT_CLI" "$WORK/grl_in.txt" -o "$WORK/grl_out" -t "$THREADS" -T "$WORK/grltmp"
step grlbwt2rle -- "$GRLBWT2RLE" "$WORK/grl_out.rl_bwt" "$WORK/grl_rle"
# Faithful widen (heads + 5-byte LE len) for TeraLCP -f rlbwt.
step adapter_teralcp -- "$ADAPTER" "$WORK/grl_rle" "$WORK/grl" -q
step teralcp -- "$TERALCP" -f rlbwt -i "$WORK/grl" -t "$WORK/teralcp.tmp" \
    -othresholds "$WORK/septera" -p "$THREADS" -v quiet

# --------------------------------------------------------------------------
# 3. Assemble preprocessed inputs and run `movi build`
# --------------------------------------------------------------------------
# For the movi build, the end marker must be byte 0 -> --movi-sentinel remaps
# grlBWT's newline terminator to 0x00. Adapter writes index/ref.fa.bwt.{heads,len}.
step adapter_movi -- "$ADAPTER" "$WORK/grl_rle" "$INDEXDIR/ref.fa" --movi-sentinel -q
cp "$WORK/septera.thr_pos" "$INDEXDIR/ref.fa.thr_pos"
[[ -f "$WORK/septera.thr" ]] && cp "$WORK/septera.thr" "$INDEXDIR/ref.fa.thr"
cp "$WORK/clean.fa" "$INDEXDIR/ref.fa"

step movi_build -- "$MOVI" build --separators --preprocessed --skip-prepare --skip-pfp \
    --type regular-thresholds --ftab-k "$FTABK" \
    --fasta "$INDEXDIR/ref.fa" --index "$INDEXDIR"

# --------------------------------------------------------------------------
# 4. Smoke test: derive queries from the reference, run --pml and --count
# --------------------------------------------------------------------------
# `movi build` consumes index/ref.fa into index.movi, so derive queries from the
# cleaned reference still sitting in the work dir.
python3 - "$WORK/clean.fa" "$WORK" <<'PY'
import sys, random
ref, W = sys.argv[1], sys.argv[2]
seqs, cur = [], []
for line in open(ref):
    if line.startswith('>'):
        if cur: seqs.append(''.join(cur)); cur=[]
    else: cur.append(line.strip())
if cur: seqs.append(''.join(cur))
seqs = [s.replace('%','') for s in seqs]
seqs = [s for s in seqs if len(s) >= 120] or [s for s in seqs if s]
random.seed(1)
with open(f"{W}/reads.fa", "w") as f:
    for i in range(20):
        s = random.choice(seqs); L = min(100, len(s)); p = random.randint(0, len(s)-L)
        f.write(f">r{i}\n{s[p:p+L]}\n")
with open(f"{W}/kmers.fa", "w") as f:
    for i in range(20):
        s = random.choice(seqs); k = 31
        if len(s) < k: continue
        p = random.randint(0, len(s)-k)
        f.write(f">k{i}\n{s[p:p+k]}\n")
PY

SMOKE_OK=1
"$MOVI" query --pml -i "$INDEXDIR" -r "$WORK/reads.fa" -o "$WORK/smoke" \
    > "$LOGDIR/smoke_pml.log" 2>&1 || SMOKE_OK=0
[[ -s "$WORK/smoke.pml.bpf" ]] || SMOKE_OK=0
"$MOVI" query --count -i "$INDEXDIR" -r "$WORK/kmers.fa" --stdout \
    > "$LOGDIR/smoke_count.txt" 2>"$LOGDIR/smoke_count.err" || SMOKE_OK=0
SMOKE_COUNT_LINES=$(wc -l < "$LOGDIR/smoke_count.txt" 2>/dev/null || echo 0)
log "Smoke test: pml bpf $( [[ -s "$WORK/smoke.pml.bpf" ]] && echo present || echo MISSING ), count lines=$SMOKE_COUNT_LINES"

# --------------------------------------------------------------------------
# 5. Optional full validation: build stock-pfp index and diff --count
# --------------------------------------------------------------------------
VALIDATE_RESULT="skipped"
if [[ "$VALIDATE_FULL" == "1" ]]; then
    log "VALIDATE_FULL: building stock-pfp separator index for diff"
    mkdir -p "$WORK/nptm"
    if "$MOVI" build --separators --fasta "$WORK/input.fa" --index "$WORK/nptm" \
        --type regular-thresholds --ftab-k "$FTABK" > "$LOGDIR/nptm_build.log" 2>&1; then
        "$MOVI" query --count -i "$WORK/nptm"  -r "$WORK/kmers.fa" --stdout 2>/dev/null | sort > "$WORK/c.nptm"
        "$MOVI" query --count -i "$INDEXDIR"   -r "$WORK/kmers.fa" --stdout 2>/dev/null | sort > "$WORK/c.tera"
        if cmp -s "$WORK/c.nptm" "$WORK/c.tera"; then VALIDATE_RESULT="PASS (count identical to stock pfp)"
        else VALIDATE_RESULT="FAIL (count differs from stock pfp)"; SMOKE_OK=0; fi
    else
        VALIDATE_RESULT="ERROR (stock pfp build failed; see nptm_build.log)"
    fi
    log "VALIDATE_FULL: $VALIDATE_RESULT"
fi

# Prune build intermediates that `movi build` folded into index.movi and no longer
# needs at query time (verified: the index loads without them). Keeps the published
# dir to {index.movi, ftab.*.bin, movi.*.nulldb}.
rm -f "$INDEXDIR/ref.fa.bwt.heads" "$INDEXDIR/ref.fa.bwt.len" "$INDEXDIR/null_reads.fasta"

# --------------------------------------------------------------------------
# 6. Summary  (reporting only -- must never fail a validated build)
# --------------------------------------------------------------------------
set +e
WALL1=$(date +%s)
WALL=$((WALL1 - WALL0))
PEAK_DISK=$(awk 'BEGIN{m=0}{if($2>m)m=$2}END{print m+0}' "$DISKLOG")
peak_rss_kb() { awk -F': ' '/Maximum resident set size/{print $2}' "$LOGDIR/time.$1.txt" 2>/dev/null; }
INDEX_BYTES=$(du -sb "$INDEXDIR" 2>/dev/null | awk '{print $1}')

{
    echo "Movi index build summary"
    echo "========================"
    echo "Collection      : $COLLECTION"
    echo "Date            : $DATE"
    echo "Slurm job       : ${SLURM_JOB_ID:-n/a} on ${SLURMD_NODENAME:-$(hostname)}"
    echo "Partition       : ${SLURM_JOB_PARTITION:-n/a}"
    echo "Path            : grlBWT separator path (all Movi query modes)"
    echo "Input kind      : $IN_KIND ($IN_PATH)"
    echo "Input bp        : $IN_BP"
    echo "ftab-k          : $FTABK"
    echo "Threads         : $THREADS"
    echo
    echo "Wall clock      : ${WALL}s"
    echo "Peak work disk  : $PEAK_DISK bytes ($(awk "BEGIN{printf \"%.2f\", $PEAK_DISK/1073741824}") GiB)"
    echo "Index size      : $INDEX_BYTES bytes ($(awk "BEGIN{printf \"%.2f\", ${INDEX_BYTES:-0}/1073741824}") GiB)"
    echo
    echo "Per-step wall times:"
    sed 's/^/  /' "$TIMELOG"
    echo
    echo "Peak RSS per step (KB):"
    for s in prepare_ref grlbwt grlbwt2rle adapter_teralcp teralcp adapter_movi movi_build; do
        printf "  %-16s %s\n" "$s" "$(peak_rss_kb "$s")"
    done
    echo
    echo "Smoke test      : $( [[ $SMOKE_OK == 1 ]] && echo PASS || echo FAIL )"
    echo "  pml.bpf bytes : $(stat -c %s "$WORK/smoke.pml.bpf" 2>/dev/null || echo missing)"
    echo "  count lines   : $SMOKE_COUNT_LINES"
    echo "Full validation : $VALIDATE_RESULT"
    echo
    echo "Index dir       : $INDEXDIR"
    echo "Logs dir        : $LOGDIR"
} > "$SUMMARY"

# tool versions
{
    echo "== movi =="; "$MOVI" --help 2>&1 | head -1
    echo "== TeraLCP =="; "$TERALCP" -h 2>&1 | head -1
    echo "== grlbwt-cli =="; "$GRLBWT_CLI" -v 2>&1 | head -1
    echo "== agc =="; "$AGC" 2>&1 | head -1
    echo "== git refs =="
    git -C "$(dirname "$TERALCP")/../.." rev-parse --short HEAD 2>/dev/null | sed 's/^/TeraTools /'
    git -C "$(dirname "$MOVI")/.." rev-parse --short HEAD 2>/dev/null | sed 's/^/Movi /'
} > "$LOGDIR/tool_versions.txt" 2>&1

cat "$SUMMARY"

if [[ $SMOKE_OK != 1 ]]; then
    echo "ERROR: smoke test / validation failed -- see $LOGDIR" >&2
    exit 1
fi
log "SUCCESS. Index at $INDEXDIR"
exit 0
