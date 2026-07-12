#!/usr/bin/env python3
"""Shared library for the Movi corner-case query-test harness.

Contains:
  * reference cleaning that reproduces movi-prepare-ref EXACTLY (incl. the
    lowercase-c/g/t -> A quirk) and the FWD % RC % index-text layout,
  * a brute-force oracle over a small in-memory text (exact for --count and
    --kmer-count; PML/ZML are pseudo statistics and are checked metamorphically,
    not oracled),
  * output parsers for every query mode (formats verified empirically against
    movi-mphf @34ab5a3; see FINDINGS.md),
  * a thin movi runner.

Design notes (from FINDINGS.md):
  --count  -> NAME \t MATCHED/LEN \t COUNT   (MATCHED = longest matching suffix)
  --pml/--zml -> ">NAME\n<space-separated per-position ints>"
  --kmer-count (mphf) -> NAME \t SUM_OF_COUNTS/N_KMERS \t POS:COUNT ...
  --mem    -> <-o>.mems / stdout: NAME \t OFFSET \t LENGTH \t COUNT  (per MEM)
  --classify -> table; per read: NAME  STATUS(FOUND|NOT_PRESENT)  avg  above below
  --filter -> FASTA of kept reads (-v inverts)
"""
import hashlib
import os
import re
import subprocess

SEP = "%"
_ANSI = re.compile(r"\x1b\[[0-9;]*m")
# movi log lines to drop when scraping data from stdout
_LOG = re.compile(r"^\s*\[(INFO|WARN|ERROR|SUCCESS|PROGRESS)\]|Movi index version|"
                  r"All the move rows|Time measured|reads are processed|"
                  r"^\s*-\s*-\s*-|^(total_kmers|positive_skipped|backward_search|"
                  r"look_ahead|initialize_skipped|right_extension|Number of kmers|"
                  r"Sum of the counts):")

# ----------------------------------------------------------------------------
# reference cleaning + index-text construction (reproduce movi-prepare-ref)
# ----------------------------------------------------------------------------
_LC = {"a": "A", "c": "C", "g": "G", "t": "T"}
_UP = set("ACGT")


def clean_base(c):
    """Reproduce prepare_ref.cpp: switch uppercases lowercase acgt, then a guard
    on the ORIGINAL char rewrites anything not in uppercase {A,C,G,T} to 'A'.
    Net: uppercase ACGT preserved; everything else (incl. lowercase c/g/t, N,
    IUPAC, gaps) -> 'A' (only 'a' is coincidentally correct)."""
    buf = _LC.get(c, c)
    if c not in _UP:
        buf = "A"
    return buf


def clean_seq(s):
    return "".join(clean_base(c) for c in s)


_RC = str.maketrans("ACGT", "TGCA")


def revcomp(s):
    return s.translate(_RC)[::-1]


def build_index_text(records):
    """records: list of raw sequence strings (one per FASTA record / contig).
    Returns the cleaned, %-separated, fwd+RC concatenated index text, exactly as
    the separator build produces: for each record `FWD % RC %`."""
    out = []
    for r in records:
        c = clean_seq(r)
        out.append(c)
        out.append(SEP)
        out.append(revcomp(c))
        out.append(SEP)
    return "".join(out)


# ----------------------------------------------------------------------------
# brute-force oracle (exact for count / kmer-count)
# ----------------------------------------------------------------------------
def occ(text, s):
    """Overlapping occurrence count of s in text. s must be %-free (a match can
    never span a separator because s contains no %)."""
    if not s:
        return 0
    n = 0
    start = 0
    while True:
        i = text.find(s, start)
        if i < 0:
            return n
        n += 1
        start = i + 1


def oracle_count(text, q):
    """Movi --count semantics: (matched, count) where matched = length of the
    longest suffix of q that occurs in text, count = its occurrence count."""
    for L in range(len(q), 0, -1):
        c = occ(text, q[len(q) - L:])
        if c > 0:
            return L, c
    return 0, 0


