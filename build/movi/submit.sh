#!/bin/bash
# submit.sh -- submit a Movi index build to Slurm on Rockfish.
#
# Run this ON a Rockfish login node (it calls sbatch). It validates arguments,
# picks a resource profile, and submits movi_build.slurm with the configuration
# passed through as exported environment variables.
#
# Usage:
#   ./submit.sh --collection NAME --fasta  /path/to/ref.fa        [options]
#   ./submit.sh --collection NAME --list   /path/to/fastas.txt    [options]
#   ./submit.sh --collection NAME --agc    /path/to/arch.agc [--haplotypes "s1,s2"] [options]
#
# Resource options:
#   --profile {express|pilot|parallel|bigmem}   default: pilot
#   --time HH:MM:SS        override walltime
#   --mem MEM             override memory (e.g. 64G)
#   --cpus N             override cpus-per-task
#   --partition NAME     override partition
#   --account ACCT       slurm account (default: blangme2; bigmem profile uses blangme2_bigmem)
#
# Build options (passed to the job):
#   --ftab-k K           ftab k (default 16; use ~5 for tiny test refs)
#   --validate-full      also build a stock-pfp index and diff --count (pilot use)
#   --keep-work          keep the scratch work dir after success
#   --work-base DIR      scratch root (default /scratch16/blangme2/movi-build)
#   --out-base DIR       durable output root (default /data/blangme2/movi)
#   --dry-run            print the sbatch command and exit

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JOB="$HERE/movi_build.slurm"
[[ -f "$JOB" ]] || { echo "missing $JOB" >&2; exit 1; }

COLLECTION="" IN_KIND="" IN_PATH="" IN_HAPS="ALL"
PROFILE="pilot" TIME="" MEM="" CPUS="" PARTITION="" ACCOUNT=""
FTABK="16" VALIDATE_FULL="0" KEEP_WORK="0" DRYRUN="0"
WORK_BASE="/scratch16/blangme2/movi-build" OUT_BASE="/data/blangme2/movi"

die() { echo "ERROR: $*" >&2; exit 1; }
need() { [[ -n "${2:-}" ]] || die "$1 needs a value"; }

while [[ $# -gt 0 ]]; do
    case "$1" in
        --collection) need "$1" "${2:-}"; COLLECTION="$2"; shift 2;;
        --fasta)      need "$1" "${2:-}"; IN_KIND="fasta"; IN_PATH="$2"; shift 2;;
        --list)       need "$1" "${2:-}"; IN_KIND="list";  IN_PATH="$2"; shift 2;;
        --agc)        need "$1" "${2:-}"; IN_KIND="agc";   IN_PATH="$2"; shift 2;;
        --haplotypes) need "$1" "${2:-}"; IN_HAPS="$2"; shift 2;;
        --profile)    need "$1" "${2:-}"; PROFILE="$2"; shift 2;;
        --time)       need "$1" "${2:-}"; TIME="$2"; shift 2;;
        --mem)        need "$1" "${2:-}"; MEM="$2"; shift 2;;
        --cpus)       need "$1" "${2:-}"; CPUS="$2"; shift 2;;
        --partition)  need "$1" "${2:-}"; PARTITION="$2"; shift 2;;
        --account)    need "$1" "${2:-}"; ACCOUNT="$2"; shift 2;;
        --ftab-k)     need "$1" "${2:-}"; FTABK="$2"; shift 2;;
        --validate-full) VALIDATE_FULL="1"; shift;;
        --keep-work)  KEEP_WORK="1"; shift;;
        --work-base)  need "$1" "${2:-}"; WORK_BASE="$2"; shift 2;;
        --out-base)   need "$1" "${2:-}"; OUT_BASE="$2"; shift 2;;
        --dry-run)    DRYRUN="1"; shift;;
        -h|--help)    sed -n '2,40p' "$0"; exit 0;;
        *) die "unknown arg: $1";;
    esac
done

[[ -n "$COLLECTION" ]] || die "--collection is required"
[[ -n "$IN_KIND"    ]] || die "one of --fasta / --list / --agc is required"
[[ -e "$IN_PATH"    ]] || die "input not found: $IN_PATH"
IN_PATH="$(readlink -f "$IN_PATH")"

# Resource profiles. parallel = 4 GB/CPU; bigmem = 32 GB/CPU; express = 8h cap.
case "$PROFILE" in
    express)  : "${PARTITION:=express}";  : "${TIME:=02:00:00}"; : "${CPUS:=4}";  : "${MEM:=16G}";  : "${ACCOUNT:=blangme2}";;  # express QOS caps cpu=4/job
    pilot)    : "${PARTITION:=shared}";   : "${TIME:=04:00:00}"; : "${CPUS:=8}";  : "${MEM:=32G}";  : "${ACCOUNT:=blangme2}";;
    parallel) : "${PARTITION:=parallel}"; : "${TIME:=12:00:00}"; : "${CPUS:=24}"; : "${MEM:=0}";    : "${ACCOUNT:=blangme2}";;
    bigmem)   : "${PARTITION:=bigmem}";   : "${TIME:=1-00:00:00}"; : "${CPUS:=24}"; : "${MEM:=720G}"; : "${ACCOUNT:=blangme2_bigmem}";;
    *) die "unknown --profile: $PROFILE (express|pilot|parallel|bigmem)";;
esac

EXPORTS="COLLECTION=$COLLECTION,IN_KIND=$IN_KIND,IN_PATH=$IN_PATH,IN_HAPS=$IN_HAPS"
EXPORTS+=",FTABK=$FTABK,THREADS=$CPUS,WORK_BASE=$WORK_BASE,OUT_BASE=$OUT_BASE"
EXPORTS+=",VALIDATE_FULL=$VALIDATE_FULL,KEEP_WORK=$KEEP_WORK"

SBATCH=( sbatch
    --job-name "movi-$COLLECTION"
    --partition "$PARTITION"
    --account "$ACCOUNT"
    --time "$TIME"
    --cpus-per-task "$CPUS"
    --chdir "$WORK_BASE"
)
[[ "$MEM" != "0" ]] && SBATCH+=( --mem "$MEM" )
SBATCH+=( --export="ALL,$EXPORTS" "$JOB" )

echo "Collection : $COLLECTION"
echo "Input      : $IN_KIND $IN_PATH ${IN_HAPS:+(haps: $IN_HAPS)}"
echo "Profile    : $PROFILE  ->  partition=$PARTITION time=$TIME cpus=$CPUS mem=${MEM} account=$ACCOUNT"
echo "ftab-k     : $FTABK   validate-full=$VALIDATE_FULL"
echo "Output     : $OUT_BASE/$COLLECTION/<YYYYMMDD>/"
echo
echo "+ ${SBATCH[*]}"
if [[ "$DRYRUN" == "1" ]]; then echo "(dry run)"; exit 0; fi
mkdir -p "$WORK_BASE"
"${SBATCH[@]}"
