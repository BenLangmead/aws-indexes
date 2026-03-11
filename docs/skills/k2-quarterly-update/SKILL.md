---
name: k2-quarterly-update
description: >-
  Updates and sanity-checks docs/k2.md for quarterly Kraken 2/Bracken index
  releases. Use when doing a quarterly k2 index update, updating k2.md for a new
  release, or when the user asks to update or check the k2 documentation.
---

# Quarterly update and sanity-check of k2.md

This skill documents how to update `docs/k2.md` for a new quarterly Kraken 2 / Bracken Refseq index release and how to run sanity checks so the same process can be repeated each quarter.

## Key files

| File | Purpose |
|------|---------|
| `docs/k2.md` | Main document to edit (Latest table, Older table, link definitions). |
| `docs/check_k2_links.py` | Link checker: run after edits; exits 0 if all `https://` URLs in k2.md are accessible. |
| `xfer/kraken/k2_sizes_for_table.py` | Source of truth for the **list of Refseq collections** and their **date**; can be used to fetch archive/index sizes from S3 (update `dates` in script to new ref date, then run from repo root). |

## Refseq collections (order in table)

The 11 Refseq collections that are updated quarterly, in table order:

1. Viral  
2. MinusB  
3. Standard  
4. Standard-8  
5. Standard-16  
6. PlusPF  
7. PlusPF-8  
8. PlusPF-16  
9. PlusPFP  
10. PlusPFP-8  
11. PlusPFP-16  

In `k2_sizes_for_table.py` the internal names are: `viral`, `minusb`, `standard`, `standard_08_GB`, `standard_16_GB`, `pluspf`, `pluspf_08_GB`, `pluspf_16_GB`, `pluspfp`, `pluspfp_08_GB`, `pluspfp_16_GB`. S3 paths use `08_GB` / `16_GB` (newer); older releases (e.g. April 2025 and before) may use `08gb` / `16gb` in paths—keep that convention when adding Older link defs.

**Latest table only:** EuPathDB46, core_nt Database, and GTDB are not part of the quarterly 11; update them separately when those indexes are released.

---

## Step 1: Add the new release to “Latest”

1. **Heading**  
   Update the “Latest” subheading (e.g. `### Latest: February 2026 update`) to the new release (e.g. `### Latest: May 2026 update`).

2. **Table rows (11 Refseq collections)**  
   For each of the 11 Refseq collections, update:
   - **Date** to the new release date (e.g. `5/15/2026`).
   - **Archive size (GB)** and **Index size (GB)** from build output or from running `xfer/kraken/k2_sizes_for_table.py` (after setting the new date in that script). Use one decimal place.
   - **Link references** to the new ref date (e.g. `20260515`):  
     `[.tar.gz][k2_viral_20260515]`, `[.txt][k2_viral_20260515_inspect]`, `[.tsv][k2_viral_20260515_library]`, `[.md5][k2_viral_20260515_md5]` (and similarly for minusb, standard, standard_8, standard_16, pluspf, pluspf_8, pluspf_16, pluspfp, pluspfp_8, pluspfp_16).  
   Use the same ref suffix for all four link types (tar.gz, inspect, library, md5) per collection.

3. **Link definitions for the new release**  
   Add definitions for the new ref date (e.g. `20260515`) in the same block where existing Latest refs are defined (above “# KrakenUniq indexes”):
   - **Tar.gz:** `[k2_<name>_<ref>]: https://genome-idx.s3.amazonaws.com/kraken/k2_<s3name>_<ref>.tar.gz`  
     Table names map to S3 names as in the script (e.g. Standard-8 → `standard_08_GB`, Standard-16 → `standard_16_GB`).
   - **Inspect:** `[k2_<name>_<ref>_inspect]: https://genome-idx.s3.amazonaws.com/kraken/<s3name>_<ref>/inspect.txt`
   - **Library:** `[k2_<name>_<ref>_library]: https://genome-idx.s3.amazonaws.com/kraken/<s3name>_<ref>/library_report.tsv`
   - **MD5:** `[k2_<name>_<ref>_md5]: https://genome-idx.s3.amazonaws.com/kraken/<s3name>_<ref>/<s3name>.md5`  
     For 08_GB/16_GB collections the md5 filename is e.g. `standard_08_GB.md5`, `pluspf_16_GB.md5`.

Do **not** change EuPathDB46, core_nt, or GTDB rows in this step unless they are being updated in the same release.

---

## Step 2: Move previous “Latest” Refseq rows to “Older”

1. **New date block in Older table**  
   In the “# Older Kraken 2 / Bracken Refseq indexes” section, add a **new** date block at the **top** of the Older table (right after the table header and separator). Format: a row like `**October, 2025**` with empty cells, then the 11 Refseq rows with the **previous** release’s date, sizes, and link refs (the same refs that were previously in Latest).

2. **Link definitions for Older**  
   Ensure every ref used in the new Older block has a definition. Definitions for older refs already in the file can stay where they are. If the ref you moved from Latest is new to the Older section, add its definitions in the “Older refs” block (the same link pattern as in Step 1; S3 path naming may use `08gb`/`16gb` for older releases).

---

## Step 3: Run the link checker

From the repo root (or from `docs/`):

```bash
python docs/check_k2_links.py docs/k2.md
```

Fix any reported broken URLs (typos, wrong ref date in path, etc.). Re-run until exit code 0.

---

## Step 4: Sanity checks (manual)

- **Date vs URL ref**  
  For each row, the date in the table (e.g. `2/26/2026`) should match the ref in the links (e.g. `20260226`). Spot-check Latest and the new Older block. Known exception: GTDB v220 (Dec 2024) has table date 12/13/2024 but links use `20241109`—leave as-is unless fixing historically.

- **GTDB md5 filename**  
  GTDB md5 links should use `gtdb_genome_reps.md5` (not `gtdb_genomes_reps.md5`). If a link is wrong, fix it.

- **Pracken / other special sections**  
  Ensure link definitions that look like `[pracken202510_url]: ...` resolve to a **full** `https://...` URL, not a bare filename.

- **08_GB vs 08gb**  
  Newer S3 paths use `08_GB` / `16_GB`; older ones may use `08gb` / `16gb`. When adding or copying link defs, match the convention used by that release on S3.

---

## Checklist (quarterly run)

- [ ] `k2_sizes_for_table.py`: `dates` updated to new ref (e.g. `20260515`); run to confirm sizes if desired.
- [ ] Latest: heading, 11 Refseq rows (date, sizes, link refs), and new link definitions added.
- [ ] Older: new date block added at top with previous 11 rows; link definitions present for that ref.
- [ ] `python docs/check_k2_links.py docs/k2.md` exits 0.
- [ ] Sanity: date/link ref alignment, GTDB md5 name, full URLs for Pracken, 08_GB vs 08gb.
