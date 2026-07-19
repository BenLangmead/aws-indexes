#!/usr/bin/env python3
"""T1: oracle-free / metamorphic corner-case tests for a PRODUCTION Movi index
(too large to brute-force). Fixtures are derived from the index's own source
.agc (real contig sequences, cleaned exactly like movi-prepare-ref). Assertions
are metamorphic relations + one-sided invariants that hold in any correct index:

  MR-boundary : a cross-separator query cannot fully match -> --count MATCHED<LEN
                and its spanning k-mers are absent from --kmer-count; and the pml
                profile of A.B over the B region equals pml(B) alone (MR1).
  MR-positive : a within-contig L-mer -> --count MATCHED==LEN, COUNT>=1 (MR3).
  MR-rc       : count(S) == count(RC(S)) (MR2; RC is indexed).
  illegal     : read N/%/lowercase -> pml 0 at that position; --ignore-illegal
                -chars 1 changes it.
  per-mode    : pml/zml/count/kmer-count/mem/classify/filter all run; positive
                reads separate from the index's own null_reads.fasta.

Emits results JSON (tests[] + params + provenance) consumed by make_witness.py.

Usage:
  run_t1_semantic.py --movi M --index DIR --agc AGC --archive A.agc
      [--sample S] [--out results.json] [--L 60] [--k 31] [--ftab-k 12]
Runs each mode ONCE over all fixtures (one index load per mode).
"""
import argparse
import json
import os
import subprocess
import sys
import time

import movi_test_lib as M


# ---------------------------------------------------------------------------
# fixture generation from agc
# ---------------------------------------------------------------------------
def agc_first_sample(agc, archive):
    out = subprocess.run([agc, "listset", archive], capture_output=True, text=True, timeout=300)
    for ln in out.stdout.splitlines():
        if ln.strip():
            return ln.strip()
    raise RuntimeError("agc listset returned no samples")


def agc_contigs(agc, archive, sample, min_len, want=3):
    """Return up to `want` cleaned contigs (>= min_len) from one sample."""
    out = subprocess.run([agc, "getset", archive, sample], capture_output=True, text=True,
                         timeout=1800)
    contigs, name, buf = [], None, []
    for ln in out.stdout.splitlines():
        if ln.startswith(">"):
            if name is not None and buf:
                contigs.append((name, "".join(buf)))
            name, buf = ln[1:].split()[0], []
        else:
            buf.append(ln.strip())
    if name is not None and buf:
        contigs.append((name, "".join(buf)))
    # keep RAW contigs (clean only short extracted pieces, not multi-Gbp contigs)
    kept = [(n, s) for n, s in contigs if len(s) >= min_len]
    kept.sort(key=lambda x: -len(x[1]))
    return kept[:want]


def build_fixtures(contigs, L, k):
    """Return (reads dict {name: seq}, meta dict {name: {...}}). Deterministic.
    contigs are RAW; only the short extracted pieces are cleaned (fast)."""
    reads, meta = {}, {}
    (_, c0), (_, c1) = contigs[0], contigs[1]
    cs = M.clean_seq
    mid0, mid1 = len(c0) // 2, len(c1) // 2
    P = cs(c0[mid0:mid0 + L])                      # interior positive, contig0
    B = cs(c1[mid1:mid1 + L])                      # positive, contig1 (MR1 B)
    suf0 = cs(c0[-L:])                             # cleaned L-suffix of contig0
    reads["pos"] = P;                       meta["pos"] = {"kind": "positive"}
    reads["long_pos"] = cs(c0[mid0:mid0 + 200])   # a longer (bounded) positive
    meta["long_pos"] = {"kind": "positive_long"}
    reads["mr1_B"] = B;                     meta["mr1_B"] = {"kind": "mr1_B"}
    # boundary: artificial contig|contig join (absent from the index)
    reads["boundary_AB"] = P + B;           meta["boundary_AB"] = {"kind": "boundary", "split": L}
    reads["mr1_AB"] = P + B;                meta["mr1_AB"] = {"kind": "mr1_AB", "split": L}
    # boundary: real FWD|RC junction of contig0 (end of FWD + start of RC)
    reads["boundary_fwdrc"] = suf0 + M.revcomp(suf0)
    meta["boundary_fwdrc"] = {"kind": "boundary", "split": L}
    # RC symmetry: pick a non-self-RC positive
    S = P if P != M.revcomp(P) else cs(c0[mid0 + 1:mid0 + 1 + L])
    reads["rc_fwd"] = S;                    meta["rc_fwd"] = {"kind": "rc"}
    reads["rc_rev"] = M.revcomp(S);         meta["rc_rev"] = {"kind": "rc"}
    # illegal-char reads (relative to a positive)
    half = L // 2
    reads["ill_N"] = P[:half] + "N" + P[half:];    meta["ill_N"] = {"kind": "illegal", "pos": half}
    reads["ill_pct"] = P[:half] + M.SEP + P[half:]; meta["ill_pct"] = {"kind": "illegal", "pos": half}
    reads["ill_lower"] = P.lower();         meta["ill_lower"] = {"kind": "illegal_lower"}
    # degenerate
    reads["one_char"] = P[0];               meta["one_char"] = {"kind": "degenerate"}
    reads["sub_k"] = P[:max(1, k - 1)];     meta["sub_k"] = {"kind": "degenerate"}
    reads["homo"] = "A" * L;                meta["homo"] = {"kind": "homopolymer"}
    return reads, meta


