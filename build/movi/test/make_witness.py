#!/usr/bin/env python3
"""Assemble a signed test-witness JSON for one Movi index from a run_t1_semantic
results file plus index/binary identity. Runs on the cluster (needs the index
dir + the movi binary present).

Witness = tamper-evident, reproducible certificate that the index passed the
corner-case query tests: re-running the listed commands on the same index.movi
reproduces the recorded results, and self_sha256 covers the whole document.

Usage:
  make_witness.py --results results_yr1.json --index /data/.../index \
      --movi /path/to/movi --movi-commit 34ab5a3 --out test-witness.json \
      [--index-sha <hex>]        # skip the (slow) sha256(index.movi) if known

Records identity (sha256(index.movi), header fingerprint from the on-disk
movi-index.yaml sidecar, movi commit + binary sha256, host, UTC time), the
per-test records from --results, a CHARACTERIZED list of known non-failing
behaviors, a summary verdict, and a top-level self_sha256.
"""
import argparse
import datetime
import hashlib
import json
import os
import socket
import sys

WITNESS_SCHEMA_VERSION = "1.0"

# Known, documented, non-failing behaviors (see FINDINGS.md). Recorded so the
# witness is honest about them rather than silently asserting around them.
CHARACTERIZED = [
    {"behavior": "reference non-ACGT -> A (incl. lowercase c/g/t; soft-mask lost)",
     "impact": "masked/ambiguous reference regions are poly-A in the index"},
    {"behavior": "read-side N/lowercase/% illegal by default; breaks the match "
                 "(pml 0); --ignore-illegal-chars 1 rewrites to A",
     "impact": "asymmetric vs reference (ref N->A) unless the flag is set"},
    {"behavior": "boundary-spanning k-mers may coincidentally occur elsewhere at "
                 "pangenome scale (a real anchor + 1 base)",
     "impact": "kmer-count boundary test asserts majority-absent, not all-absent; "
               "the rigorous no-crossing proof is count MATCHED<LEN + MR1"},
    {"behavior": "--pml is a pseudo statistic (can be < true match length)",
     "impact": "positive control uses --count MATCHED==LEN, not pml"},
    {"behavior": "mphf --kmer-count reports SUM/N_KMERS and omits zero-count "
                 "k-mers; fix-kmer-count is not in mphf",
     "impact": "per-kmer count format differs from the pre-mphf binary"},
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def read_header(index_dir):
    """Read the header fingerprint from the on-disk movi-index.yaml sidecar."""
    sc = os.path.join(index_dir, "movi-index.yaml")
    if not os.path.exists(sc):
        return {"note": "no movi-index.yaml sidecar"}
    try:
        import yaml
        d = yaml.safe_load(open(sc)) or {}
        h = d.get("header", {}) or {}
        return {k: h.get(k) for k in ("mode", "format", "version", "reflen",
                "original_r", "r", "end_bwt_idx", "alphabet", "alpha_size",
                "thresholds")}
    except Exception as e:
        return {"note": "sidecar parse failed: %s" % e}


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--index", required=True)
    ap.add_argument("--movi", required=True)
    ap.add_argument("--movi-commit", required=True)
    ap.add_argument("--harness-commit", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--index-sha", default=None,
                    help="precomputed sha256(index.movi) to skip the slow hash")
    a = ap.parse_args()

    res = json.load(open(a.results))
    movi_bin = os.path.join(a.index, "index.movi")
    idx_sha = a.index_sha or sha256_file(movi_bin)

    witness = {
        "witness_schema_version": WITNESS_SCHEMA_VERSION,
        "kind": "movi-index-test-witness",
        "identity": {
            "index_id": os.path.basename(os.path.dirname(a.index.rstrip("/")))
                        if os.path.basename(a.index.rstrip("/")) == "index"
                        else os.path.basename(a.index.rstrip("/")),
            "index_dir": a.index,
            "index_movi_sha256": idx_sha,
            "index_movi_size_bytes": os.path.getsize(movi_bin),
            "header_fingerprint": read_header(a.index),
            "movi": {"path": a.movi, "commit": a.movi_commit,
                     "sha256_launcher": sha256_file(a.movi)},
            "host": socket.gethostname(),
            "utc_time": datetime.datetime.now(datetime.timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
            "harness_commit": a.harness_commit,
        },
        "source": {"agc_sample": res.get("sample"), "contigs": res.get("contigs")},
        "params": res.get("params", {}),
        "tests": res.get("tests", []),
        "characterized": CHARACTERIZED,
        "summary": {
            "n_tests": res.get("n_tests"),
            "n_fail": res.get("n_fail"),
            "verdict": res.get("verdict"),
        },
        "self_sha256": "",
    }
    witness["self_sha256"] = hashlib.sha256(canonical(witness)).hexdigest()
    with open(a.out, "w") as fh:
        json.dump(witness, fh, indent=2)

    print("witness: %s  verdict=%s  n_tests=%s n_fail=%s  self_sha256=%s"
          % (a.out, witness["summary"]["verdict"], witness["summary"]["n_tests"],
             witness["summary"]["n_fail"], witness["self_sha256"][:16]))
    # exit nonzero if the underlying run failed, so callers can gate on it
    sys.exit(0 if (res.get("n_fail") == 0) else 1)


if __name__ == "__main__":
    main()
