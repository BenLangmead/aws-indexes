#!/bin/bash
# membench_devlangmead.sh -- memory probe for the RAM-risky stages of the Movi
# build pipeline (RLBWT construction via grlBWT, and TeraLCP thresholds), run on
# devlangmead1 with a hard ~1 TB memory ceiling so a runaway can't take down the
# shared node. All scratch lives on /tmp (fast local NVMe, ~1.7 TB free).
#
# Enforcement (privilege-free; systemd --user cgroup memory caps are NOT delegated
# on this node, so we do not rely on them):
#   * ulimit -v  (RLIMIT_AS)  -> hard ceiling on virtual address space. RSS <= AS,
#     so this alone guarantees physical RAM can never exceed the cap.
#   * RSS watchdog            -> polls the step's process-group *physical* RSS every
#     POLL s, records the peak, and TERM/KILLs the step if RSS crosses KILL_GIB.
#     This is the real cap (physical), and avoids killing a tool that merely
#     over-reserves virtual space.
#
# Steps measured:  agc getcol -> movi-prepare-ref -> grlbwt-cli -> grlbwt2rle ->
#                  grlbwt2teralcp -> TeraLCP -f rlbwt -othresholds
# (Stops at thresholds; `movi build` memory is a separate question.)
#
# Usage: nohup bash membench_devlangmead.sh >LOG 2>&1 &   (it is long-running)

set -uo pipefail

# ---- configuration -------------------------------------------------------
ARCHIVE="${ARCHIVE:-/data/blangme2/fasta/hprc-yr1/HPRC-yr1.agc}"
IN_HAPS="${IN_HAPS:-}"     # comma/space list of agc sample names; empty => whole collection (getcol)
TAG="${TAG:-hprc-yr1}"
THREADS="${THREADS:-24}"
WORK="${WORK:-/tmp/movi-membench/$TAG}"
POLL="${POLL:-2}"

# Cap: stay safely under 1 TB (decimal) on a 1.5 TB node.
AS_LIMIT_KB="${AS_LIMIT_KB:-1258291200}"   # ulimit -v ceiling: 1200 GiB (loose backstop)
KILL_GIB="${KILL_GIB:-950}"                # watchdog physical-RSS kill threshold (~1.02 TB)
KILL_KB=$(( KILL_GIB * 1024 * 1024 ))

MOVI="${MOVI:-$HOME/git/movi-langmead/build/movi}"
PREPARE="${PREPARE:-$(dirname "$MOVI")/bin/movi-prepare-ref}"
TERALCP="${TERALCP:-$HOME/git/TeraTools-pr/src/TeraLCP/TeraLCP}"
ADAPTER="${ADAPTER:-$HOME/git/TeraTools-pr/src/TeraLCP/tools/grlbwt2teralcp}"
GRLBWT_CLI="${GRLBWT_CLI:-$HOME/git/grlBWT/build/grlbwt-cli}"
GRLBWT2RLE="${GRLBWT2RLE:-$HOME/git/grlBWT/build/grlbwt2rle}"
AGC="${AGC:-$HOME/bin/agc}"

export OMP_NUM_THREADS="$THREADS"

LOG="$WORK/logs"
mkdir -p "$WORK" "$LOG"
STATUS="$LOG/STATUS.txt"
SUMMARY="$LOG/SUMMARY.txt"
GNUTIME=/usr/bin/time

# The AS backstop applies to this shell and all children.
ulimit -v "$AS_LIMIT_KB" 2>/dev/null || echo "WARN: could not set ulimit -v" | tee -a "$STATUS"

# Save the script's real stdout on fd 3 so status/heartbeat messages never leak
# into a step's stdout when the caller redirects run_capped (e.g. getcol > input.fa).
exec 3>&1
ts()  { date '+%Y-%m-%d %H:%M:%S'; }
say() { echo "[$(ts)] $*" | tee -a "$STATUS" >&3; }

free_gib()    { free -g | awk '/^Mem:/{print $7}'; }       # "available"
tmp_used_g()  { df -BG /tmp | awk 'NR==2{gsub("G","",$3); print $3}'; }
gib() { awk "BEGIN{printf \"%.1f\", $1/1048576}"; }          # KB -> GiB

