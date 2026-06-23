#!/bin/bash
# Launch the Movi-index build on Rockfish via Snakemake + the SLURM executor.
# Run from a login node (it only submits/monitors; the work happens in Slurm jobs).
#
#   ./run.sh             # real run (submits Slurm jobs, blocks while monitoring)
#   ./run.sh -n          # dry run: print the plan / DAG without submitting
#   ./run.sh <target>    # build a specific target file
#
# Keep this process alive for the duration (it's the Snakemake scheduler). Use
# tmux/screen, or nohup:  nohup ./run.sh > run.log 2>&1 &
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

source ~/miniforge3/etc/profile.d/conda.sh
conda activate snakemake8     # env with snakemake>=8 + snakemake-executor-plugin-slurm

snakemake \
    --workflow-profile profiles/rockfish \
    --configfile config.yaml \
    "$@"
