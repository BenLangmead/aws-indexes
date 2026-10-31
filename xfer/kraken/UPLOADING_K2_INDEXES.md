# Uploading a new set of Kraken 2 indexes to Index Zone

This runbook is for **Rone (`rcharles`)** to publish a fresh quarterly set of Kraken 2
prebuilt indexes to the Index Zone website, using **his own identity** — not Ben's
`langmead` credentials.

There are two things you touch:

1. **The S3 bucket** `s3://genome-idx/kraken/` in AWS account **`128342663110`**
   ("Public data registry", the account whose IAM users are `langmead` and `rcharles`).
   You write to it through a **role** you assume, never with raw keys.
2. **The website** at <https://benlangmead.github.io/aws-indexes/k2> — a Jekyll/GitHub
   Pages site built from [`docs/k2.md`](../../docs/k2.md) in `BenLangmead/aws-indexes`.
   Editing that file and pushing to `master` republishes the table.

Part 0 is a **one-time** setup. Parts 1–4 are what you repeat every quarter.

---

## Part 0 — One-time setup

### 0a. IAM: confirm your access (Ben, once)

Your IAM user `rcharles` should already be a member of the **`IndexZoneS3Assumers`**
group in account `128342663110`. That group grants `sts:AssumeRole` on both:

- `IndexZoneS3ManagerRole` — read/write `s3://genome-idx` (this is what uploads use)
- `IndexZoneUsageReaderRole` — read-only usage/billing telemetry (optional)

If for any reason `rcharles` is not in that group, Ben adds it in the IAM console
(account `128342663110` → IAM → Groups → `IndexZoneS3Assumers` → add user `rcharles`).
Rone's user needs **console sign-in enabled** so the `aws login` flow below works.

### 0b. AWS CLI profiles on the build host (Rone, once)

You run the upload from wherever you built the databases (the CompBio cluster —
`elephant1`). Confirm AWS CLI v2 (2.35+) is available there:

```bash
aws --version      # need aws-cli/2.35 or newer for the `aws login` command
```

Edit `~/.aws/config` and add three profiles. The **base** profile `data-rcharles` is
your console-login identity; the two `index-zone-*` profiles **role-chain** off it
(`source_profile = data-rcharles`). This mirrors Ben's `data-langmead` setup with your
user substituted.

```ini
# Base IAM-user identity, driven by `aws login` (no long-lived keys on disk).
[profile data-rcharles]
region = us-east-1
# (mirror the rest of Ben's [profile data-langmead] stanza if it has extra keys)

# Assume the content-manager role — this is what the upload writes through.
[profile index-zone-s3]
role_arn = arn:aws:iam::128342663110:role/IndexZoneS3ManagerRole
source_profile = data-rcharles
region = us-east-1

# Optional: read-only usage/billing telemetry.
[profile index-zone-usage]
role_arn = arn:aws:iam::128342663110:role/IndexZoneUsageReaderRole
source_profile = data-rcharles
region = us-east-1
```

### 0c. Log in and verify (Rone)

`aws login` prints a sign-in URL and waits for an authorization code. On a headless
node reached over SSH (like `elephant1`), use `--remote`:

```bash
aws login --remote --profile data-rcharles
# Open the printed URL in your browser, sign in as rcharles, paste the code back.
```

This caches temporary credentials **plus a refresh token**, so ordinary
`--profile index-zone-s3 …` calls keep working silently for a long time. You only
re-run `aws login` when a call fails with *"Your session has expired. Please
reauthenticate using 'aws login'"*.

Verify the role chain works end to end:

```bash
aws sts get-caller-identity --profile index-zone-s3 --query Arn --output text
# expect: arn:aws:sts::128342663110:assumed-role/IndexZoneS3ManagerRole/...

aws s3 ls s3://genome-idx/kraken/ --profile index-zone-s3 | tail
# expect: a listing of existing kraken/ objects (no AccessDenied)
```

### 0d. GitHub write access + clone (Ben grants once; Rone clones)

Ben adds `rcharles` as a **collaborator with Write access** on
`github.com/BenLangmead/aws-indexes` (repo → Settings → Collaborators). Then Rone, on
whatever machine he edits the site from (your laptop is fine — the website edit does
**not** have to happen on the cluster):

```bash
git clone git@github.com:BenLangmead/aws-indexes.git
cd aws-indexes
```

Setup done. Everything below repeats each quarter.

---

## Part 1 — Pre-upload verification (on the build host)

Get onto the build host the same way Ben does — via the CompBio gateway, in a
persistent `screen` so a dropped SSH connection doesn't kill a multi-hour upload:

```bash
ssh gwln1          # Host alias in ~/.ssh/config (gwln1.pha.jhu.edu, user = you)
screen -r          # reattach; if none exists, start one with:  screen
ssh elephant1
cd <dir containing viral/ minusb/ standard*/ pluspf*/ pluspfp*/>   # your build output dir
```

Now sanity-check the built databases **before** uploading. The per-database
subdirectories are `viral/`, `minusb/`, `standard{,08gb,16gb}/`,
`pluspf{,08gb,16gb}/`, `pluspfp{,08gb,16gb}/`. (`microbial` is intentionally **not**
part of this quarterly set.)

**1. Archive sizes — eyeball against the current website table.**

```bash
find . -name '*.tar.gz' | grep -v 'dbs_' | grep -v archive | xargs du -sh | sort -k2,2
```

Compare the sizes to what's already on <https://benlangmead.github.io/aws-indexes/k2>.
A new build should be in the same ballpark as the previous quarter — a wildly different
size means something went wrong in the build.

**2. Every database has the full set of `.kmer_distrib` files (same count each).**

