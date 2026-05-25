#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

targets_file="${TARGETS_FILE:-${script_dir}/targets.tsv}"
out_dir="${OUT_DIR:-${script_dir}/out}"
work_dir="${WORK_DIR:-${script_dir}/work}"
bowtie2_build="${BOWTIE2_BUILD:-bowtie2-build}"
samtools_bin="${SAMTOOLS:-samtools}"
curl_bin="${CURL:-curl}"
threads="${THREADS:-}"
force=0
keep_fasta=0
upload_prefix="${UPLOAD_PREFIX:-}"
target_ids=()

usage() {
    cat <<'USAGE'
Build selected Bowtie 2 indexes from build/bowtie/targets.tsv.

Usage:
  build_indexes.bash [options] [target-id ...]

Options:
  --list                  Show available targets and exit.
  --targets FILE          TSV target catalog. Default: build/bowtie/targets.tsv
  --out-dir DIR           Directory for .bt2/.bt2l files, dict, zip, md5, provenance.
  --work-dir DIR          Directory for downloaded FASTA and temporary build files.
  --threads N             Threads passed to bowtie2-build.
  --upload-prefix S3_URI  Also upload output artifacts to this S3 prefix.
  --force                 Redownload/rebuild even when outputs exist.
  --keep-fasta            Keep decompressed FASTA files in the work directory.
  -h, --help              Show this help.

If no target IDs are given, all targets in the TSV are built.
USAGE
}

default_threads() {
    if command -v nproc >/dev/null 2>&1; then
        nproc
    elif getconf _NPROCESSORS_ONLN >/dev/null 2>&1; then
        getconf _NPROCESSORS_ONLN
    elif command -v sysctl >/dev/null 2>&1; then
        sysctl -n hw.ncpu
    else
        printf '1\n'
    fi
}

require_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        printf 'error: required command not found: %s\n' "$1" >&2
        exit 1
    fi
}

target_selected() {
    local id="$1"
    local selected

    if [[ "${#target_ids[@]}" -eq 0 ]]; then
        return 0
    fi

    for selected in "${target_ids[@]}"; do
        if [[ "$selected" == "$id" ]]; then
            return 0
        fi
    done

    return 1
}

list_targets() {
    local id index_base species assembly source url expected_ext notes

    printf '%-12s %-32s %-18s %s\n' "ID" "INDEX_BASE" "EXPECTED_EXT" "ASSEMBLY"
    while IFS=$'\t' read -r id index_base species assembly source url expected_ext notes; do
        [[ -z "${id:-}" || "${id:0:1}" == "#" ]] && continue
        printf '%-12s %-32s %-18s %s / %s\n' "$id" "$index_base" "$expected_ext" "$species" "$assembly"
    done < "$targets_file"
}

md5_file() {
    if command -v md5sum >/dev/null 2>&1; then
        md5sum "$@"
    elif command -v md5 >/dev/null 2>&1; then
        md5 -r "$@"
    else
        printf 'error: neither md5sum nor md5 found\n' >&2
        exit 1
    fi
}

md5_value() {
    if command -v md5sum >/dev/null 2>&1; then
        md5sum "$1" | awk '{print $1}'
    elif command -v md5 >/dev/null 2>&1; then
        md5 -q "$1"
    else
        printf 'error: neither md5sum nor md5 found\n' >&2
        exit 1
    fi
}

default_builder_id() {
    local commit suffix status

    if [[ -n "${INDEX_ZONE_BUILDER:-}" ]]; then
        printf '%s\n' "$INDEX_ZONE_BUILDER"
    elif git -C "$script_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        commit="$(git -C "$script_dir" rev-parse --short=12 HEAD)"
        status="$(git -C "$script_dir" status --porcelain -- "$script_dir" || true)"
        suffix=""
        [[ -n "$status" ]] && suffix="+dirty"
        printf 'aws-indexes:%s%s\n' "$commit" "$suffix"
    else
        printf 'aws-indexes:unknown\n'
    fi
}

index_ext_for_prefix() {
    local prefix="$1"

    if [[ -e "${prefix}.1.bt2l" ]]; then
        printf 'bt2l\n'
    elif [[ -e "${prefix}.1.bt2" ]]; then
        printf 'bt2\n'
    else
        printf 'error: no Bowtie 2 index files found for %s\n' "$prefix" >&2
        exit 1
    fi
}

validate_index_files() {
    local prefix="$1"
    local ext="$2"
    local suffix

    for suffix in .1 .2 .3 .4 .rev.1 .rev.2; do
        if [[ ! -s "${prefix}${suffix}.${ext}" ]]; then
            printf 'error: expected index file missing or empty: %s\n' "${prefix}${suffix}.${ext}" >&2
            exit 1
        fi
    done
}

