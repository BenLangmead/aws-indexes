#!/usr/bin/env python3
"""T2 soundness anchor: build a small adversarial --separators index with mphf,
compute ground truth in Python (oracle), and assert Movi's query outputs match
exactly (count / kmer-count) or satisfy structural invariants (pml / classify /
filter / mem). Passing T2 proves the mphf query engine + our parsers are correct,
so the oracle-free metamorphic assertions in T1 (on the big production indexes)
can be trusted.

Usage:
  run_t2.py --movi /path/to/movi [--work DIR] [--ftab-k 4]
Exit 0 iff every assertion passes.
"""
import argparse
import os
import shutil
import subprocess
import sys

import movi_test_lib as M

# Adversarial reference: distinctive records so boundary joins never occur by
# chance; duplicate record; an N-run; a homopolymer.
REC_A = "ACGTACGTACGTACGTACACAC"      # 22
REC_B = "GTGTGTTTAAGGGCCCTTTAAG"      # 22, distinctive
REC_D = "TTAACCGGATCGATCGTTAACC"      # 22, appears twice (duplicate)
REC_N = "ACGTACGTNNNNACGTACGTAC"      # 22, N-run
REC_H = "AAAAAAAAAAAAAAAAAAAA"        # 20, homopolymer
RECORDS = [REC_A, REC_B, REC_D, REC_D, REC_N, REC_H]


class Results:
    def __init__(self):
        self.rows = []

    def check(self, name, ok, detail=""):
        self.rows.append((name, bool(ok), detail))
        print("  %-4s %-34s %s" % ("PASS" if ok else "FAIL", name, detail))

    def failed(self):
        return [r for r in self.rows if not r[1]]


