# Movi query-mode behavior findings (empirical) — basis for the corner-case test harness

Captured 2026-07-09 by probing a tiny synthetic `--separators` index built with
`/home/blangme2/git/movi-wide/build/movi` (movi-wide @0851cc0, binary
`sha256 45e337ea92881e0c8ed78c5ed561c523a67da7dd31fcc39acb7815032890cdce`). These are the
exact formats/behaviors the T1/T2 assertions must encode. Verify against production during T1.

## Binary: use `mphf` (latest-greatest), NOT `wide-thresholds`, for querying/testing
Branch investigation (2026-07-09): the indexes were BUILT with `wide-thresholds` (needed for its
`read_thresholds` >2^40 fix — build-time only). But `wide-thresholds` is a **separate lineage** that
shares only the Nov-2025 `develop` base with the recent query work and contains **none** of it. The
query improvements are stacked in **`mphf`** (BenLangmead/Movi @34ab5a3), which contains
`efficiency_fixes` + `kmer_improvements` + `mem_improvements` + `kmer_bv` + `pml_coro_efficiency`.
NOT in mphf: `fix-kmer-count`, `coroutine` (older), `wide-thresholds`, `lh_kmers_mems_mph`.
**Decision (user): test/query with `mphf` as-is** (both `movi` and the coroutine `movi-co`, where the
improved MEM/k-mer queries live — this likely resolves the MEM empty-output open item). Querying a
finished `index.movi` does NOT need the wide-thresholds fix.
**Format-compat: VERIFIED 2026-07-09.** Built mphf on the cluster (worktree off movi-wide @ origin/mphf
`34ab5a3`; `mkdir build && cd build && cmake .. && make -j` — FetchContent pulls sdsl/zlib/hclust/pfp;
cluster clone must use the **https** origin, ssh clone of the private fork fails in non-interactive
shells). Binary: **`/home/blangme2/git/movi-mphf/build/movi`** (NOTE: `build/movi` is only the ~110 KB
launcher — its sha256 collides with wide-thresholds because the launcher source is unchanged; the real
per-mode query binaries in `build/` differ. Record identity as **commit `34ab5a3`**, not launcher sha).
Results:
- **Reads our `wide-thresholds`-built indexes** — same `index.movi` filename convention
  (`movi_launcher.cpp:410`), opened yr1 production `index.movi` (v2.0.0) and returned the *identical*
  count on the tiny index (`within 12/12 18`). No format drift. ✅
- **MEM now works** (was empty on wide-thresholds — it lacked `mem_improvements`). `movi query --mem
  --min-mem-length 6` → `.mems` file **and** stdout: `NAME\tOFFSET\tLENGTH\tCOUNT` (e.g. `whole 0 22 2`).
  There is **no separate `movi-co`** — coroutine k-mer/MEM folded into `movi query`.
- `--pml`/`--zml`/`--count`/`--classify`/`--filter` byte-stable vs wide-thresholds (pml `1 0 1 0 6 5 4
  3 2 1 0 0`; zml `11 10 …0`; classify FOUND/NOT_PRESENT).
- ⚠️ **`--kmer-count` format CHANGED** on mphf: `NAME\tSUM_OF_COUNTS/N_KMERS\t POS:COUNT…` (e.g.
  `within 140/5 …`) vs wide's `FOUND/TOTAL` (`5/5`). And **`fix-kmer-count` is NOT in mphf** — so
  per-kmer `--kmer-count` correctness fix is absent; parse mphf's format accordingly / flag if it matters.
- ⚠️ **`--mmap` fails** on mphf ("Failed to open index file") — use plain load.
**⇒ Use `movi-mphf` (commit `34ab5a3`) for the harness + witness; record that commit in the witness.**

## Reference source (IMPORTANT pivot)
`ref.fa` was **deleted from `/data` for hprc-yr2 and openhgl** (multi-TB, not needed to query
`index.movi`); only hprc-yr1 still has it. So fixtures are built from the **source .agc**, not ref.fa:
- agc binary: `/home/blangme2/bin/agc`
- archives: yr1 `/data/blangme2/fasta/hprc-yr1/HPRC-yr1.agc`, yr2 `/data/blangme2/fasta/hprc-v2/human472.agc` (3,354,049,236 B), openhgl `/data/blangme2/fasta/openHGL/human579.agc` (3,675,483,835 B).
- `agc getset <archive> <sample>` streams a haplotype's contigs; reproduce `movi-prepare-ref`
  cleaning in Python to get the exact indexed sequence: **every non-ACGT → `A`** (N, IUPAC, `-`,
  digits), and **lowercase `c/g/t` → `A` too** (only `a`→A coincidental). Layout per input record in
  the index text: `FWD % RC %` (a `%` after every contig AND at every fwd/RC junction).

