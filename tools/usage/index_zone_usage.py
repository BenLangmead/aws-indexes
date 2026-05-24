#!/usr/bin/env python3
"""Index Zone AWS usage reporting.

This CLI intentionally uses the AWS CLI instead of boto3 so it works in this
repository without adding Python package dependencies.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable, Iterator, Mapping, Sequence
from urllib.parse import unquote_plus


DEFAULT_PROFILE = "index-zone-usage"
DEFAULT_BUCKET = "genome-idx"
DEFAULT_LOG_BUCKET = "genome-idx-logs"
DEFAULT_REGION = "us-east-1"
DEFAULT_CACHE_DIR = Path(".usage-cache") / "s3-access-logs"
FIRST_KNOWN_LOG_DATE = "2020-06-15"

S3_LOG_RE = re.compile(
    r"^(?P<owner>\S+) "
    r"(?P<bucket>\S+) "
    r"\[(?P<time>[^\]]+)\] "
    r"(?P<remote_ip>\S+) "
    r"(?P<requester>\S+) "
    r"(?P<request_id>\S+) "
    r"(?P<operation>\S+) "
    r"(?P<key>\S+) "
    r'"(?P<request_uri>[^"]*)" '
    r"(?P<http_status>\S+) "
    r"(?P<error_code>\S+) "
    r"(?P<bytes_sent>\S+) "
    r"(?P<object_size>\S+) "
    r"(?P<total_time>\S+) "
    r"(?P<turnaround_time>\S+) "
    r'"(?P<referrer>[^"]*)" '
    r'"(?P<user_agent>[^"]*)"'
    r"(?: (?P<rest>.*))?$"
)


@dataclasses.dataclass(frozen=True)
class S3AccessLogRecord:
    owner: str
    bucket: str
    time: dt.datetime
    remote_ip: str | None
    requester: str | None
    request_id: str
    operation: str
    key: str | None
    request_uri: str | None
    http_status: int | None
    error_code: str | None
    bytes_sent: int | None
    object_size: int | None
    total_time_ms: int | None
    turnaround_time_ms: int | None
    referrer: str | None
    user_agent: str | None
    raw: str

    @property
    def date(self) -> str:
        return self.time.date().isoformat()

    @property
    def prefix(self) -> str:
        if not self.key:
            return ""
        return self.key.split("/", 1)[0] if "/" in self.key else ""

    @property
    def client_fingerprint(self) -> str:
        parts = (
            self.remote_ip or "",
            self.requester or "",
            self.user_agent or "",
        )
        return hashlib.sha256("\t".join(parts).encode("utf-8")).hexdigest()[:16]


@dataclasses.dataclass
class DownloadSession:
    key: str
    prefix: str
    client_fingerprint: str
    user_agent_hash: str
    first_seen: dt.datetime
    last_seen: dt.datetime
    raw_get_requests: int = 0
    bytes_sent: int = 0
    object_size: int | None = None

    def add(self, record: S3AccessLogRecord) -> None:
        self.last_seen = max(self.last_seen, record.time)
        self.raw_get_requests += 1
        self.bytes_sent += record.bytes_sent or 0
        if record.object_size is not None:
            self.object_size = max(self.object_size or 0, record.object_size)

    def is_complete(self, threshold: float) -> bool:
        if not self.object_size:
            return False
        return self.bytes_sent >= int(self.object_size * threshold)


def none_if_dash(value: str | None) -> str | None:
    return None if value in (None, "-") else value


def int_or_none(value: str | None) -> int | None:
    if value in (None, "-"):
        return None
    return int(value)


def parse_s3_time(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%d/%b/%Y:%H:%M:%S %z")


def parse_s3_access_log_line(line: str) -> S3AccessLogRecord:
    stripped = line.rstrip("\n")
    match = S3_LOG_RE.match(stripped)
    if not match:
        raise ValueError(f"not an S3 access log line: {stripped[:120]}")
    fields = match.groupdict()
    raw_key = none_if_dash(fields["key"])
    return S3AccessLogRecord(
        owner=fields["owner"],
        bucket=fields["bucket"],
        time=parse_s3_time(fields["time"]),
        remote_ip=none_if_dash(fields["remote_ip"]),
        requester=none_if_dash(fields["requester"]),
        request_id=fields["request_id"],
        operation=fields["operation"],
        key=unquote_plus(raw_key) if raw_key else None,
        request_uri=none_if_dash(fields["request_uri"]),
        http_status=int_or_none(fields["http_status"]),
        error_code=none_if_dash(fields["error_code"]),
        bytes_sent=int_or_none(fields["bytes_sent"]),
        object_size=int_or_none(fields["object_size"]),
        total_time_ms=int_or_none(fields["total_time"]),
        turnaround_time_ms=int_or_none(fields["turnaround_time"]),
        referrer=none_if_dash(fields["referrer"]),
        user_agent=none_if_dash(fields["user_agent"]),
        raw=stripped,
    )


def parse_date(value: str | None) -> dt.date | None:
    if value is None:
        return None
    return dt.date.fromisoformat(value)


def iter_dates(start: dt.date, end: dt.date) -> Iterator[dt.date]:
    current = start
    while current < end:
        yield current
        current += dt.timedelta(days=1)


def run_aws(
    aws_args: Sequence[str],
    *,
    profile: str | None,
    region: str | None = None,
    expect_json: bool = True,
) -> Any:
    cmd = ["aws"]
    if profile:
        cmd += ["--profile", profile]
    if region:
        cmd += ["--region", region]
    cmd += list(aws_args)
    if expect_json and "--output" not in aws_args:
        cmd += ["--output", "json"]
    result = subprocess.run(cmd, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"AWS command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"{result.stderr.strip()}"
        )
    if expect_json:
        return json.loads(result.stdout or "{}")
    return result.stdout


def write_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    fmt: str,
    output: str | None,
    markdown_title: str | None = None,
) -> None:
    stream = open(output, "w", newline="") if output else sys.stdout
    try:
        if fmt == "json":
            json.dump(list(rows), stream, indent=2, default=str)
            stream.write("\n")
            return
        headers = list(rows[0].keys()) if rows else []
        if fmt == "md":
            if markdown_title:
                stream.write(f"# {markdown_title}\n\n")
            if not headers:
                stream.write("_No rows._\n")
                return
            stream.write("| " + " | ".join(headers) + " |\n")
            stream.write("| " + " | ".join("---" for _ in headers) + " |\n")
            for row in rows:
                stream.write("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |\n")
            return
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if output:
            stream.close()


def write_json_document(document: Mapping[str, Any], output: str | None) -> None:
    stream = open(output, "w") if output else sys.stdout
    try:
        json.dump(document, stream, indent=2, default=str)
        stream.write("\n")
    finally:
        if output:
            stream.close()


def get_cost_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    metrics = args.metrics.split(",")
    request = [
        "ce",
        "get-cost-and-usage",
        "--time-period",
        f"Start={args.start},End={args.end}",
        "--granularity",
        args.granularity,
        "--metrics",
        *metrics,
        "--filter",
        json.dumps({"Dimensions": {"Key": "SERVICE", "Values": [args.service]}}),
    ]
    if args.group_by:
        request += ["--group-by", f"Type=DIMENSION,Key={args.group_by}"]
    data = run_aws(request, profile=args.profile, region=args.region)
    rows: list[dict[str, Any]] = []
    for period in data.get("ResultsByTime", []):
        start = period["TimePeriod"]["Start"]
        end = period["TimePeriod"]["End"]
        groups = period.get("Groups") or [{"Keys": ["TOTAL"], "Metrics": period.get("Total", {})}]
        for group in groups:
            usage_type = group.get("Keys", ["TOTAL"])[0]
            for metric, values in group.get("Metrics", {}).items():
                rows.append(
                    {
                        "start": start,
                        "end": end,
                        "group": usage_type,
                        "metric": metric,
                        "amount": values.get("Amount"),
                        "unit": values.get("Unit"),
                    }
                )
    return rows


def list_log_objects_for_prefix(args: argparse.Namespace, prefix: str) -> Iterator[dict[str, Any]]:
    token: str | None = None
    while True:
        request = [
            "s3api",
            "list-objects-v2",
            "--bucket",
            args.log_bucket,
            "--prefix",
            prefix,
        ]
        if token:
            request += ["--continuation-token", token]
        data = run_aws(request, profile=args.profile, region=args.region)
        for obj in data.get("Contents", []):
            yield obj
        token = data.get("NextContinuationToken")
        if not token:
            break


def date_prefixes(start: str, end: str) -> Iterator[str]:
    start_date = dt.date.fromisoformat(start)
    end_date = dt.date.fromisoformat(end)
    for day in iter_dates(start_date, end_date):
        yield day.isoformat()


def local_log_path(cache_dir: Path, key: str) -> Path:
    return cache_dir / key


def fetch_logs(args: argparse.Namespace) -> list[dict[str, Any]]:
    cache_dir = Path(args.cache_dir)
    rows: list[dict[str, Any]] = []
    seen = 0
    downloaded = 0
    for prefix in date_prefixes(args.start, args.end):
        for obj in list_log_objects_for_prefix(args, prefix):
            if args.max_objects and seen >= args.max_objects:
                break
            key = obj["Key"]
            seen += 1
            destination = local_log_path(cache_dir, key)
            exists = destination.exists() and destination.stat().st_size == obj.get("Size")
            if not args.dry_run and not exists:
                destination.parent.mkdir(parents=True, exist_ok=True)
                run_aws(
                    [
                        "s3",
                        "cp",
                        f"s3://{args.log_bucket}/{key}",
                        str(destination),
                    ],
                    profile=args.profile,
                    region=args.region,
                    expect_json=False,
                )
                downloaded += 1
            rows.append(
                {
                    "key": key,
                    "last_modified": obj.get("LastModified"),
                    "size": obj.get("Size"),
                    "local_path": str(destination),
                    "status": "cached" if exists else ("dry-run" if args.dry_run else "downloaded"),
                }
            )
        if args.max_objects and seen >= args.max_objects:
            break
    sys.stderr.write(f"listed={seen} downloaded={downloaded}\n")
    return rows


def iter_log_paths(inputs: Sequence[str], cache_dir: str | None) -> Iterator[Path]:
    if inputs:
        for item in inputs:
            path = Path(item)
            if path.is_dir():
                yield from (p for p in sorted(path.rglob("*")) if p.is_file())
            else:
                yield path
        return
    base = Path(cache_dir or DEFAULT_CACHE_DIR)
    if base.exists():
        yield from (p for p in sorted(base.rglob("*")) if p.is_file())


def iter_records(
    paths: Iterable[Path],
    *,
    start: str | None = None,
    end: str | None = None,
    skip_bad_lines: bool = False,
) -> Iterator[S3AccessLogRecord]:
    start_date = parse_date(start)
    end_date = parse_date(end)
    for path in paths:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line_no, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    record = parse_s3_access_log_line(line)
                except ValueError:
                    if skip_bad_lines:
                        continue
                    raise ValueError(f"{path}:{line_no}: invalid S3 access log line") from None
                record_date = record.time.date()
                if start_date and record_date < start_date:
                    continue
                if end_date and record_date >= end_date:
                    continue
                yield record


def summarize_logs(args: argparse.Namespace) -> list[dict[str, Any]]:
    aggregates: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for record in iter_records(
        iter_log_paths(args.inputs, args.cache_dir),
        start=args.start,
        end=args.end,
        skip_bad_lines=args.skip_bad_lines,
    ):
        key = record.key or ""
        aggregate_key = (
            record.date,
            record.prefix,
            key,
            record.operation,
            str(record.http_status or ""),
        )
        row = aggregates.setdefault(
            aggregate_key,
            {
                "date": record.date,
                "prefix": record.prefix,
                "key": key,
                "operation": record.operation,
                "http_status": record.http_status or "",
                "raw_requests": 0,
                "bytes_sent": 0,
                "max_object_size": 0,
                "first_seen": record.time.isoformat(),
                "last_seen": record.time.isoformat(),
            },
        )
        row["raw_requests"] += 1
        row["bytes_sent"] += record.bytes_sent or 0
        row["max_object_size"] = max(row["max_object_size"], record.object_size or 0)
        row["first_seen"] = min(row["first_seen"], record.time.isoformat())
        row["last_seen"] = max(row["last_seen"], record.time.isoformat())
    return sorted(aggregates.values(), key=lambda r: (r["date"], r["prefix"], r["key"], r["operation"]))


def is_download_record(record: S3AccessLogRecord) -> bool:
    return (
        record.operation == "REST.GET.OBJECT"
        and record.key is not None
        and record.http_status in (200, 206)
        and (record.bytes_sent or 0) > 0
    )


def coalesce_download_sessions(
    records: Iterable[S3AccessLogRecord],
    *,
    window: dt.timedelta,
) -> list[DownloadSession]:
    active: dict[tuple[str, str], DownloadSession] = {}
    sessions: list[DownloadSession] = []
    sorted_records = sorted((r for r in records if is_download_record(r)), key=lambda r: r.time)
    for record in sorted_records:
        assert record.key is not None
        user_agent_hash = hashlib.sha256((record.user_agent or "").encode("utf-8")).hexdigest()[:16]
        session_key = (record.key, record.client_fingerprint)
        current = active.get(session_key)
        if current is None or record.time - current.last_seen > window:
            if current is not None:
                sessions.append(current)
            current = DownloadSession(
                key=record.key,
                prefix=record.prefix,
                client_fingerprint=record.client_fingerprint,
                user_agent_hash=user_agent_hash,
                first_seen=record.time,
                last_seen=record.time,
            )
            active[session_key] = current
        current.add(record)
    sessions.extend(active.values())
    return sessions


def summarize_downloads(args: argparse.Namespace) -> list[dict[str, Any]]:
    sessions = coalesce_download_sessions(
        iter_records(
            iter_log_paths(args.inputs, args.cache_dir),
            start=args.start,
            end=args.end,
            skip_bad_lines=args.skip_bad_lines,
        ),
        window=dt.timedelta(minutes=args.window_minutes),
    )
    aggregates: dict[tuple[str, str, str], dict[str, Any]] = {}
    for session in sessions:
        row_key = (session.first_seen.date().isoformat(), session.prefix, session.key)
        row = aggregates.setdefault(
            row_key,
            {
                "date": row_key[0],
                "prefix": session.prefix,
                "key": session.key,
                "download_sessions": 0,
                "likely_complete_sessions": 0,
                "likely_partial_sessions": 0,
                "raw_get_requests": 0,
                "bytes_sent": 0,
                "max_object_size": 0,
                "first_seen": session.first_seen.isoformat(),
                "last_seen": session.last_seen.isoformat(),
            },
        )
        row["download_sessions"] += 1
        if session.is_complete(args.complete_threshold):
            row["likely_complete_sessions"] += 1
        else:
            row["likely_partial_sessions"] += 1
        row["raw_get_requests"] += session.raw_get_requests
        row["bytes_sent"] += session.bytes_sent
        row["max_object_size"] = max(row["max_object_size"], session.object_size or 0)
        row["first_seen"] = min(row["first_seen"], session.first_seen.isoformat())
        row["last_seen"] = max(row["last_seen"], session.last_seen.isoformat())
    return sorted(aggregates.values(), key=lambda r: (r["date"], r["prefix"], r["key"]))


def discover_storage_metrics(args: argparse.Namespace, metric_name: str) -> list[str]:
    data = run_aws(
        [
            "cloudwatch",
            "list-metrics",
            "--namespace",
            "AWS/S3",
            "--metric-name",
            metric_name,
            "--dimensions",
            f"Name=BucketName,Value={args.bucket}",
        ],
        profile=args.profile,
        region=args.region,
    )
    storage_types: set[str] = set()
    for metric in data.get("Metrics", []):
        for dim in metric.get("Dimensions", []):
            if dim.get("Name") == "StorageType":
                storage_types.add(dim["Value"])
    return sorted(storage_types)


def latest_storage_datapoint(args: argparse.Namespace, metric_name: str, storage_type: str) -> dict[str, Any] | None:
    end = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1)
    start = end - dt.timedelta(days=args.days)
    data = run_aws(
        [
            "cloudwatch",
            "get-metric-statistics",
            "--namespace",
            "AWS/S3",
            "--metric-name",
            metric_name,
            "--start-time",
            start.isoformat(),
            "--end-time",
            end.isoformat(),
            "--period",
            "86400",
            "--statistics",
            "Average",
            "--dimensions",
            f"Name=BucketName,Value={args.bucket}",
            f"Name=StorageType,Value={storage_type}",
        ],
        profile=args.profile,
        region=args.region,
    )
    points = data.get("Datapoints", [])
    if not points:
        return None
    return sorted(points, key=lambda p: p["Timestamp"])[-1]


def storage_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for metric_name in ("BucketSizeBytes", "NumberOfObjects"):
        for storage_type in discover_storage_metrics(args, metric_name):
            point = latest_storage_datapoint(args, metric_name, storage_type)
            if not point:
                continue
            rows.append(
                {
                    "bucket": args.bucket,
                    "metric": metric_name,
                    "storage_type": storage_type,
                    "timestamp": point["Timestamp"],
                    "average": point["Average"],
                    "unit": point.get("Unit", ""),
                }
            )
    return rows


def numeric(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def sum_metric(
    rows: Sequence[Mapping[str, Any]],
    *,
    metric: str,
    unit: str | None = None,
    group_suffix: str | None = None,
    group_prefix: str | None = None,
    group_exact: str | None = None,
) -> float:
    total = 0.0
    for row in rows:
        group = str(row.get("group", ""))
        if row.get("metric") != metric:
            continue
        if unit and row.get("unit") != unit:
            continue
        if group_suffix and not group.endswith(group_suffix):
            continue
        if group_prefix and not group.startswith(group_prefix):
            continue
        if group_exact and group != group_exact:
            continue
        total += numeric(row.get("amount"))
    return total


def compact_number(value: float) -> str:
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 10_000:
        return f"{value / 1_000:.0f}K"
    if value >= 1_000:
        return f"{value:,.0f}"
    if math.isclose(value, round(value)):
        return f"{value:.0f}"
    return f"{value:.1f}"


def compact_money(value: float) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def end_minus_one(end: str) -> str:
    return (dt.date.fromisoformat(end) - dt.timedelta(days=1)).isoformat()


def period_days(start: str, end: str) -> int:
    return max(1, (dt.date.fromisoformat(end) - dt.date.fromisoformat(start)).days)


def display_period(start: str, end: str) -> str:
    start_date = dt.date.fromisoformat(start)
    end_date = dt.date.fromisoformat(end_minus_one(end))
    start_month = start_date.strftime("%B")
    end_month = end_date.strftime("%B")
    if start_date.year == end_date.year and start_date.month == end_date.month:
        return f"{start_month} {start_date.day} through {end_month} {end_date.day}, {end_date.year}"
    if start_date.year == end_date.year:
        return f"{start_month} {start_date.day} through {end_month} {end_date.day}, {end_date.year}"
    return f"{start_month} {start_date.day}, {start_date.year} through {end_month} {end_date.day}, {end_date.year}"


def storage_totals(rows: Sequence[Mapping[str, Any]]) -> tuple[float, float, str | None]:
    bytes_total = 0.0
    objects = 0.0
    timestamp: str | None = None
    for row in rows:
        if row.get("metric") == "BucketSizeBytes":
            bytes_total += numeric(row.get("average"))
            timestamp = timestamp or str(row.get("timestamp", ""))
        elif row.get("metric") == "NumberOfObjects" and row.get("storage_type") == "AllStorageTypes":
            objects = numeric(row.get("average"))
            timestamp = timestamp or str(row.get("timestamp", ""))
    return bytes_total, objects, timestamp


def build_highlights(
    *,
    start: str,
    end: str,
    cost_rows: Sequence[Mapping[str, Any]],
    storage: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    egress_gb = sum_metric(
        cost_rows,
        metric="UsageQuantity",
        unit="GB",
        group_suffix="Out-Bytes",
    )
    public_egress_gb = sum_metric(
        cost_rows,
        metric="UsageQuantity",
        unit="GB",
        group_exact="DataTransfer-Out-Bytes",
    )
    requests = sum_metric(
        cost_rows,
        metric="UsageQuantity",
        unit="Requests",
        group_prefix="Requests-",
    )
    unblended_cost = sum_metric(cost_rows, metric="UnblendedCost")
    bytes_total, objects, storage_timestamp = storage_totals(storage)
    storage_tb = bytes_total / 1_000_000_000_000
    weekly_egress_gb = egress_gb / period_days(start, end) * 7
    weekly_unblended_cost = unblended_cost / period_days(start, end) * 7
    period_label = display_period(start, end)
    generated_at = dt.datetime.now(dt.timezone.utc)
    updated_label = f"{generated_at.strftime('%B')} {generated_at.day}, {generated_at.year}"
    cards = [
        {
            "label": "Indexed data stored",
            "value": f"{storage_tb:.1f} TB",
            "detail": f"Current S3 storage across {compact_number(objects)} objects.",
        },
        {
            "label": "Objects available",
            "value": compact_number(objects),
            "detail": "Public files, archives, indexes, checksums, and reports in genome-idx.",
        },
        {
            "label": "Data served this period",
            "value": f"{egress_gb / 1000:.1f} TB",
            "detail": f"S3 transfer out from {period_label}.",
        },
        {
            "label": "S3 requests this period",
            "value": compact_number(requests),
            "detail": "Cost Explorer request classes for the same period.",
        },
    ]
    site_cards = [
        {
            "label": "Indexed data stored",
            "value": f"{storage_tb:.1f} TB",
        },
        {
            "label": "Files available",
            "value": compact_number(objects),
        },
        {
            "label": "Data served per week",
            "value": f"~{weekly_egress_gb / 1000:.1f} TB",
        },
        {
            "label": "AWS charges per week",
            "value": f"~{compact_money(weekly_unblended_cost)}",
            "note": "Thank you, AWS!",
        },
    ]
    return {
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "updated_label": updated_label,
        "period": {"start": start, "end": end, "label": period_label},
        "first_known_log_date": FIRST_KNOWN_LOG_DATE,
        "storage_timestamp": storage_timestamp,
        "metrics": {
            "egress_gb": egress_gb,
            "public_egress_gb": public_egress_gb,
            "weekly_egress_gb": weekly_egress_gb,
            "weekly_unblended_cost_usd": weekly_unblended_cost,
            "requests": requests,
            "unblended_cost_usd": unblended_cost,
            "storage_bytes": bytes_total,
            "storage_tb_decimal": storage_tb,
            "objects": objects,
        },
        "cards": cards,
        "site_cards": site_cards,
    }


def snapshot_document(args: argparse.Namespace) -> dict[str, Any]:
    cost_args = argparse.Namespace(
        profile=args.profile,
        region=args.region,
        start=args.start,
        end=args.end,
        granularity=args.granularity,
        metrics="UnblendedCost,UsageQuantity",
        service="Amazon Simple Storage Service",
        group_by="USAGE_TYPE",
    )
    storage_args = argparse.Namespace(
        profile=args.profile,
        region=args.region,
        bucket=args.bucket,
        days=args.storage_days,
    )
    cost_rows = get_cost_rows(cost_args)
    storage = storage_rows(storage_args)
    log_args = argparse.Namespace(
        inputs=args.inputs,
        cache_dir=args.cache_dir,
        start=args.start,
        end=args.end,
        skip_bad_lines=args.skip_bad_lines,
        window_minutes=args.window_minutes,
        complete_threshold=args.complete_threshold,
    )
    logs_summary: list[dict[str, Any]] = []
    downloads_summary: list[dict[str, Any]] = []
    if not args.no_logs:
        logs_summary = summarize_logs(log_args)
        downloads_summary = summarize_downloads(log_args)
    highlights = build_highlights(start=args.start, end=args.end, cost_rows=cost_rows, storage=storage)
    return {
        "generated_at": highlights["generated_at"],
        "bucket": args.bucket,
        "log_bucket": args.log_bucket,
        "period": highlights["period"],
        "highlights": highlights,
        "cost": cost_rows,
        "storage": storage,
        "logs": {
            "summary": logs_summary,
            "downloads": downloads_summary,
            "privacy": "Raw client IPs are not emitted. Download coalescing uses hashed client fingerprints only.",
        },
    }


def highlights_document(args: argparse.Namespace) -> dict[str, Any]:
    cost_args = argparse.Namespace(
        profile=args.profile,
        region=args.region,
        start=args.start,
        end=args.end,
        granularity=args.granularity,
        metrics="UnblendedCost,UsageQuantity",
        service="Amazon Simple Storage Service",
        group_by="USAGE_TYPE",
    )
    storage_args = argparse.Namespace(
        profile=args.profile,
        region=args.region,
        bucket=args.bucket,
        days=args.storage_days,
    )
    return build_highlights(
        start=args.start,
        end=args.end,
        cost_rows=get_cost_rows(cost_args),
        storage=storage_rows(storage_args),
    )


def add_common_aws_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile", default=os.environ.get("AWS_PROFILE", DEFAULT_PROFILE))
    parser.add_argument("--region", default=os.environ.get("AWS_REGION", DEFAULT_REGION))


def add_output_args(parser: argparse.ArgumentParser, *, default: str = "csv") -> None:
    parser.add_argument("--format", choices=("csv", "json", "md"), default=default)
    parser.add_argument("--output", help="Write output to this file instead of stdout.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    cost = subparsers.add_parser("cost", help="Query Cost Explorer usage/cost data.")
    add_common_aws_args(cost)
    add_output_args(cost)
    cost.add_argument("--start", required=True, help="Inclusive start date, YYYY-MM-DD.")
    cost.add_argument("--end", required=True, help="Exclusive end date, YYYY-MM-DD.")
    cost.add_argument("--granularity", choices=("DAILY", "MONTHLY"), default="DAILY")
    cost.add_argument("--service", default="Amazon Simple Storage Service")
    cost.add_argument("--group-by", default="USAGE_TYPE")
    cost.add_argument("--metrics", default="UnblendedCost,UsageQuantity")
    cost.set_defaults(func=lambda args: write_rows(get_cost_rows(args), fmt=args.format, output=args.output))

    logs = subparsers.add_parser("logs", help="Fetch or summarize S3 access logs.")
    logs_subparsers = logs.add_subparsers(dest="logs_command", required=True)

    fetch = logs_subparsers.add_parser("fetch", help="Cache S3 access log objects locally.")
    add_common_aws_args(fetch)
    add_output_args(fetch)
    fetch.add_argument("--log-bucket", default=DEFAULT_LOG_BUCKET)
    fetch.add_argument("--start", required=True, help="Inclusive start date, YYYY-MM-DD.")
    fetch.add_argument("--end", required=True, help="Exclusive end date, YYYY-MM-DD.")
    fetch.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    fetch.add_argument("--max-objects", type=int, default=0)
    fetch.add_argument("--dry-run", action="store_true")
    fetch.set_defaults(func=lambda args: write_rows(fetch_logs(args), fmt=args.format, output=args.output))

    summarize = logs_subparsers.add_parser("summarize", help="Summarize cached S3 access logs.")
    add_output_args(summarize)
    summarize.add_argument("inputs", nargs="*", help="Log files or directories. Defaults to --cache-dir.")
    summarize.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    summarize.add_argument("--start", help="Inclusive record date, YYYY-MM-DD.")
    summarize.add_argument("--end", help="Exclusive record date, YYYY-MM-DD.")
    summarize.add_argument("--skip-bad-lines", action="store_true")
    summarize.set_defaults(
        func=lambda args: write_rows(
            summarize_logs(args),
            fmt=args.format,
            output=args.output,
            markdown_title="S3 Access Log Summary",
        )
    )

    downloads = subparsers.add_parser("downloads", help="Estimate file download sessions from S3 access logs.")
    add_output_args(downloads)
    downloads.add_argument("inputs", nargs="*", help="Log files or directories. Defaults to --cache-dir.")
    downloads.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    downloads.add_argument("--start", help="Inclusive record date, YYYY-MM-DD.")
    downloads.add_argument("--end", help="Exclusive record date, YYYY-MM-DD.")
    downloads.add_argument("--window-minutes", type=float, default=15.0)
    downloads.add_argument("--complete-threshold", type=float, default=0.95)
    downloads.add_argument("--skip-bad-lines", action="store_true")
    downloads.set_defaults(
        func=lambda args: write_rows(
            summarize_downloads(args),
            fmt=args.format,
            output=args.output,
            markdown_title="Estimated Download Sessions",
        )
    )

    storage = subparsers.add_parser("storage", help="Report latest CloudWatch S3 storage metrics.")
    add_common_aws_args(storage)
    add_output_args(storage)
    storage.add_argument("--bucket", default=DEFAULT_BUCKET)
    storage.add_argument("--days", type=int, default=14)
    storage.set_defaults(func=lambda args: write_rows(storage_rows(args), fmt=args.format, output=args.output))

    highlights = subparsers.add_parser("highlights", help="Build website-ready usage highlight JSON.")
    add_common_aws_args(highlights)
    highlights.add_argument("--start", required=True, help="Inclusive start date, YYYY-MM-DD.")
    highlights.add_argument("--end", required=True, help="Exclusive end date, YYYY-MM-DD.")
    highlights.add_argument("--granularity", choices=("DAILY", "MONTHLY"), default="DAILY")
    highlights.add_argument("--bucket", default=DEFAULT_BUCKET)
    highlights.add_argument("--storage-days", type=int, default=14)
    highlights.add_argument("--output", help="Write highlight JSON to this file instead of stdout.")
    highlights.set_defaults(func=lambda args: write_json_document(highlights_document(args), args.output))

    snapshot = subparsers.add_parser("snapshot", help="Build a JSON snapshot for the static explorer UI.")
    add_common_aws_args(snapshot)
    snapshot.add_argument("--start", required=True, help="Inclusive start date, YYYY-MM-DD.")
    snapshot.add_argument("--end", required=True, help="Exclusive end date, YYYY-MM-DD.")
    snapshot.add_argument("--granularity", choices=("DAILY", "MONTHLY"), default="DAILY")
    snapshot.add_argument("--bucket", default=DEFAULT_BUCKET)
    snapshot.add_argument("--log-bucket", default=DEFAULT_LOG_BUCKET)
    snapshot.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    snapshot.add_argument("--storage-days", type=int, default=14)
    snapshot.add_argument("--window-minutes", type=float, default=15.0)
    snapshot.add_argument("--complete-threshold", type=float, default=0.95)
    snapshot.add_argument("--skip-bad-lines", action="store_true")
    snapshot.add_argument("--no-logs", action="store_true", help="Skip cached access-log summaries.")
    snapshot.add_argument("--output", help="Write snapshot JSON to this file instead of stdout.")
    snapshot.add_argument("inputs", nargs="*", help="Cached log files or directories. Defaults to --cache-dir.")
    snapshot.set_defaults(func=lambda args: write_json_document(snapshot_document(args), args.output))

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except RuntimeError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