def oracle_kmer_counts(text, q, k):
    """Per-kmer counts for every k-window of q (left-to-right). Returns list of
    (start_pos, count). A k-mer containing '%' cannot occur (returns 0)."""
    res = []
    for i in range(0, len(q) - k + 1):
        kmer = q[i:i + k]
        res.append((i, 0 if SEP in kmer else occ(text, kmer)))
    return res


# ----------------------------------------------------------------------------
# output parsers
# ----------------------------------------------------------------------------
def _data_lines(stdout):
    for ln in stdout.splitlines():
        ln = _ANSI.sub("", ln)
        if not ln.strip() or _LOG.search(ln):
            continue
        yield ln


def parse_count(stdout):
    """-> {name: (matched, length, count)}"""
    out = {}
    for ln in _data_lines(stdout):
        parts = ln.split("\t")
        if len(parts) >= 3 and "/" in parts[1]:
            m, L = parts[1].split("/")
            out[parts[0]] = (int(m), int(L), int(parts[2]))
    return out


def parse_pml(stdout):
    """-> {name: [ints]}   (also handles --zml, same format)"""
    out = {}
    name = None
    for ln in _data_lines(stdout):
        if ln.startswith(">"):
            name = ln[1:].strip()
            out[name] = []
        elif name is not None:
            out[name].extend(int(x) for x in ln.split())
    return out


parse_zml = parse_pml


def parse_kmer_count(stdout):
    """mphf format -> {name: {'sum':S,'nkmers':N,'per':[(pos,count),...]}}"""
    out = {}
    for ln in _data_lines(stdout):
        parts = ln.split("\t")
        if len(parts) >= 2 and "/" in parts[1]:
            s, n = parts[1].split("/")
            per = []
            if len(parts) >= 3:
                for tok in parts[2].split():
                    if ":" in tok:
                        p, c = tok.split(":")
                        per.append((int(p), int(c)))
            out[parts[0]] = {"sum": int(s), "nkmers": int(n), "per": per}
    return out


def parse_mem(text):
    """MEM file/stdout -> {name: [(offset,length,count),...]}"""
    out = {}
    for ln in _data_lines(text):
        parts = ln.split("\t")
        if len(parts) >= 4:
            try:
                out.setdefault(parts[0], []).append(
                    (int(parts[1]), int(parts[2]), int(parts[3])))
            except ValueError:
                pass
    return out


def parse_classify(stdout):
    """-> {name: status}  (FOUND / NOT_PRESENT)"""
    out = {}
    for ln in _data_lines(stdout):
        if ln.lower().startswith("read id"):
            continue
        parts = ln.split()
        if len(parts) >= 2 and parts[1] in ("FOUND", "NOT_PRESENT"):
            out[parts[0]] = parts[1]
    return out


def parse_filter(stdout):
    """-> set of kept read names (FASTA headers)"""
    kept = set()
    for ln in stdout.splitlines():
        ln = _ANSI.sub("", ln)
        if ln.startswith(">"):
            kept.add(ln[1:].strip().split()[0])
    return kept


# ----------------------------------------------------------------------------
# movi runner + helpers
# ----------------------------------------------------------------------------
def write_fasta(path, reads):
    """reads: list of (name, seq)."""
    with open(path, "w") as fh:
        for name, seq in reads:
            fh.write(">%s\n%s\n" % (name, seq))
    return path


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s):
    return hashlib.sha256(s.encode()).hexdigest()


def run_movi(movi, index, reads_fa, mode_args, out_prefix=None, extra=None,
             timeout=1800):
    """Run `movi query <mode_args> -i index -r reads_fa [--stdout|-o out]`.
    Returns (returncode, stdout_text, mems_text_or_None). mode_args is a list
    like ['--count'] or ['--mem','--min-mem-length','6','--ftab-k','12']."""
    cmd = [movi, "query"] + list(mode_args) + ["-i", index, "-r", reads_fa]
    mems = None
    if out_prefix is not None:
        cmd += ["-o", out_prefix]
    else:
        cmd += ["--stdout"]
    if extra:
        cmd += list(extra)
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if out_prefix is not None:
        mp = out_prefix + ".mems"
        if os.path.exists(mp):
            with open(mp) as fh:
                mems = fh.read()
    return p.returncode, p.stdout + p.stderr, mems, " ".join(cmd)