def build_index(movi, work, ftab_k):
    idx = os.path.join(work, "idx")
    fa = os.path.join(work, "ref.fa")
    M.write_fasta(fa, [("rec%d" % i, r) for i, r in enumerate(RECORDS)])
    if os.path.isdir(idx):
        shutil.rmtree(idx)
    p = subprocess.run(
        [movi, "build", "--separators", "--type", "regular-thresholds",
         "--ftab-k", str(ftab_k), "--fasta", fa, "--index", idx],
        capture_output=True, text=True, timeout=600)
    if not os.path.exists(os.path.join(idx, "index.movi")):
        sys.stderr.write("BUILD FAILED:\n" + p.stdout + p.stderr + "\n")
        sys.exit(2)
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--movi", required=True)
    ap.add_argument("--work", default="/tmp/movi_t2")
    ap.add_argument("--ftab-k", type=int, default=4)
    ap.add_argument("-k", "--kmer-k", type=int, default=6)
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)

    text = M.build_index_text(RECORDS)          # the exact index text (oracle)
    idx = build_index(a.movi, a.work, a.ftab_k)
    R = Results()

    def count_of(name, seq):
        fa = M.write_fasta(os.path.join(a.work, name + ".fa"), [(name, seq)])
        rc, so, _, _ = M.run_movi(a.movi, idx, fa, ["--count"])
        return M.parse_count(so).get(name)

    ca = clean = M.clean_seq
    A, B, D = ca(REC_A), ca(REC_B), ca(REC_D)

    print("== T2: count vs oracle ==")
    cases = {
        "pos_within":   A[3:15],                       # fully within rec_A
        "boundary_AB":  A[-8:] + B[:8],                # artificial contig|contig join
        "boundary_fwdrc": A[-8:] + M.revcomp(A)[:8],   # FWD|RC junction of rec_A
        "dup":          D[2:14],                       # in the duplicated record
        "homopolymer":  "AAAAAAAA",
        "whole_record": A,                             # entire rec_A
        "longer_than_rec": A + "TTT",                  # 25-mer, cannot fully occur
        "one_char":     "A",
    }
    for name, q in cases.items():
        om, oc = M.oracle_count(text, q)
        got = count_of(name, q)
        ok = got is not None and got[0] == om and got[2] == oc
        R.check("count/" + name, ok, "movi=%s oracle=(m=%d,c=%d)" % (got, om, oc))
    # explicit boundary semantics: spanning query must NOT fully match
    for name in ("boundary_AB", "boundary_fwdrc", "longer_than_rec"):
        got = count_of(name, cases[name])
        R.check("boundary_partial/" + name, got is not None and got[0] < len(cases[name]),
                "matched=%d < len=%d" % (got[0] if got else -1, len(cases[name])))
    # positive fully matches
    got = count_of("pos_within", cases["pos_within"])
    R.check("positive_full/pos_within", got and got[0] == len(cases["pos_within"]) and got[2] >= 1,
            "matched==len and count>=1")

    print("== T2: RC symmetry (MR2) ==")
    s = B[2:16]
    if s != M.revcomp(s):
        cf, cr = count_of("rc_fwd", s), count_of("rc_rev", M.revcomp(s))
        R.check("rc_symmetry", cf and cr and cf[2] == cr[2],
                "count(S)=%s count(RC(S))=%s" % (cf, cr))
    else:
        R.check("rc_symmetry", True, "(skipped: S is self-RC)")

    print("== T2: kmer-count vs oracle ==")
    k = a.kmer_k
    for name, q in (("kc_within", A), ("kc_boundary", A[-8:] + B[:8])):
        fa = M.write_fasta(os.path.join(a.work, name + ".fa"), [(name, q)])
        rc, so, _, _ = M.run_movi(a.movi, idx, fa, ["--kmer-count", "-k", str(k)])
        parsed = M.parse_kmer_count(so).get(name)
        oracle = M.oracle_kmer_counts(text, q, k)        # [(pos,count)] all windows
        exp = {p: c for p, c in oracle if c > 0}         # mphf omits zero-count k-mers
        if parsed is None:
            R.check("kmer-count/" + name, False, "no output")
        else:
            got = {p: c for p, c in parsed["per"]}
            R.check("kmer-count/" + name, got == exp,
                    "movi=%s oracle_nz=%s" % (sorted(got.items()), sorted(exp.items())))
        if name == "kc_boundary":
            got = {p: c for p, c in (parsed["per"] if parsed else [])}
            spanning = [p for p, c in oracle if c == 0]
            R.check("kmer-count/boundary_spanning_absent",
                    len(spanning) > 0 and all(p not in got for p in spanning),
                    "%d spanning k-mers absent from output" % len(spanning))

    print("== T2: pml illegal-char structural ==")
    def pml_of(name, seq, extra=None):
        fa = M.write_fasta(os.path.join(a.work, name + ".fa"), [(name, seq)])
        rc, so, _, _ = M.run_movi(a.movi, idx, fa, ["--pml"], extra=extra)
        return M.parse_pml(so).get(name)
    qn = "ACGTACGTNNNNACGTAC"                 # N at positions 8..11
    pn = pml_of("pml_N", qn)
    R.check("pml/N_breaks", pn and all(pn[i] == 0 for i in range(8, 12)),
            "zeros at N positions: %s" % (pn[8:12] if pn else None))
    pn1 = pml_of("pml_N_ic1", qn, extra=["--ignore-illegal-chars", "1"])
    R.check("pml/ignore_illegal_changes", pn and pn1 and pn1[8:12] != pn[8:12],
            "N->A extends: %s vs %s" % (pn1[8:12] if pn1 else None, pn[8:12] if pn else None))
    qp = "ACGTACGT" + M.SEP + "ACGTAC"        # % at position 8
    pp = pml_of("pml_pct", qp)
    R.check("pml/pct_breaks", pp and pp[8] == 0, "zero at %% position: %s" % (pp[8] if pp else None))
    ql = "acgtacgtACGTAC"                     # lowercase 0..7
    pl = pml_of("pml_lower", ql)
    R.check("pml/lowercase_illegal", pl and all(pl[i] == 0 for i in range(8)),
            "zeros at lowercase: %s" % (pl[:8] if pl else None))

    print("== T2: classify / filter ==")
    pos, neg = A, "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"     # poly-C absent from ref
    cf = M.write_fasta(os.path.join(a.work, "cls.fa"), [("posr", pos), ("negr", neg)])
    rc, so, _, _ = M.run_movi(a.movi, idx, cf, ["--classify"])
    cl = M.parse_classify(so)
    R.check("classify/positive_FOUND", cl.get("posr") == "FOUND", "posr=%s" % cl.get("posr"))
    R.check("classify/negative_NOT_PRESENT", cl.get("negr") == "NOT_PRESENT", "negr=%s" % cl.get("negr"))
    rc, so, _, _ = M.run_movi(a.movi, idx, cf, ["--filter"])
    kept = M.parse_filter(so)
    R.check("filter/keeps_positive", "posr" in kept and "negr" not in kept, "kept=%s" % sorted(kept))
    rc, so, _, _ = M.run_movi(a.movi, idx, cf, ["--filter"], extra=["-v"])
    keptv = M.parse_filter(so)
    R.check("filter/invert", "negr" in keptv and "posr" not in keptv, "kept(-v)=%s" % sorted(keptv))

    print("== T2: MEM sanity ==")
    mf = M.write_fasta(os.path.join(a.work, "mem.fa"), [("memr", A)])
    rc, so, mems, _ = M.run_movi(a.movi, idx, mf,
                                 ["--mem", "--min-mem-length", "6", "--ftab-k", str(a.ftab_k)],
                                 out_prefix=os.path.join(a.work, "memout"))
    mm = M.parse_mem(mems or so).get("memr", [])
    R.check("mem/produces_output", len(mm) >= 1, "mems=%s" % mm)
    R.check("mem/length_bounded", all(o + L <= len(A) for o, L, _ in mm) if mm else False,
            "all MEMs within read length")

    print()
    fails = R.failed()
    print("T2 RESULT: %d/%d passed%s" % (len(R.rows) - len(fails), len(R.rows),
          "" if not fails else "  FAILED: " + ", ".join(f[0] for f in fails)))
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