copy_index_artifacts() {
    local prefix="$1"
    local index_base="$2"
    local ext="$3"
    local suffix

    mkdir -p "$out_dir"

    for suffix in .1 .2 .3 .4 .rev.1 .rev.2; do
        cp "${prefix}${suffix}.${ext}" "${out_dir}/${index_base}${suffix}.${ext}"
    done

    rm -f "${out_dir}/${index_base}.zip"
    zip -jq "${out_dir}/${index_base}.zip" \
        "${prefix}".*.${ext} \
        "${out_dir}/${index_base}.dict" \
        "${out_dir}/${index_base}.manifest.json"
    md5_file \
        "${out_dir}/${index_base}.zip" \
        "${out_dir}/${index_base}".*.${ext} \
        "${out_dir}/${index_base}.dict" \
        "${out_dir}/${index_base}.manifest.json" \
        "${out_dir}/${index_base}.build.txt" \
        > "${out_dir}/${index_base}.md5"
}

write_sequence_dictionary() {
    local fasta="$1"
    local index_base="$2"

    mkdir -p "$out_dir"
    "$samtools_bin" dict "$fasta" > "${out_dir}/${index_base}.dict"
}

write_manifest() {
    local id="$1"
    local index_base="$2"
    local species="$3"
    local assembly="$4"
    local source="$5"
    local url="$6"
    local expected_ext="$7"
    local actual_ext="$8"
    local notes="$9"
    local download="${10}"
    local fasta="${11}"
    local prefix="${12}"
    local version_line tool_version input_md5 build_command builder_id

    version_line="$("$bowtie2_build" --version | head -n 1 || true)"
    tool_version="$(printf '%s\n' "$version_line" | sed -E 's/.*version ([^[:space:]]+).*/\1/')"
    input_md5="$(md5_value "$download")"
    build_command="$(printf '%q ' "$bowtie2_build" --threads "$threads" "$fasta" "$prefix")"
    build_command="${build_command% }"
    builder_id="$(default_builder_id)"

    INDEX_MANIFEST_PATH="${out_dir}/${index_base}.manifest.json" \
    INDEX_ID="$id" \
    INDEX_BASE="$index_base" \
    INDEX_SPECIES="$species" \
    INDEX_ASSEMBLY="$assembly" \
    INDEX_SOURCE="$source" \
    INDEX_SOURCE_URL="$url" \
    INDEX_EXPECTED_EXT="$expected_ext" \
    INDEX_ACTUAL_EXT="$actual_ext" \
    INDEX_NOTES="$notes" \
    INDEX_DOWNLOAD="$download" \
    INDEX_INPUT_MD5="$input_md5" \
    INDEX_TOOL_VERSION="$tool_version" \
    INDEX_TOOL_VERSION_LINE="$version_line" \
    INDEX_COMMAND="$build_command" \
    INDEX_THREADS="$threads" \
    INDEX_BUILDER="$builder_id" \
    python3 - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

index_base = os.environ["INDEX_BASE"]
ext = os.environ["INDEX_ACTUAL_EXT"]
now = datetime.now(timezone.utc)

outputs = [
    f"{index_base}.1.{ext}",
    f"{index_base}.2.{ext}",
    f"{index_base}.3.{ext}",
    f"{index_base}.4.{ext}",
    f"{index_base}.rev.1.{ext}",
    f"{index_base}.rev.2.{ext}",
    f"{index_base}.dict",
    f"{index_base}.zip",
    f"{index_base}.md5",
    f"{index_base}.build.txt",
    f"{index_base}.manifest.json",
]
source_url = os.environ["INDEX_SOURCE_URL"]
manifest = {
    "schema_version": "1.0",
    "id": os.environ["INDEX_ID"],
    "index_base": index_base,
    "species": os.environ["INDEX_SPECIES"],
    "assembly": os.environ["INDEX_ASSEMBLY"],
    "source": os.environ["INDEX_SOURCE"],
    "source_urls": [source_url],
    "expected_extension": os.environ["INDEX_EXPECTED_EXT"],
    "actual_extension": ext,
    "tool": "bowtie2-build",
    "tool_version": os.environ["INDEX_TOOL_VERSION"],
    "tool_version_output": os.environ["INDEX_TOOL_VERSION_LINE"],
    "command": os.environ["INDEX_COMMAND"],
    "threads": os.environ["INDEX_THREADS"],
    "inputs": [
        {
            "path": Path(os.environ["INDEX_DOWNLOAD"]).name,
            "md5": os.environ["INDEX_INPUT_MD5"],
        }
    ],
    "outputs": outputs,
    "date": now.date().isoformat(),
    "built_utc": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "builder": os.environ["INDEX_BUILDER"],
    "notes": os.environ["INDEX_NOTES"],
}

with open(os.environ["INDEX_MANIFEST_PATH"], "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, indent=2, sort_keys=True)
    fh.write("\n")
PY
}

write_provenance() {
    local id="$1"
    local index_base="$2"
    local species="$3"
    local assembly="$4"
    local source="$5"
    local url="$6"
    local expected_ext="$7"
    local actual_ext="$8"
    local notes="$9"
    local version

    version="$("$bowtie2_build" --version | head -n 1 || true)"

    {
        printf 'id=%s\n' "$id"
        printf 'index_base=%s\n' "$index_base"
        printf 'species=%s\n' "$species"
        printf 'assembly=%s\n' "$assembly"
        printf 'source=%s\n' "$source"
        printf 'url=%s\n' "$url"
        printf 'expected_ext=%s\n' "$expected_ext"
        printf 'actual_ext=%s\n' "$actual_ext"
        printf 'built_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        printf 'bowtie2_build=%s\n' "$version"
        printf 'threads=%s\n' "$threads"
        printf 'notes=%s\n' "$notes"
    } > "${out_dir}/${index_base}.build.txt"
}

upload_outputs() {
    local index_base="$1"
    local ext="$2"
    local artifact

    [[ -z "$upload_prefix" ]] && return 0
    require_cmd aws

    for artifact in "${out_dir}/${index_base}.zip" "${out_dir}/${index_base}".*.${ext} "${out_dir}/${index_base}.dict" "${out_dir}/${index_base}.manifest.json" "${out_dir}/${index_base}.md5" "${out_dir}/${index_base}.build.txt"; do
        aws s3 cp "$artifact" "${upload_prefix%/}/$(basename "$artifact")"
    done
}

build_one() {
    local id="$1"
    local index_base="$2"
    local species="$3"
    local assembly="$4"
    local source="$5"
    local url="$6"
    local expected_ext="$7"
    local notes="$8"
    local target_work download fasta prefix actual_ext

    target_work="${work_dir}/${id}"
    download="${target_work}/source.fa.gz"
    fasta="${target_work}/source.fa"
    prefix="${target_work}/${index_base}"

    if [[ "$force" -eq 0 && -s "${out_dir}/${index_base}.zip" && -s "${out_dir}/${index_base}.dict" && -s "${out_dir}/${index_base}.manifest.json" && -s "${out_dir}/${index_base}.md5" ]]; then
        printf 'Skipping %s; outputs already exist in %s. Use --force to rebuild.\n' "$id" "$out_dir"
        return 0
    fi

    printf 'Building %s (%s / %s)\n' "$id" "$species" "$assembly"
    mkdir -p "$target_work"

    if [[ "$force" -eq 1 || ! -s "$download" ]]; then
        rm -f "$download"
        "$curl_bin" --fail --location --silent --show-error --retry 5 --retry-delay 10 -o "$download" "$url"
    fi

    if [[ "$force" -eq 1 || ! -s "$fasta" ]]; then
        rm -f "$fasta"
        gzip -cd "$download" > "$fasta"
    fi

    rm -f "${prefix}".*.bt2 "${prefix}".*.bt2l
    "$bowtie2_build" --threads "$threads" "$fasta" "$prefix"

    actual_ext="$(index_ext_for_prefix "$prefix")"
    validate_index_files "$prefix" "$actual_ext"
    write_sequence_dictionary "$fasta" "$index_base"
    write_provenance "$id" "$index_base" "$species" "$assembly" "$source" "$url" "$expected_ext" "$actual_ext" "$notes"
    write_manifest "$id" "$index_base" "$species" "$assembly" "$source" "$url" "$expected_ext" "$actual_ext" "$notes" "$download" "$fasta" "$prefix"
    copy_index_artifacts "$prefix" "$index_base" "$actual_ext"
    upload_outputs "$index_base" "$actual_ext"

    if [[ "$keep_fasta" -eq 0 ]]; then
        rm -f "$fasta"
    fi

    printf 'Finished %s -> %s/%s.zip\n' "$id" "$out_dir" "$index_base"
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --list)
            list_targets
            exit 0
            ;;
        --targets)
            targets_file="$2"
            shift 2
            ;;
        --out-dir)
            out_dir="$2"
            shift 2
            ;;
        --work-dir)
            work_dir="$2"
            shift 2
            ;;
        --threads)
            threads="$2"
            shift 2
            ;;
        --upload-prefix)
            upload_prefix="$2"
            shift 2
            ;;
        --force)
            force=1
            shift
            ;;
        --keep-fasta)
            keep_fasta=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            break
            ;;
        -*)
            printf 'error: unknown option: %s\n' "$1" >&2
            usage >&2
            exit 1
            ;;
        *)
            target_ids+=("$1")
            shift
            ;;
    esac
done

if [[ "$#" -gt 0 ]]; then
    target_ids+=("$@")
fi

threads="${threads:-$(default_threads)}"

require_cmd "$bowtie2_build"
require_cmd "$samtools_bin"
require_cmd "$curl_bin"
require_cmd python3
require_cmd gzip
require_cmd zip

if [[ ! -f "$targets_file" ]]; then
    printf 'error: target file does not exist: %s\n' "$targets_file" >&2
    exit 1
fi

mkdir -p "$out_dir" "$work_dir"

matched=0
while IFS=$'\t' read -r id index_base species assembly source url expected_ext notes; do
    [[ -z "${id:-}" || "${id:0:1}" == "#" ]] && continue
    if target_selected "$id"; then
        matched=$((matched + 1))
        build_one "$id" "$index_base" "$species" "$assembly" "$source" "$url" "$expected_ext" "$notes"
    fi
done < "$targets_file"

if [[ "$matched" -eq 0 ]]; then
    printf 'error: no target IDs matched. Use --list to see valid IDs.\n' >&2
    exit 1
fi
