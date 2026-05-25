# Index Zone usage tooling

This directory contains a small AWS CLI based reporting tool for the Index Zone
S3 bucket. It is designed to use temporary credentials through the
`index-zone-usage` profile.

The tool avoids Python package dependencies. It shells out to `aws`, parses JSON
responses, and streams S3 server access logs from the local cache.

## Setup

Add this profile to your local AWS config:

```ini
[profile index-zone-usage]
role_arn = arn:aws:iam::128342663110:role/IndexZoneUsageReaderRole
source_profile = data-langmead
region = us-east-1
```

Then verify:

```bash
aws sts get-caller-identity --profile index-zone-usage
```

## Broad cost and usage

Daily S3 cost and usage grouped by AWS usage type:

```bash
python3 tools/usage/index_zone_usage.py cost \
  --start 2026-05-01 \
  --end 2026-05-24 \
  --format csv
```

Useful usage types include `DataTransfer-Out-Bytes`, `Requests-*`,
`TimedStorage-*`, and inter-region `*-AWS-Out-Bytes` lines.

## Fetch S3 access logs

S3 server access logs are already configured for `genome-idx` and delivered to
`genome-idx-logs`. Cache a date range locally:

```bash
python3 tools/usage/index_zone_usage.py logs fetch \
  --start 2026-05-23 \
  --end 2026-05-24
```

The default cache is `.usage-cache/s3-access-logs/`, which is ignored by git.

## Summarize raw requests

Summarize cached logs by date, prefix, key, operation, and HTTP status:

```bash
python3 tools/usage/index_zone_usage.py logs summarize \
  --start 2026-05-23 \
  --end 2026-05-24 \
  --format csv
```

This reports raw request counts. For large files, raw request count is often not
the same thing as a user-visible download.

## Estimate file downloads

Estimate download sessions by coalescing nearby `REST.GET.OBJECT` records for
the same key and client fingerprint:

```bash
python3 tools/usage/index_zone_usage.py downloads \
  --start 2026-05-23 \
  --end 2026-05-24 \
  --window-minutes 15 \
  --format csv
```

The output includes both `download_sessions` and `raw_get_requests`. It also
splits sessions into likely complete versus likely partial based on cumulative
bytes sent relative to object size.

Client IPs are used only for private in-memory coalescing and are not emitted in
reports.

## Storage metrics

Latest CloudWatch S3 storage metrics:

```bash
python3 tools/usage/index_zone_usage.py storage --format csv
```

This discovers available S3 storage metric dimensions for `genome-idx`, then
reports the latest datapoint found within the last 14 days.

## Snapshot for the explorer UI

Build a single JSON file containing Cost Explorer rows, storage rows, and any
cached log summaries:

```bash
python3 tools/usage/index_zone_usage.py snapshot \
  --start 2026-05-01 \
  --end 2026-05-24 \
  --output /tmp/index-zone-usage-snapshot.json
```

Open `tools/usage/ui/index.html` in a browser and load the snapshot JSON.
The static explorer can roll Cost Explorer transfer data and inferred downloads
up by day, week, or month. It also includes a selectable top-files table that
allocates approximate download cost by applying the snapshot's effective
transfer-out and request rates to each file's inferred download traffic.

## Website highlights

Build the small JSON file used by the Index Zone home page usage cards:

```bash
python3 tools/usage/index_zone_usage.py highlights \
  --start 2026-05-01 \
  --end 2026-05-24 \
  --output docs/_data/usage_highlights.json
```

The committed snapshot should be refreshed deliberately; it is not updated by
the site build.