```bash
for i in 50 100 150 200 250 300 ; do
  ls minusb/database$i* pluspf*/database$i* standard*/database$i* viral/database$i* | wc -l
done
```

Each line must print the **same** number.

**3. Every database has its taxonomy file (same count again).**

```bash
ls minusb/ktax* pluspf*/ktax* standard*/ktax* viral/ktax* | wc -l
```

**4. No truncated `.kmer_distrib` files.** List them and look for any file that is
dramatically smaller than its neighbors on either side (a sign of a partial write):

```bash
ls -l */database*.kmer_distrib
```

**5. Normalize dates.** Occasionally a build finishes with a few files stamped on
different dates. Pick one `YYYYMMDD` for the whole release and make sure every archive
and directory uses it consistently. This date is what you pass to `upload.sh` and what
goes in the website table.

---

## Part 2 — Upload to S3

The uploader is [`upload.sh`](upload.sh). Copy the repo's canonical version to the build
host if you don't already have it (`~/upload.sh`), then:

**1. Check the database loop.** Open `~/upload.sh` and confirm the `for c in …` loop
lists exactly the databases you're releasing this quarter (currently: `viral minusb
pluspf pluspf08gb pluspf16gb pluspfp pluspfp08gb pluspfp16gb standard standard08gb
standard16gb`). Add/remove entries if the offering changed.

**2. Run it with the release date.** The script writes through the `index-zone-s3`
profile by default (no edit needed — that's the role you set up in Part 0):

```bash
./upload.sh 20260226      # <-- use THIS quarter's YYYYMMDD
```

For each database it uploads `k2_<db>_<DATE>.tar.gz` plus the loose per-database files
(`hash.k2d`, `opts.k2d`, `taxo.k2d`, `inspect.txt`, `ktaxonomy.tsv`,
`library_report.tsv`, `seqid2taxid.map`, `names.dmp`, `nodes.dmp`, the `.kmer_distrib`
set, and the `.md5`) under `s3://genome-idx/kraken/<db>_<DATE>/`. It **aborts** if any
expected file is missing, so a clean run means everything was present and copied.

> If you ever need to run it under Ben's identity instead, prefix with
> `AWS_UPLOAD_PROFILE=data-langmead`. Normal operation needs no such override.

**3. Spot-check a couple of objects landed:**

```bash
aws s3 ls s3://genome-idx/kraken/ --profile index-zone-s3 | grep 20260226
aws s3 ls s3://genome-idx/kraken/standard_20260226/ --profile index-zone-s3
```

---

## Part 3 — Update the website table

This part is in your **clone of the repo** (laptop is fine), not the SSH session.

```bash
cd ~/git/aws-indexes/xfer/kraken
```

**1. Point the size-scraper at the new release.** Edit
[`k2_sizes_for_table.py`](k2_sizes_for_table.py):

- Set the `dates` list to this quarter's date, once per database, e.g.
  `dates = ['20260226'] * 11` (it must have the **same length** as the `dbs` list —
  the checked-in copy currently has an 11/12 length mismatch; fix it while you're here).
- Confirm the `dbs` list matches the databases you uploaded.

Then run it (it `curl`s the public HTTPS URLs you just uploaded and prints, per
database, the **archive size** and the **hash.k2d / index size** in GB):

```bash
./k2_sizes_for_table.py
```

**2. Edit [`docs/k2.md`](../../docs/k2.md)** — three edits:

- **The "Latest" heading** near the top (`### Latest: <Month> <Year> update`).
- **The table rows** (the block starting `Collection | Contains | Date | Archive size
  (GB) | Index size (GB) | …`). Add/replace one row per database, filling the Date and
  the two size columns from the script's output. Match the existing row formatting
  exactly — the reference-style link labels are what matter.
- **The reference link definitions** lower in the file (the `[k2_<db>_<DATE>]: https://…`
  blocks for the `.tar.gz`, `_inspect`, `_library`, and `_md5` variants). Copy the
  previous quarter's block and bump the date. Note the `08_GB` / `16_GB` spelling in the
  S3 keys vs. the `-8` / `-16` labels in the table — the existing entries show the
  pattern.

**3. Preview locally (optional but recommended)** to confirm the table renders and links
resolve:

```bash
cd ~/git/aws-indexes/docs
bundle install          # first time only
./jekyll-local.sh serve
# open http://localhost:4000/aws-indexes/k2 and check the new rows + links
```

**4. Commit and push to `master`** (you have direct write access):

```bash
cd ~/git/aws-indexes
git add docs/k2.md xfer/kraken/k2_sizes_for_table.py
git commit -m "Kraken 2 indexes: 20260226 quarterly release"
git push origin master
```

GitHub Pages rebuilds automatically within a minute or two.

---

## Part 4 — Verify the live site

- Load <https://benlangmead.github.io/aws-indexes/k2> and confirm the new rows appear
  with the right sizes and date.
- Click a couple of the new `.tar.gz` / inspect / md5 links to confirm they resolve
  (they point at the S3 objects you uploaded in Part 2). The repo also has a link
  checker: `python docs/check_k2_links.py`.

---

## Quick reference

| Thing | Value |
|---|---|
| Bucket | `s3://genome-idx/kraken/` (account `128342663110`) |
| Upload role | `IndexZoneS3ManagerRole` via profile `index-zone-s3` |
| Base identity | IAM user `rcharles`, profile `data-rcharles` (via `aws login`) |
| Re-auth when | call fails with "session has expired … reauthenticate using 'aws login'" → `aws login --remote --profile data-rcharles` |
| Website source | `docs/k2.md` in `BenLangmead/aws-indexes`, pushed to `master` |
| Build/upload host | CompBio cluster `elephant1` (via `gwln1`, inside `screen`) |