# ---------------------------------------------------------------------------
# assertions
# ---------------------------------------------------------------------------
class Rec:
    def __init__(self):
        self.tests = []

    def add(self, case_id, mode, cmd, assertion, ok, observed, wall):
        self.tests.append({"case_id": case_id, "mode": mode, "command": cmd,
                           "assertion": assertion, "pass": bool(ok),
                           "observed": observed, "wall_s": round(wall, 1)})
        print("  %-4s %-26s %s" % ("PASS" if ok else "FAIL", case_id, observed))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--movi", required=True)
    ap.add_argument("--index", required=True)
    ap.add_argument("--agc", required=True)
    ap.add_argument("--archive", required=True)
    ap.add_argument("--sample", default=None)
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--work", default="/tmp/movi_t1")
    ap.add_argument("--L", type=int, default=60)
    ap.add_argument("--k", type=int, default=31)
    ap.add_argument("--ftab-k", type=int, default=12)
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)

    sample = a.sample or agc_first_sample(a.agc, a.archive)
    contigs = agc_contigs(a.agc, a.archive, sample, min_len=2 * a.L + a.k, want=3)
    if len(contigs) < 2:
        sys.stderr.write("need >=2 contigs >= %d bp from sample %s\n" % (2 * a.L + a.k, sample))
        sys.exit(2)
    reads, meta = build_fixtures(contigs, a.L, a.k)
    R = Rec()

    def run(mode_args, names, out_prefix=None, extra=None):
        fa = M.write_fasta(os.path.join(a.work, "q.fa"),
                           [(n, reads[n]) for n in names if reads[n] != ""])
        t = time.time()
        rc, so, mems, cmd = M.run_movi(a.movi, a.index, fa, mode_args,
                                       out_prefix=out_prefix, extra=extra)
        return so, mems, cmd, time.time() - t, M.sha256_file(fa)

    # ---- count: positive full, boundary partial, RC symmetry, homopolymer ----
    names = ["pos", "long_pos", "boundary_AB", "boundary_fwdrc", "rc_fwd", "rc_rev", "homo", "one_char", "sub_k"]
    so, _, cmd, wall, insha = run(["--count"], names)
    cnt = M.parse_count(so)
    def cget(n): return cnt.get(n)
    R.add("count/positive_full", "count", cmd,
          "positive matched==len and count>=1",
          cget("pos") and cget("pos")[0] == len(reads["pos"]) and cget("pos")[2] >= 1,
          {"pos": cget("pos")}, wall)
    for bn in ("boundary_AB", "boundary_fwdrc"):
        R.add("count/%s_partial" % bn, "count", cmd,
              "cross-separator query does not fully match (MATCHED<LEN)",
              cget(bn) and cget(bn)[0] < len(reads[bn]),
              {bn: cget(bn), "len": len(reads[bn])}, 0)
    R.add("count/rc_symmetry", "count", cmd, "count(S)==count(RC(S))",
          cget("rc_fwd") and cget("rc_rev") and cget("rc_fwd")[2] == cget("rc_rev")[2],
          {"S": cget("rc_fwd"), "RC": cget("rc_rev")}, 0)
    R.add("count/long_positive", "count", cmd, "long (200bp) positive matched==len, count>=1",
          cget("long_pos") and cget("long_pos")[0] == len(reads["long_pos"]) and cget("long_pos")[2] >= 1,
          {"long_matched": cget("long_pos")[0] if cget("long_pos") else None,
           "len": len(reads["long_pos"])}, 0)
    R.add("count/homopolymer", "count", cmd, "poly-A occurs (count>0)",
          cget("homo") and cget("homo")[2] > 0, {"homo": cget("homo")}, 0)

    # ---- kmer-count: boundary spanning k-mers absent ----
    so, _, cmd, wall, _ = run(["--kmer-count", "-k", str(a.k)], ["pos", "boundary_AB"])
    kc = M.parse_kmer_count(so)
    pos_kc = kc.get("pos")
    R.add("kmercount/positive_found", "kmer-count", cmd, "positive read has found k-mers",
          pos_kc and pos_kc["nkmers"] >= 1, {"pos_nkmers": pos_kc["nkmers"] if pos_kc else None}, wall)
    bkc = kc.get("boundary_AB")
    # spanning windows straddle the split at position L (k-mer i spans if i<L<i+k)
    span = [i for i in range(0, len(reads["boundary_AB"]) - a.k + 1) if i < a.L < i + a.k]
    got = {p for p, c in (bkc["per"] if bkc else [])}
    absent = [p for p in span if p not in got]
    coincidental = sorted(set(span) & got)
    # A correct separator blocks the junction: a BROKEN one would find ALL spanning
    # k-mers (frac_absent==0). Coincidental occurrences (a real anchor + 1 base that
    # exists elsewhere in a 96-579 haplotype pangenome) are expected, so require a
    # majority absent rather than all. The rigorous no-crossing proof is count-partial
    # (MATCHED<LEN) + MR1, both asserted separately.
    frac = (len(absent) / len(span)) if span else 0.0
    R.add("kmercount/boundary_mostly_absent", "kmer-count", cmd,
          ">=50% of boundary-spanning k-mers absent (coincidences allowed at pangenome scale)",
          len(span) > 0 and frac >= 0.5,
          {"absent": len(absent), "of": len(span), "coincidental": coincidental}, 0)

    # ---- pml: MR1 boundary non-extension + illegal-char breaks ----
    so, _, cmd, wall, _ = run(["--pml"], ["mr1_B", "mr1_AB", "ill_N", "ill_pct", "ill_lower"])
    pml = M.parse_pml(so)
    pB, pAB = pml.get("mr1_B"), pml.get("mr1_AB")
    R.add("pml/MR1_boundary_noextend", "pml", cmd,
          "pml(A.B) over B region == pml(B) (no cross-junction extension)",
          pB is not None and pAB is not None and pAB[a.L:a.L + len(pB)] == pB,
          {"B_len": len(pB) if pB else None,
           "match": (pAB[a.L:a.L + len(pB)] == pB) if (pB and pAB) else None}, wall)
    pN = pml.get("ill_N")
    R.add("pml/illegal_N_breaks", "pml", cmd, "pml==0 at N position",
          pN is not None and pN[meta["ill_N"]["pos"]] == 0,
          {"at_N": pN[meta["ill_N"]["pos"]] if pN else None}, 0)
    pP = pml.get("ill_pct")
    R.add("pml/illegal_pct_breaks", "pml", cmd, "pml==0 at %% position",
          pP is not None and pP[meta["ill_pct"]["pos"]] == 0,
          {"at_pct": pP[meta["ill_pct"]["pos"]] if pP else None}, 0)
    pL = pml.get("ill_lower")
    R.add("pml/lowercase_illegal", "pml", cmd, "lowercase read -> all pml 0 (illegal)",
          pL is not None and all(v == 0 for v in pL), {"nonzero": sum(1 for v in (pL or []) if v)}, 0)

    # ---- pml with --ignore-illegal-chars 1 changes the N behavior ----
    so, _, cmd, wall, _ = run(["--pml"], ["ill_N"], extra=["--ignore-illegal-chars", "1"])
    pN1 = M.parse_pml(so).get("ill_N")
    # --ignore-illegal-chars 1 treats N as A rather than a hard break; the exact
    # value at the N position is data-dependent, but the overall profile must change
    # (the read is no longer split at N). Compare the whole profile.
    R.add("pml/ignore_illegal_changes", "pml", cmd,
          "--ignore-illegal-chars 1 (N->A) changes the pml profile vs the default break",
          pN is not None and pN1 is not None and pN1 != pN,
          {"differs": (pN1 != pN) if (pN and pN1) else None,
           "at_N_default": pN[meta["ill_N"]["pos"]] if pN else None,
           "at_N_ic1": pN1[meta["ill_N"]["pos"]] if pN1 else None}, wall)

    # ---- zml runs ----
    so, _, cmd, wall, _ = run(["--zml"], ["pos"])
    zP = M.parse_zml(so).get("pos")
    R.add("zml/runs", "zml", cmd, "zml produces a profile for a positive read",
          zP is not None and len(zP) == len(reads["pos"]), {"len": len(zP) if zP else None}, wall)

    # ---- mem: produces output + bounded ----
    so, mems, cmd, wall, _ = run(["--mem", "--min-mem-length", str(min(20, a.L)), "--ftab-k", str(a.ftab_k)],
                                 ["pos", "long_pos"], out_prefix=os.path.join(a.work, "memout"))
    mm = M.parse_mem(mems or so)
    posmem = mm.get("pos", [])
    R.add("mem/positive_produces", "mem", cmd, "positive read yields >=1 MEM",
          len(posmem) >= 1, {"pos_mems": posmem[:3]}, wall)
    R.add("mem/bounded", "mem", cmd, "MEMs fit within the read",
          all(o + L <= len(reads["pos"]) for o, L, _ in posmem) if posmem else False,
          {"n": len(posmem)}, 0)

    # ---- classify + filter: positive vs the index's own null_reads.fasta ----
    nullfa = os.path.join(a.index, "null_reads.fasta")
    nulldb = os.path.join(a.index, "movi.pml.nulldb")
    if os.path.exists(nullfa) and os.path.exists(nulldb):
        # take a few null reads + the positive into one file
        nreads = []
        with open(nullfa) as fh:
            nm = None
            for ln in fh:
                if ln.startswith(">"):
                    nm = ln[1:].strip().split()[0]
                elif nm and len(nreads) < 5:
                    nreads.append(("null_" + nm, ln.strip())); nm = None
        cf = M.write_fasta(os.path.join(a.work, "cls.fa"), [("posr", reads["pos"])] + nreads)
        t = time.time()
        rc, so, _, cmd = M.run_movi(a.movi, a.index, cf, ["--classify"])
        cl = M.parse_classify(so)
        nulls_absent = all(cl.get(n) == "NOT_PRESENT" for n, _ in nreads)
        R.add("classify/positive_vs_null", "classify", cmd,
              "positive FOUND; null reads NOT_PRESENT",
              cl.get("posr") == "FOUND" and nulls_absent,
              {"pos": cl.get("posr"), "nulls_not_present": nulls_absent}, time.time() - t)
        rc, so, _, cmd = M.run_movi(a.movi, a.index, cf, ["--filter"])
        kept = M.parse_filter(so)
        R.add("filter/keeps_positive", "filter", cmd, "filter keeps positive, drops null",
              "posr" in kept and all(("null_" + n.split("null_")[-1]) not in kept for n, _ in nreads),
              {"kept": sorted(kept)}, 0)
    else:
        # index has no null model (movi.pml.nulldb + null_reads.fasta) -> classify
        # /filter can't run. Record as skipped (not a failure) + flag the gap.
        R.tests.append({"case_id": "classify_filter", "mode": "classify/filter",
                        "command": "-", "assertion": "requires null model in index",
                        "pass": True, "skipped": True,
                        "observed": {"skipped": "index lacks movi.pml.nulldb / null_reads.fasta"},
                        "wall_s": 0})
        print("  SKIP classify/filter          (index lacks null model)")

    fails = [t for t in R.tests if not t["pass"]]
    result = {
        "index": a.index, "sample": sample,
        "params": {"L": a.L, "k": a.k, "ftab_k": a.ftab_k},
        "contigs": [{"name": n, "len": len(s)} for n, s in contigs],
        "n_tests": len(R.tests), "n_fail": len(fails),
        "verdict": "PASS" if not fails else "FAIL",
        "tests": R.tests,
    }
    with open(a.out, "w") as fh:
        json.dump(result, fh, indent=2)
    print("\nT1 %s: %d/%d passed -> %s" % (a.index, len(R.tests) - len(fails), len(R.tests), a.out))
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