## Query modes / flags (movi query)
- `--pml` (default) · `--zml` · `--count` · `--kmer` / `--kmer-count` with `-k/--k-length` (and
  `--output-format movi|kmc|sshash`, `--kmer-bv`) · `--mem` with `--min-mem-length` + `--ftab-k` ·
  `--classify` · `--filter` (+ `-v/--invert`) · `--stdout` · `--ignore-illegal-chars {1,2}` · `--mmap`
  (memory-map, avoids loading 40–50 GB into RAM — use for production T1) · `--multi-ftab`.
- **MEM min length is `--min-mem-length` (long form).** `-l 5` did NOT override the default 25 in
  this build (WARN still said "minimum MEM (length 25)"); the long form parses correctly.

## Output formats (exact)
- **`--count --stdout`**: `NAME\tMATCHED/LEN\tCOUNT`. Within-record 12-mer → `within  12/12  18`
  (full match, 18 occurrences across dups+RC). Boundary-spanning 12-mer → `span  6/12  2` (**partial**
  — only the 6-char suffix matched). ⇒ **separator assertion: spanning query gives MATCHED < LEN;
  within-record positive gives MATCHED == LEN.** COUNT is the count of the longest-matching suffix.
- **`--pml --stdout`**: `>NAME` then space-separated per-position values. Illegal char (`N`, `%`,
  lowercase) → value `0` at that position and the match breaks (e.g. `... 1 0 [0 0 0 0] 6 5 ...`
  across an `NNNN` run). `--ignore-illegal-chars 1` rewrites the illegal char to `A` and the match
  extends through it (verified). **PML is a *pseudo* statistic — a whole 22 bp record maxed at 17,
  not 22 — so do NOT assert `PML == len`; use `--count` MATCHED==LEN for the positive control.**
- **`--kmer-count --stdout -k K`**: `NAME\tFOUND/TOTAL\t POS:COUNT …` + a stats block. Boundary read
  → `span  0/5` (no K-mer exists across the join). ⇒ **k-mer separator assertion: FOUND == 0** for a
  boundary-spanning read; > 0 for a within-record read.
- **`--kmer -k K` with `N` in the read did NOT abort** (exit 0; found the N-free k-mers). Assert it
  runs, not that it aborts.
- **`--classify --stdout`**: table with `status:` column = `FOUND` (positive) vs `NOT_PRESENT`
  (negative/null). ⇒ assert positive→FOUND, null→NOT_PRESENT.
- **`--filter`**: emits the matching reads as FASTA to stdout (kept `pos`, dropped `neg`); `-v`
  inverts. ⇒ assert positives kept / negatives dropped, and the inverse with `-v`.
- **`--mem`**: writes `<-o_prefix>.mems` (NOT stdout in this build). **OPEN ITEM:** on the tiny index
  it produced a 0-byte `.mems` even for a fully-matching read at `--min-mem-length 6` — likely a
  tiny-index/ftab-k artifact. **Resolve MEM output format + a producing invocation on a PRODUCTION
  index during T1** (real ftab-k 12, long reads) before trusting a MEM assertion; until then record
  MEM output as-is and flag if empty.

## Assertion mapping (updated from these findings)
- Separator / boundary: `--count` MATCHED<LEN (robust; immune to coincidental occurrence) **and**
  `--kmer-count` FOUND==0; plus **MR1** (pml profile of `A·B` over B == profile of B alone).
- Positive control (MR3): `--count` MATCHED==LEN and COUNT≥1 (NOT pml).
- RC symmetry (MR2): `count(S)==count(RC(S))` — **pick a non-self-RC segment** (ACGT-repeats are
  self-RC; avoid them).
- Illegal chars: pml shows `0` at the N/`%`/lowercase position (default); `--ignore-illegal-chars 1`
  changes it → assert the difference.
- classify FOUND/NOT_PRESENT; filter keep/drop (+`-v`).

## Gotchas
- FASTA reads must have clean multi-char record names; some ad-hoc `>d`/`>f` probes hit
  `Error: header line is missing an id` — generate validated FASTA in the harness.
- Query files for `--kmer`/`--mem` should be ACGT-only where a clean count is wanted (N breaks/kmer-
  skips). Case #15 (N in `--kmer`) intentionally tests the tolerate-N behavior.
- Use `--mmap` for production T1 to avoid resident 40–50 GB per query.
