# Handoff: a CDK workflow to build **Movi indexes** from pangenome collections

**Audience:** a fresh agent (cold context) picking up Movi-index-building work in the
`~/git/aws-indexes` repo. This document is self-contained — read it top to bottom
before touching anything. It captures the goal, the upstream facts already proven
elsewhere, where everything lives, the template to clone, and the design decisions
still open.

**Status:** greenfield. No `build/movi/` stack exists yet (this `HANDOFF.md` is the
first file in it). The upstream science/tooling (TeraLCP thresholds → Movi) is
validated; what remains is the AWS orchestration.

> **Update (2026-06-15): a Slurm workflow now exists** — see [`README.md`](README.md),
> `submit.sh`, and `movi_build.slurm`. It runs the grlBWT separator path end-to-end
> through `movi build` on Rockfish via `sbatch`, using the prebuilt binaries on shared
> `/home` (no in-job compile). Piloted on `TeraTools-pr/test/shred1_mini/…` with
> `--validate-full`: **`--count` byte-identical to a stock-pfp `--separators` index.**
> **AGC ingestion is wired and verified** (both `getcol` all-samples and `getset`
> `--haplotypes` subset) on a tiny AGC fixture, same validation. Real archives:
> `/data/blangme2/fasta/*/*.agc`. Still open: EC2/CDK port, S3 publish + catalog row,
> N policy, and a real full-pangenome run (bigmem). The §5–§8 CDK plan below remains the
> reference for the EC2 variant.

---

## 1. The ultimate goal

Make it turnkey to point at a new pangenome collection — **AGC files + haplotype
names, or FASTA** — and say *"build me a Movi index of that."* The system should
cheaply produce a Movi index that answers **all** of Movi's query modes (PML, count,
MEM, k-mer, ZML), then publish it to the **Index Zone** bucket and list it in the
catalog at <https://benlangmead.github.io/aws-indexes/movi>.

This replaces the older PFP-based path (`pfp-thresholds`) with a faster, compressed-
space path that separates **RLBWT construction** (swappable algorithm) from
**threshold computation** (TeraLCP).

## 2. Target pipeline

```
 AGC / FASTA
     │   (AGC: decompress haplotypes by name → FASTA)
     ▼
 [1] RLBWT construction          ← swappable: ropeBWT3 | grlBWT | (lyndon-grammar, TBD)
     ▼
 [2] TeraLCP -othresholds        ← emits .thr/.thr_pos + .bwt.heads/.bwt.len
     ▼
 [3] movi build --preprocessed   ← consumes heads/len + thresholds → Movi index
     --skip-prepare --skip-pfp
     ▼
 [4] upload index + provenance → s3://genome-idx/movi/<collection>/YYYYMMDD/
     ▼
 [5] add an entry to the aws-indexes catalog (Movi page)
```

Steps 1–3 are **proven end-to-end** (see §3). The CDK job's novelty vs the existing
`build/tera` stack is that it runs the **full chain through `movi build`** and
publishes a *finished Movi index*, starting from FASTA/AGC rather than a pre-built FMD.

## 3. What is already proven (trust these — do not re-derive)

Validated on **devlangmead1** (JHU Rockfish dev node) against stock pfp/Movi. Source
of truth: `~/git/TeraTools-langmead` (branch `movi-validation`) and its
`test/validate_against_movi.sh`, `test/MOVI_QUERY_MODES.md`.

- **TeraLCP thresholds == pfp-thresholds, byte-identical.** `TeraLCP -othresholds`
  writes `.thr`/`.thr_pos` (5-byte LE) + `.bwt.heads`/`.bwt.len`, parallel to BWT runs.
- **Two RLBWT paths, both validated through a real Movi query:**
  - **No separators (ropeBWT3):** `ropebwt3 build -R -d -o x.fmd` → `TeraLCP -f fmd`
    → `movi build`. `movi query --pml` byte-identical to a stock `movi build` (pfp)
    index. ropeBWT3 **cannot** emit a distinct separator/terminator (no alphabet room).
  - **Separators (grlBWT):** `grlbwt-cli` → `grlbwt2rle` → **`grlbwt2teralcp` adapter**
    → `TeraLCP -f rlbwt` → `movi build --separators`. `movi query --count` identical
    to stock (incl. multi-occurrence counts).
