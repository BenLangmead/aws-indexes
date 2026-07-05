#!/usr/bin/env python3
"""Build a `seqdict` precursor JSON for a Movi pangenome index.

For each haplotype (an agc "set") we extract its FASTA from the agc archive and pipe
it through `samtools dict -`.  From the resulting @SQ header lines we read, per contig:
  SN -> name, LN -> length, M5 -> md5
The M5 convention is samtools/refget/Picard: sequence is UPPERCASED and newlines are
stripped, but non-ACGT characters (N, IUPAC codes, gaps) are hashed LITERALLY (not
collapsed to a gap char).  This makes our pangenome contig MD5s directly comparable to
standard reference `.dict` M5s.

The per-haplotype identifier `xor_of_md5s` is the bitwise XOR of its contigs' 16-byte
M5 values.  It is order-independent (contig order in the archive does not matter).
Caveat: two byte-identical contigs cancel to zero; rare within one haplotype.

Provenance: records the source .agc path, its on-disk md5, size, agc version, and the
number of distinct haplotypes (sets) stored in the archive (which may exceed the number
actually indexed when a subset build was done).
"""
import argparse, hashlib, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_out(cmd, check=True):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and p.returncode != 0:
        raise RuntimeError("cmd failed (%d): %s\n%s" % (p.returncode, " ".join(cmd), p.stderr))
    return p.stdout


def file_md5(path, bufsize=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(bufsize), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_sq(dict_text):
    contigs = []
    for line in dict_text.splitlines():
        if not line.startswith("@SQ"):
            continue
        d = {}
        for fld in line.split("\t")[1:]:
            k, sep, v = fld.partition(":")
            if sep:
                d[k] = v
        contigs.append({"name": d.get("SN"),
                        "length": int(d.get("LN", "0")),
                        "md5": d.get("M5")})
    return contigs


def xor_md5s(md5hexes):
    acc = bytearray(16)
    for m in md5hexes:
        if not m:
            continue
        b = bytes.fromhex(m)
        for i in range(16):
            acc[i] ^= b[i]
    return acc.hex()


def pansn_prefix(name):
    if name and name.count("#") >= 2:
        p = name.split("#")
        return p[0] + "#" + p[1]
    return None


def do_set(agc, s, agc_bin, samtools_bin, threads):
    getset = subprocess.Popen([agc_bin, "getset", agc, s, "-t", str(threads)],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    dictp = subprocess.run([samtools_bin, "dict", "-"], stdin=getset.stdout,
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    getset.stdout.close()
    if getset.wait() != 0:
        raise RuntimeError("agc getset failed for set %s" % s)
    contigs = parse_sq(dictp.stdout)
    prefixes = {pansn_prefix(c["name"]) for c in contigs if pansn_prefix(c["name"])}
    return {
        "name": s,
        "pansn_prefix": (prefixes.pop() if len(prefixes) == 1 else None),
        "n_contigs": len(contigs),
        "total_length": sum(c["length"] for c in contigs),
        "xor_of_md5s": xor_md5s([c["md5"] for c in contigs]),
        "contigs": contigs,
    }


def agc_version(agc_bin):
    try:
        p = subprocess.run([agc_bin], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return p.stdout.split("v.")[1].split("[")[0].strip()
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--agc", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--collection", required=True)
    ap.add_argument("--feeds-index", default="")
    ap.add_argument("--sets", default="", help="comma-separated set names; default = all in archive")
    ap.add_argument("--threads", type=int, default=4, help="threads per agc getset")
    ap.add_argument("--jobs", type=int, default=4, help="concurrent haplotypes")
    ap.add_argument("--agc-bin", default="agc")
    ap.add_argument("--samtools-bin", default="samtools")
    args = ap.parse_args()

    all_sets = [x.strip() for x in run_out([args.agc_bin, "listset", args.agc]).splitlines() if x.strip()]
    sets = [s for s in args.sets.split(",") if s] if args.sets else all_sets

    haps = [None] * len(sets)
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(do_set, args.agc, s, args.agc_bin, args.samtools_bin, args.threads): i
                for i, s in enumerate(sets)}
        done = 0
        for f in as_completed(futs):
            i = futs[f]
            haps[i] = f.result()
            done += 1
            print("[%d/%d] %s (%d contigs)" % (done, len(sets), sets[i], haps[i]["n_contigs"]),
                  file=sys.stderr, flush=True)

    doc = {
        "schema_version": "1.0",
        "kind": "seqdict",
        "collection": args.collection,
        "feeds_index": args.feeds_index,
        "md5_normalization": {
            "tool": "samtools dict (M5 tag)",
            "case_insensitive": True,
            "non_acgt_maps_to": None,
            "strip_whitespace": True,
            "algorithm": "md5",
            "per_haplotype": ("xor_of_md5s = bitwise XOR of constituent contig M5 (16-byte) "
                              "values; order-independent; identical contigs cancel"),
        },
        "source_agc": {
            "path": os.path.abspath(args.agc),
            "file_md5": file_md5(args.agc),
            "file_size": os.path.getsize(args.agc),
            "agc_version": agc_version(args.agc_bin),
            "n_haplotypes_in_archive": len(all_sets),
        },
        "n_haplotypes_indexed": len(sets),
        "haplotypes": haps,
    }
    with open(args.out, "w") as o:
        json.dump(doc, o, indent=1)
    print("wrote %s: %d haplotypes, total_length=%d"
          % (args.out, len(sets), sum(h["total_length"] for h in haps)), file=sys.stderr)


if __name__ == "__main__":
    main()