# run_capped LABEL -- cmd args...
# Runs the command in its own process group under the RSS watchdog. Records peak
# RSS (KB) to $LOG/peak.LABEL and wall seconds to $LOG/wall.LABEL. Returns the
# command's exit code (137-ish / nonzero if the watchdog killed it).
run_capped() {
    local label="$1"; shift
    # By default a step's stdout is captured as a per-step PROGRESS log ($label.out)
    # -- this is where grlBWT's per-round timings and TeraLCP's -v time tree land.
    # For data-producing steps (getcol/getset) pass `--out FILE` to send stdout there.
    local outfile="$LOG/$label.out"
    if [[ "${1:-}" == "--out" ]]; then outfile="$2"; shift 2; fi
    [[ "${1:-}" == "--" ]] && shift
    say "STEP $label START : ${*:0:6} ... (avail $(free_gib)GiB, /tmp used $(tmp_used_g)G)"
    local t0; t0=$(date +%s)
    # tool stdout -> $outfile, tool stderr -> $label.err, time's report -> its -o file
    setsid "$GNUTIME" -v -o "$LOG/time.$label.txt" "$@" \
        >"$outfile" 2>"$LOG/$label.err" &
    local pid=$!            # session+group leader: pgid == pid
    local peak=0 killed=0 rss
    while kill -0 "$pid" 2>/dev/null; do
        rss=$(ps -o rss= -g "$pid" 2>/dev/null | awk '{s+=$1} END{print s+0}')
        (( rss > peak )) && peak=$rss
        if (( rss > KILL_KB )); then
            say "WATCHDOG KILL $label : RSS $(gib $rss)GiB > ${KILL_GIB}GiB"
            kill -TERM -"$pid" 2>/dev/null; sleep 5; kill -KILL -"$pid" 2>/dev/null
            killed=1; break
        fi
        # heartbeat every ~30s
        if (( $(date +%s) % 30 < POLL )); then
            say "  .. $label running: RSS $(gib $rss)GiB (peak $(gib $peak)GiB), /tmp used $(tmp_used_g)G"
        fi
        sleep "$POLL"
    done
    wait "$pid"; local rc=$?
    local t1; t1=$(date +%s)
    echo "$peak"        > "$LOG/peak.$label"
    echo "$((t1-t0))"   > "$LOG/wall.$label"
    (( killed )) && rc=137
    say "STEP $label DONE rc=$rc : peakRSS $(gib $peak)GiB, wall $((t1-t0))s"
    return $rc
}

# Authoritative peak RSS from /usr/bin/time -v (KB), falls back to watchdog peak.
time_peak_kb() { awk -F': ' '/Maximum resident set size/{print $2}' "$LOG/time.$1.txt" 2>/dev/null; }

say "=== membench start: $TAG ==="
say "archive=$ARCHIVE threads=$THREADS work=$WORK"
say "caps: ulimit -v=${AS_LIMIT_KB}KB (~$(gib $AS_LIMIT_KB)GiB), watchdog kill=${KILL_GIB}GiB, poll=${POLL}s"
say "node: avail $(free_gib)GiB, /tmp free $(df -BG /tmp | awk 'NR==2{print $4}')"

cd "$WORK"

# Resume-aware staging: reuse the furthest-along artifact already on disk so an
# interrupted run doesn't redo the slow getcol/prepare passes. Stages 1-3 are NOT
# the memory-risky ones (prepare_ref peaks well under 1 GiB).
if [[ -s grl_in.txt ]]; then
    say "resume: grl_in.txt present ($(du -h grl_in.txt|cut -f1)); skipping getcol/prepare/concat"
    rm -f input.fa clean.fa
elif [[ -s clean.fa ]]; then
    say "resume: clean.fa present ($(du -h clean.fa|cut -f1)); skipping getcol/prepare"
    rm -f input.fa
    say "building grl_in.txt from clean.fa"
    { grep -v '^>' clean.fa | tr -d '\n'; echo; } > grl_in.txt
    say "grl_in.txt: $(du -h grl_in.txt|cut -f1) ; /tmp used $(tmp_used_g)G"
    rm -f clean.fa