- **`grlbwt2teralcp` adapter exists** (TeraTools `src/TeraLCP/tools/grlbwt2teralcp.cpp`,
  built by the TeraLCP Makefile): reads grlBWT `.syms`(1B/run)+`.len`(4B/run) → writes
  `.bwt.heads`(1B/run)+`.bwt.len`(5B/run LE). Default = faithful widen; `--movi-sentinel`
  also remaps the grlBWT newline sentinel `0x0a`→`0x00` (needed only for the `movi build`
  input, not for `-f rlbwt`).
- **Movi query modes & what exercises what** (from `test/MOVI_QUERY_MODES.md`):
  - `--pml` (default), `--zml`, `--count`, `--mem` (`-l`), `--kmer`/`--kmer-count`
    (`-k`), `--classify`, `--filter`.
  - **Bidirectional search is not a separate flag** — it is the *engine* behind `--mem`
    and `--kmer`/`--kmer-count`. Testing those covers bidirectional. They require the
    **ftab** (build with `--ftab-k K`; `--mem` also needs `--ftab-k K` repeated at query
    time — see filed Movi issue #2) and require the **reverse complement present** in the
    index (added by the prepare step / `ropebwt3 -R`).
- **N / non-ACGT handling** (relevant to fidelity of published indexes):
  - `movi-prepare-ref` silently maps **every non-ACGT byte → `A`** (all IUPAC ambiguity
    codes, not just N); no flag, no warning. Because the Tera path *owns* RLBWT
    construction, we can choose a better policy upstream (e.g. split contigs at N runs
    and separate with `%`) instead of inheriting this.
  - `--kmer`/`--kmer-count` **silently emit nothing** on read files containing N unless
    `--ignore-illegal-chars {1→A,2→random}` is passed. For a turnkey product, set a sane
    default for k-mer mode.
  - These are **Movi-side**, filed as issues on the fork `BenLangmead/Movi`
    (#1 = `--kmer` N silence, #2 = `--mem` ftab-k re-spec). They do **not** affect index
    construction fidelity (Tera and stock pfp produce identical indexes).

## 4. Where everything lives

| Thing | Location |
|---|---|
| This repo | `~/git/aws-indexes` (origin `git@github.com:BenLangmead/aws-indexes`, branch **`master`**) |
| Existing CDK stacks | `build/{bowtie,tera,pfp_thresh_builder,moni-align}` |
| **Closest template** | **`build/tera`** (spot instance + RAID-0 NVMe + build TeraTools + run TeraLCP→thresholds + resource capture + S3 upload; already uploads to `s3://genome-idx/movi/...`) |
| Old PFP precedent + lessons | `build/pfp_thresh_builder/{README.md,ISSUES.md}` |
| Instance/cost shopping | repo root: `instance_shopper.py`, `spot_shopper.py`, `instances_20260123.csv` |
| AWS auth notes | `AWS.md` (profiles: `data-langmead`, `index-zone-s3`, `index-zone-ec2`; account `159168350739`) |
| TeraTools (upstream science) | `~/git/TeraTools-langmead`; branch `movi-validation` (validation work) vs pristine PR branch `movi-thresholds` (commits C1–C4, target `ucfcbb/TeraTools`). See its `PR_HANDOFF.md`. |
| Movi fork | `github.com/BenLangmead/Movi` (fork of `mohsenzakeri/Movi`); issues #1,#2[,#3] filed there |
| Build/validation host | **devlangmead1** via the **`rockfish` skill**; dirs: `~/git/TeraTools-pr`, `~/git/movi-langmead` (`build/movi`, `build/bin/movi-prepare-ref`), `~/git/grlBWT/build` |
| Index Zone bucket | **`s3://genome-idx`** (canonical; the user sometimes writes "s3://genome.idx" — same place). Movi prefix convention: `s3://genome-idx/movi/<collection>/YYYYMMDD/` |
| Catalog site | <https://benlangmead.github.io/aws-indexes/movi> (GitHub Pages from `docs/`) |

> ✅ **Clone-able ref (resolved):** the TeraTools validation work (the
> `grlbwt2teralcp.cpp` adapter, `test/corner/`, `test/MOVI_QUERY_MODES.md`, reproducer
> edits) is committed as **`dab9398`** on branch **`movi-validation`**, pushed to
> `origin` (`github.com/BenLangmead/TeraTools`). **The CDK job should pin its clone to
> commit `dab9398`** (or a tag cut from it), not the branch name — branches move/get
> deleted. This branch sits on top of the pristine PR commits C1–C4, so it carries the
> full threshold feature plus the adapter. Build it with `make -C src/TeraLCP` (the
> `tools` target builds `grlbwt2teralcp`; no SDSL link needed for the adapter itself).
> Still open (non-blocking, the user's call): whether this work eventually folds into
> the upstream PR as a follow-up commit or stays a separate tooling branch.

## 5. The template to clone: `build/tera`

`build/tera` already implements the hard parts. Read `build/tera/README.md` and
`build/tera/tera_stack/tera_stack.py` (472 lines) first. Reusable as-is:

- **Stack shape:** `app.py` reads `config.json`, picks `instance_type[instance_profile]`
  (region/AZ/type/spot_price), builds one `CfnInstance` from a spot Launch Template on
  the latest AL2023 AMI (arch mapped arm64/x86_64 by instance type), exports KeyPairId +
  public IP. `deploy.sh` = `cdk bootstrap/synth/deploy` then pulls the SSH key from SSM.
- **Storage:** first-boot user data discovers whole-disk NVMe (`/dev/nvme*n1`, skips EBS
  root via `lsblk`), RAID-0 stripes them, mounts at `/data`. All job data + temp live on
  `/data`.
- **Credentials without reading them:** local AWS creds are embedded into user data for
  the final `aws s3` upload — follow the existing pattern; never cat/print them.
- **Measurement harness:** `psrecord` time-series + `/usr/bin/time -v` (peak RSS / virt)
  + a background disk sampler → a single `summary.txt` (wall clock, peak disk, peak RSS,
  peak virt) plus `os_info.txt`, tool `--version`s, and a `*.tar.gz` of the build dir.
- **S3 layout:** `output/`, `logs/`, tarball under `…/YYYYMMDD/`.

**What to add for Movi** (the delta from `build/tera`):
1. **Input acquisition:** accept FASTA, a list of FASTAs, or **AGC** (decompress named
   haplotypes → FASTA). New vs `tera`, which starts from a pre-built `.fmd`.
2. **RLBWT step:** build + run the chosen constructor (ropeBWT3 and/or grlBWT) on the
   instance. grlBWT needs SDSL (see TeraTools `PR_HANDOFF.md` for its cmake flags).
3. **Adapter + TeraLCP:** for the grlBWT path, run `grlbwt2teralcp` then `TeraLCP -f rlbwt
   -othresholds`; for ropeBWT3, `TeraLCP -f fmd -othresholds`.
4. **`movi build`:** clone/build Movi (fork `BenLangmead/Movi`), then
   `movi build --preprocessed --skip-prepare --skip-pfp [--separators] --ftab-k K …`
   to produce the finished index. Decide ftab-k default(s).
5. **Validate before publish:** run a quick `movi query` smoke test (at least `--pml`
   and, for separator indexes, `--count`) on a few reads derived from the input, and
   record it in `summary.txt`.
6. **Publish + catalog:** upload the Movi index dir; add a row to the catalog
   (`docs/` Movi page) with size, modes supported, and the `s3://` + `https://` URLs.

## 6. Design-space decisions to work through

The user explicitly wants the *"best"* workflow mapped out, where "best" is **not**
simply fastest — higher memory/disk drives more expensive instance classes (EC2 high-mem
/ Slurm `bigmem`), which may or may not be worth the time saved. Sequencing preference
(stated earlier): **correctness first** (largely done in TeraTools), then **build the
benchmark harness and run a small pilot** (not a full sweep) before committing.

Decisions to resolve, with data:

1. **RLBWT constructor choice.** ropeBWT3 (fast, DNA-only, **no separators**) vs grlBWT
   (byte-alphabet, **supports separators/terminators**) vs lyndon-grammar (uncharacterized
   — benchmark or drop). **Key constraint:** `--count` and document-aware queries need
   separators ⇒ if the published index must feed *all* Movi modes, the **grlBWT
   (separator) path is the default**; ropeBWT3 is the no-separator special case.
2. **Cost vs footprint.** Profile each path's wall-clock, peak RAM, peak disk on
   representative inputs. Map onto (a) **Rockfish** Slurm (`bigmem` queue when RAM-bound;
   use the `rockfish` skill) and (b) **EC2 spot** (memory-optimized: `x2idn`, `x2iedn`,
   `r8gd`, `r6gd.metal` — see `AWS.md` / shoppers). Build a small table: tool × input
   size → (time, RAM, disk, $ on cheapest viable spot type).
3. **Instance selection inputs.** `instance_shopper.py` / `spot_shopper.py` +
   `instances_*.csv`. Prefer instances with **instance-store NVMe** (the RAID-0 `/data`
   pattern) and arch-appropriate AMIs. Reuse `tera`'s `config.json` profile scheme.
4. **AGC ingestion.** Confirm the AGC CLI, how haplotype names are listed/selected, and
   whether decompression happens on-instance or is pre-staged to S3.
5. **N policy** (see §3). Decide the published-index convention (recommended: split at N
   runs with `%` separators rather than silent →A) and the k-mer query default.

## 7. Gotchas (consolidated from `pfp_thresh_builder/ISSUES.md` + `tera` design notes)

- Package is **`gcc-c++`**, not `g++`, on AL2023. Install: `dnf install -y make gcc
  gcc-c++ git zlib-devel cmake`.
- Build user-data command lists with **`'\n'.join()`**, never `' '.join()` (heredoc
  delimiters must be on their own line, or the job silently no-ops).
- **Spot prices are strings** in `config.json` (CDK `max_price` is `Optional[str]`;
  floats serialize wrong).
- **Pin external clones to a commit/tag**, not a feature branch (branches get deleted).
  Relevant for TeraTools (`movi-validation`/PR branch) and the Movi fork.
- A spot bid far below on-demand means the instance **silently never launches** — verify
  current spot price *and* regional availability of exotic families (`x2iedn`, etc.).
- `git submodule update --init --recursive` after cloning TeraTools.
- Confirm **NVMe instance store** actually exists on the chosen type, else `/data` lands
  tiny on the EBS root.

## 8. Concrete first steps for the new agent

1. Read `build/tera/README.md`, `build/tera/tera_stack/tera_stack.py`,
   `build/pfp_thresh_builder/ISSUES.md`, and `AWS.md`.
2. Clone TeraTools at the pinned ref **`dab9398`** (branch `movi-validation`) and
   `make -C src/TeraLCP` to get `TeraLCP` + `tools/grlbwt2teralcp` (see §4).
3. Decide the **pilot**: one small collection (e.g. a handful of HPRC haplotypes or the
   `human579`-style OpenHGL subset) through the **grlBWT separator path** end-to-end to a
   finished, query-validated Movi index — on **devlangmead1 first** (cheap, no spot), then
   port to a `build/movi/` CDK stack cloned from `build/tera`.
4. Stand up `build/movi/` (mirror `tera`'s files: `app.py`, `config.json`, `deploy.sh`,
   `movi_stack/movi_stack.py`, `README.md`) and run the pilot on spot.
5. Record the §6 cost/footprint table from the pilot to inform constructor + instance
   defaults before any larger run.

## 9. Cross-references

- TeraTools: `~/git/TeraTools-langmead/PR_HANDOFF.md`, `test/MOVI_QUERY_MODES.md`,
  `test/validate_against_movi.sh`, `test/corner/run_corner_tests.sh`,
  `src/TeraLCP/tools/grlbwt2teralcp.cpp`.
- Plan that produced the validation work:
  `~/.claude/plans/floating-baking-frost.md`.
- Movi fork issues: <https://github.com/BenLangmead/Movi/issues>.
