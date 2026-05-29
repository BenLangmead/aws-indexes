#!/usr/bin/env python3
"""
Compare Bowtie Index Zone catalog (xfer/bt/shortname_map.csv) to objects under
s3://genome-idx/bt/ (or --bucket/--prefix).

Requires AWS CLI: `aws s3api list-objects-v2` (credentials or public read as
configured for the bucket).

Usage:
  cd build/bowtie && python3 audit_s3.py
  python3 audit_s3.py --strict   # exit 1 if any expected object is missing
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = REPO_ROOT / "xfer" / "bt" / "shortname_map.csv"

INDEX_SUFFIXES = [".1", ".2", ".3", ".4", ".rev.1", ".rev.2"]


def parse_shortname_row(row: list[str]) -> tuple[str, str, str, list[str]] | None:
    """Return (short_id, index_base, index_ext, metadata_types) or None."""
    if not row or not row[0].strip() or row[0].startswith("#"):
        return None
    short = row[0].strip()
    index_base = row[1].strip()
    ext = row[6].strip() if len(row) > 6 and row[6].strip() else "bt2"
    if ext not in ("bt2", "bt2l"):
        raise ValueError(f"{short}: invalid index extension {ext!r}")
    meta = ["md5"]
    if len(row) > 7 and row[7].strip():
        meta.extend(t.strip() for t in row[7].split(";") if t.strip())
    allowed = {"md5", "dict", "manifest"}
    bad = sorted(set(meta) - allowed)
    if bad:
        raise ValueError(f"{short}: unknown metadata types {bad}")
    meta = [m for m in ["md5", "dict", "manifest"] if m in meta]
    return short, index_base, ext, meta


def aws_list_keys(bucket: str, prefix: str) -> set[str]:
    """Return set of object keys (no bucket) under prefix."""
    keys: set[str] = set()
    token = ""
    while True:
        cmd = [
            "aws",
            "s3api",
            "list-objects-v2",
            "--bucket",
            bucket,
            "--prefix",
            prefix,
            "--output",
            "json",
        ]
        if token:
            cmd.extend(["--continuation-token", token])
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr or proc.stdout or "aws s3api failed\n")
            raise RuntimeError("aws s3api list-objects-v2 failed")
        data = json.loads(proc.stdout)
        for obj in data.get("Contents", []) or []:
            key = obj.get("Key", "")
            if key:
                keys.add(key)
        if not data.get("IsTruncated"):
            break
        token = data.get("NextContinuationToken") or ""
        if not token:
            break
    return keys


def expected_keys_for_index(
    index_base: str, ext: str, meta: list[str], require_metadata: bool
) -> list[str]:
    p = f"bt/{index_base}"
    keys = [f"{p}.zip", f"{p}.md5"]
    for suf in INDEX_SUFFIXES:
        keys.append(f"{p}{suf}.{ext}")
    want_sidecars = require_metadata or ("dict" in meta and "manifest" in meta)
    if want_sidecars:
        keys.extend([f"{p}.dict", f"{p}.manifest.json", f"{p}.build.txt"])
    return keys


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit Bowtie bt/ objects vs shortname_map.csv")
    ap.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help="Path to shortname_map.csv",
    )
    ap.add_argument("--bucket", default=os.environ.get("BT_AUDIT_BUCKET", "genome-idx"))
    ap.add_argument("--prefix", default=os.environ.get("BT_AUDIT_PREFIX", "bt/"))
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 if any catalogued object is missing",
    )
    ap.add_argument(
        "--require-metadata",
        action="store_true",
        help="Treat .dict, .manifest.json, .build.txt as required for every index",
    )
    args = ap.parse_args()

    prefix = args.prefix
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    rows: list[tuple[str, str, str, list[str]]] = []
    with open(args.csv, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        for row in reader:
            parsed = parse_shortname_row(row)
            if parsed:
                rows.append(parsed)

    try:
        s3_keys = aws_list_keys(args.bucket, prefix)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 2

    # Normalize to keys relative to bucket root (list-objects returns full keys)
    # prefix is e.g. bt/ — keys are like bt/hs1.zip
    missing_all: list[tuple[str, str]] = []
    print(f"Bucket s3://{args.bucket}/{prefix} — {len(s3_keys)} objects listed\n")

    for short, index_base, ext, meta in rows:
        expected = expected_keys_for_index(index_base, ext, meta, args.require_metadata)
        missing = [k for k in expected if k not in s3_keys]
        status = "OK" if not missing else "MISSING"
        meta_s = "+".join(meta) if len(meta) > 1 else meta[0]
        print(f"{status}\t{short}\t{index_base}\t{ext}\tmeta={meta_s}")
        for k in missing:
            print(f"  missing: s3://{args.bucket}/{k}")
            missing_all.append((short, k))
        if not missing:
            print(f"  ({len(expected)} objects)")

    if missing_all:
        print(f"\nTotal missing: {len(missing_all)}")
        if args.strict:
            return 1
    else:
        print("\nAll expected objects present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