else
    # 1. Extract -> input.fa (reuse a pre-staged input.fa if present; IN_HAPS selects
    #    a subset via getset, else the whole collection via getcol)
    if [[ -s input.fa ]]; then
        say "reusing existing input.fa ($(du -h input.fa | cut -f1))"
    elif [[ -n "$IN_HAPS" ]]; then
        read -r -a _haps <<< "${IN_HAPS//,/ }"
        say "extracting ${#_haps[@]} samples via getset"
        run_capped getset --out input.fa -- "$AGC" getset -t "$THREADS" "$ARCHIVE" "${_haps[@]}"
    else
        run_capped getcol --out input.fa -- "$AGC" getcol -t "$THREADS" "$ARCHIVE"
    fi
    _nrec=$(grep -c '^>' input.fa)        # count once (input.fa can be 100s of GB)
    say "input.fa: $(du -h input.fa | cut -f1), ${_nrec} records"
    [[ ${_nrec} -gt 0 ]] || { say "input.fa has no records; aborting"; exit 1; }

    # 2. Clean + %-separate + add reverse complement
    run_capped prepare_ref -- "$PREPARE" "$WORK/input.fa" "$WORK/clean.fa" separators \
        || { say "prepare_ref failed; aborting"; exit 1; }
    rm -f input.fa; say "removed input.fa (freed space); /tmp used $(tmp_used_g)G"

    # 3. One concatenated string (trailing newline = grlBWT sentinel)
    say "building grl_in.txt from clean.fa"
    { grep -v '^>' clean.fa | tr -d '\n'; echo; } > grl_in.txt
    say "grl_in.txt: $(du -h grl_in.txt | cut -f1)"
    rm -f clean.fa; say "removed clean.fa; /tmp used $(tmp_used_g)G"
fi

# 4. RLBWT construction (memory step of interest #1)
mkdir -p grltmp
run_capped grlbwt -- "$GRLBWT_CLI" grl_in.txt -o grl_out -t "$THREADS" -T "$WORK/grltmp"
GRL_RC=$?
rm -rf grltmp
[[ $GRL_RC -eq 0 ]] || { say "grlbwt rc=$GRL_RC (killed=$([[ $GRL_RC == 137 ]] && echo yes))"; }
rm -f grl_in.txt; say "removed grl_in.txt; /tmp used $(tmp_used_g)G"

if [[ $GRL_RC -eq 0 ]]; then
    run_capped grlbwt2rle -- "$GRLBWT2RLE" grl_out.rl_bwt grl_rle
    run_capped adapter -- "$ADAPTER" grl_rle grl -q
    # 5. TeraLCP thresholds (memory step of interest #2)
    run_capped teralcp -- "$TERALCP" -f rlbwt -i grl -t "$WORK/teralcp.tmp" \
        -othresholds septera -p "$THREADS" -v time
    TERA_RC=$?
else
    say "skipping grlbwt2rle/adapter/teralcp because grlbwt did not finish"
    TERA_RC=255
fi

# ---- summary -------------------------------------------------------------
{
    echo "Movi membench summary -- $TAG"
    echo "==============================="
    echo "Host        : $(hostname)"
    echo "Archive     : $ARCHIVE  (95 haplotypes)"
    echo "Threads     : $THREADS"
    echo "Caps        : ulimit -v ~$(gib $AS_LIMIT_KB)GiB ; watchdog kill ${KILL_GIB}GiB"
    echo
    printf "%-12s %8s %12s %12s\n" "step" "rc" "peakRSS_GiB" "wall_s"
    for s in getcol prepare_ref grlbwt grlbwt2rle adapter teralcp; do
        [[ -f "$LOG/peak.$s" ]] || continue
        tk=$(time_peak_kb "$s"); wp=$(cat "$LOG/peak.$s" 2>/dev/null)
        kb=${tk:-$wp}; [[ -z "$kb" ]] && kb=0
        printf "%-12s %8s %12s %12s\n" "$s" \
            "$(awk -F': ' '/Exit status/{print $2}' "$LOG/time.$s.txt" 2>/dev/null || echo '?')" \
            "$(gib ${kb})" "$(cat "$LOG/wall.$s" 2>/dev/null)"
    done
    echo
    echo "KEY RESULT (the two RAM-risky stages):"
    for s in grlbwt teralcp; do
        tk=$(time_peak_kb "$s"); wp=$(cat "$LOG/peak.$s" 2>/dev/null); kb=${tk:-$wp}
        echo "  $s : peak RSS $(gib ${kb:-0}) GiB  $( [[ -f $LOG/wall.$s ]] && echo "(wall $(cat $LOG/wall.$s)s)" )"
    done
    echo
    echo "Under 1 TB? grlbwt=$([[ $GRL_RC -eq 0 ]] && echo yes || echo 'NO/killed') teralcp=$([[ ${TERA_RC:-255} -eq 0 ]] && echo yes || echo 'NO/killed-or-skipped')"
} | tee "$SUMMARY"

say "=== membench done ==="
