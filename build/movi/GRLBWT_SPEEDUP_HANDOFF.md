# Handoff: speed up grlBWT for pangenome-scale inputs

**Audience:** a developer picking up grlBWT performance work for the Movi build pipeline
(`aws-indexes build/movi/snakemake`). Self-contained. There is a deliberate
**"profile first, then start small"** ladder in §5 — you do not have to solve it all at
once. grlBWT upstream is `github.com/ddiazdom/grlBWT` (Díaz-Domínguez & Navarro); our
checkout is `~/git/grlBWT` @ `c93306a` (already carries a BenLangmead include-fix PR).

---

## 1. One-sentence problem

grlBWT is now the **single longest step** in the Movi build pipeline — ~4.6 days for
HPRC-yr2 and ~5 days projected for OpenHGL — and its cost is concentrated in **two
per-round phases that run at ~20 MB/s**, far below what the CPU or disk can sustain, so
there is large headroom.

## 2. Why this matters (the cost, now that TeraLCP is parallel)

With the TeraLCP construct now parallelized and the thresholds fixed, the pipeline's time
budget is roughly: **grlBWT ~4.6–5 d**, construct A/B/C ~1.8 d, thresholds ~0.5 d,
movi_build+ftab ~few h. grlBWT is ~60% of the wall clock and the #1 target. A 2–3× grlBWT
speedup shaves ~3 days off every pangenome build.

## 3. Where the time actually goes (measured, HPRC-yr2, n = 2.84e12)

From the captured grlBWT log (per-phase timers it prints itself). Two sub-phases per
parsing round dominate; everything else is minutes:

| round | Computing the dictionary of LMS phrases | Creating the parse of the text | round total | parse size out |
|------:|----------------------------------------:|-------------------------------:|------------:|---------------:|
| 1     | **16:34:14**                            | **22:57:26**                   | 39:40:38    | 792 GB |
| 2     | **27:19:20**                            | **19:43:03**                   | 47:20:28    | 247 GB |
| 3     | 7:47:07                                 | …                              | …           | … |

- Rounds 1–2 alone are **~87 h (~3.6 days)**; 7 rounds total → ~4.6 d.
- The cheap sub-phases (compacting, sorting+preliminary BWT, compressing, assigning
  metasymbols) are **seconds to a few minutes** each — ignore them.
- **Effective throughput of round 1 ≈ 2.84 TB / 40 h ≈ 20 MB/s.** That is ~50–100× below
  local NVMe bandwidth and far below 48-core hashing throughput, so the phase is **neither
  disk- nor CPU-saturated** as currently run.
- **Tell-tale clue:** round 2's dictionary phase (27 h) is *longer* than round 1's (16.5 h)
  despite operating on a 3.6× smaller input (792 GB vs 2.84 TB). Cost tracks the **number of
  distinct LMS phrases and the hash-table access pattern**, not raw bytes — i.e. it smells
  **memory-latency-bound on a large hash table with poor locality**, not throughput-bound.

## 4. Environment levers we are not using

`grlbwt-cli` options: `-t` threads, `-f` hbuff (hashing uses ≤ INPUT_SIZE·f bytes; def 0.5),
`-b` run-len-bytes (def 1), `-T` temp dir, `-a` alphabet. Our Snakemake `grlbwt` rule runs
`grlbwt-cli grl_in.txt -o WORK/grl_out -t {threads} -T WORK/grltmp`, with **`WORK` on VAST
(networked GPFS)**.

**devlangmead1 has fast local storage grlBWT never touches:**
- `/tmp` = **1.8 TB local NVMe** (xfs, non-rotational), ~1.7 TB free.
- `/dev/shm` = **756 GB tmpfs** (RAM-backed).
- grlBWT's `-T` currently points at **/vast** (networked). If any of those long phases are
  even partly small-random-I/O on temp files, moving `-T` to local NVMe is a big, zero-code win.

## 5. The ladder — profile first, then start small

**Rung 0 — profile one round to classify the bottleneck (do this before anything else).**
Attach to a live "Computing the dictionary of LMS phrases" / "Creating the parse" phase (the
current OpenHGL run will enter them) and answer three questions:
- **CPU-bound?** `ps -L`/`top -H` on the grlbwt-cli pid: how many threads are R at once? If ~1–few
  of 32, the phase is under-parallelized. `perf stat -p <pid> sleep 30` → IPC and
  `cache-misses`; low IPC + high LLC misses ⇒ memory-latency-bound (matches the §3 clue).
- **I/O-bound?** `iostat -x 5` (or `pidstat -d`): is nvme/vast busy? Is the phase reading/writing
  temp at MB/s (small random) vs GB/s (streaming)? Compare temp traffic on /vast.
- **Where in the code?** `perf record -p <pid> -g sleep 60; perf report` → the hot function in
  `lib/`/`include/grl_bwt.hpp` (LMS-phrase hashing vs parse emission).
This single measurement decides Rung 1 vs Rung 2 vs Rung 3.

**Rung 1 — quick, no code changes (try today, on a medium input).**
- **Local-NVMe temp:** run with `-T /tmp/grltmp` (local NVMe) instead of VAST and time the same
  input. Caveat: check grlBWT's peak temp first (yr1 peaked ~371 GB; yr2 parse files reach ~792 GB
  — may exceed /tmp's 1.7 TB for OpenHGL, so validate headroom or use it only for ≤ yr2 scale).
  `/dev/shm` (756 GB tmpfs) is even faster but smaller.
- **Hash buffer `-f`:** the node has 1.5 TB RAM; sweep `-f` (e.g. 0.5 → 1.0) and measure whether the
  dictionary phase speeds up (bigger in-RAM hash working set = fewer spills/passes).
- **Threads `-t`:** confirm the *dominant* phases actually scale with `-t` (measure at `-t` 8/16/32).
  If they don't, that's the Rung-2 signal.
Each is independently valuable; keep whichever helps and note the delta.

**Rung 2 — parallelize the dominant phases (if Rung 0 says under-parallelized).**
"Computing the dictionary of LMS phrases" and "Creating the parse" are, in the prefix-free-parsing
sense, **embarrassingly parallel over text chunks** (hash phrases per chunk into shard-local tables,
then merge; emit the parse per chunk with a shared phrase→metasymbol map). If grlBWT does these
serially or with a global lock, shard them across `-t` threads with per-thread hash shards and a
deterministic merge. Validate **bit-identical `grl_out.rl_bwt`** vs the serial build on a fixture.

**Rung 3 — attack memory latency (if Rung 0 says latency-bound, per the §3 clue).**
The dictionary hashing is the suspect. Options, cheapest first: a more cache-friendly hash
(open-addressing + prefetch, or a radix/partitioned hash so each partition fits in LLC), reduce
per-entry footprint, or process phrases in a locality-preserving order. Re-measure IPC/LLC-miss.

**Rung 4 — scale test + production.** Confirm ~linear or better on a 10–40-haplotype subset (build its
`grl_in.txt` via the Snakemake pipeline), then rerun a full pangenome grlBWT and compare wall clock +
verify the RLBWT is byte-identical to the reference build.

## 6. Where everything is

| thing | location |
|---|---|
| grlBWT source | `~/git/grlBWT` (@ `c93306a`; `main.cpp`, `include/grl_bwt.hpp`, `lib/`, `scripts/`) |
| upstream | `github.com/ddiazdom/grlBWT` |
| binary | `~/git/grlBWT/build/grlbwt-cli` (built via cmake) |
| how we invoke it | `aws-indexes build/movi/snakemake/Snakefile`, rule `grlbwt` (`-t {threads} -T WORK/grltmp`), sized in `config.*.yaml` `res.grlbwt` |
| self-printed per-phase timers | grlbwt-cli prints "Parsing round k / … / Elapsed time" to stdout — captured in the run log; this is your built-in profiler |
| medium test input | build a 10–40-hap subset's `grl_in.txt` (config `haplotypes:` a sample list), or reuse `/scratch16/blangme2/movi-work/hprc-yr1` intermediates |
| baselines | yr1: 16h42m / 84 GiB RAM / 371 GB temp / 573 GB input. yr2: ~4.6 d / ~397 GiB RAM / 2.84 TB input / 7 rounds (see §3). OpenHGL: ~5 d / 3.5 TB input (running now) |
| downstream (unaffected) | `grlbwt2rle` → `grlbwt2teralcp` adapter → TeraLCP; do not change the RLBWT bytes |

## 7. Gotchas

- **Correctness is the RLBWT bytes.** The only acceptance test is that `grl_out.rl_bwt` (hence
  `grl.bwt.heads`/`.len`) is unchanged; the downstream TeraLCP/Movi index depends on it exactly.
- **Temp sizing.** grlBWT's peak temp can approach the largest parse (yr2 round-1 parse = 792 GB);
  a local-NVMe `-T` must have headroom, or fall back to VAST for the biggest rounds only.
- **Repetitiveness is the point.** grlBWT is designed for repetitive text; our %-separated,
  reverse-complemented pangenome is extremely repetitive, which is why the dictionary phase (distinct
  phrases) — not raw size — dominates. Optimizations should assume high repetition.
- **Don't regress memory.** RAM peaked ~397 GiB (yr2) under the 1.5 TB node; a faster hash must not
  blow that.

## 8. Definition of done

The two dominant per-round phases run at a rate consistent with the machine's real limit
(CPU-saturated if compute-bound, or local-NVMe bandwidth if I/O-bound) rather than ~20 MB/s;
a full pangenome grlBWT drops from ~4.6 days toward ~1.5–2 days; and `grl_out.rl_bwt` is
byte-identical to the reference build.
