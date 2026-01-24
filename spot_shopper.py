#!/usr/bin/env python3

"""
spot_prices_multi_region.py

Query EC2 Spot price history for a single instance type across multiple
AWS regions and availability zones, then write results to CSV.

Requires:
  pip install boto3

AWS permissions needed:
  ec2:DescribeRegions
  ec2:DescribeSpotPriceHistory
  ec2:DescribeInstanceTypes
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError


@dataclass(frozen=True)
class SpotRecord:
    region: str
    availability_zone: str
    instance_type: str
    product_description: str
    timestamp_utc: datetime
    spot_price_usd: float


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Fetch Spot price history for an instance type across regions/AZs."
    )
    p.add_argument("--instance-type", required=True, help="e.g., x8g.24xlarge")
    p.add_argument(
        "--days",
        type=int,
        default=7,
        help="How many days of history to fetch (default: 7)",
    )
    p.add_argument(
        "--regions",
        default="all",
        help=(
            "Comma-separated region list (e.g. us-east-1,us-west-2) "
            "or 'all' (default: all)"
        ),
    )
    p.add_argument(
        "--product",
        default="Linux/UNIX",
        help="Product description (default: Linux/UNIX). Other values exist, e.g. Linux/UNIX (Amazon VPC).",
    )
    p.add_argument(
        "--max-items-per-call",
        type=int,
        default=1000,
        help="Max results per API call/pagination page (default: 1000)",
    )
    p.add_argument(
        "--sleep",
        type=float,
        default=0.2,
        help="Seconds to sleep between region calls to be gentle on APIs (default: 0.2)",
    )
    p.add_argument(
        "--out",
        default=None,
        help="Output CSV path (default: spot_<instance>_<days>d.csv)",
    )
    return p.parse_args()


def check_aws_credentials(session: boto3.Session) -> None:
    """
    Check if AWS credentials are available and valid.
    Raises SystemExit with helpful error message if credentials are missing or invalid.
    """
    # Check if credentials are configured
    try:
        credentials = session.get_credentials()
        if credentials is None:
            raise NoCredentialsError("No credentials found")
    except NoCredentialsError:
        print("ERROR: AWS credentials not found.", file=sys.stderr)
        print("\nTo configure AWS credentials, use one of the following methods:\n", file=sys.stderr)
        print("1. Environment variables:", file=sys.stderr)
        print("   export AWS_ACCESS_KEY_ID='your-access-key-id'", file=sys.stderr)
        print("   export AWS_SECRET_ACCESS_KEY='your-secret-access-key'", file=sys.stderr)
        print("   export AWS_DEFAULT_REGION='us-east-1'  # optional\n", file=sys.stderr)
        print("2. AWS credentials file (~/.aws/credentials):", file=sys.stderr)
        print("   [default]", file=sys.stderr)
        print("   aws_access_key_id = your-access-key-id", file=sys.stderr)
        print("   aws_secret_access_key = your-secret-access-key\n", file=sys.stderr)
        print("3. AWS CLI configure command:", file=sys.stderr)
        print("   aws configure\n", file=sys.stderr)
        print("4. AWS SSO (if using SSO):", file=sys.stderr)
        print("   aws sso login\n", file=sys.stderr)
        raise SystemExit(1)
    
    # Try to validate credentials by making a simple API call
    try:
        # Use a lightweight call to validate credentials
        sts = session.client("sts", region_name="us-east-1")
        sts.get_caller_identity()
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        error_msg = e.response.get("Error", {}).get("Message", str(e))
        
        if error_code == "AuthFailure":
            print("ERROR: AWS credentials are invalid or expired.", file=sys.stderr)
            print(f"   Details: {error_msg}\n", file=sys.stderr)
            print("To fix this:", file=sys.stderr)
            print("1. Verify your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are correct", file=sys.stderr)
            print("2. If using temporary credentials, they may have expired - refresh them", file=sys.stderr)
            print("3. If using AWS SSO, run: aws sso login", file=sys.stderr)
            print("4. Check your IAM user/role has the necessary permissions", file=sys.stderr)
        elif error_code == "InvalidClientTokenId":
            print("ERROR: Invalid AWS access key ID.", file=sys.stderr)
            print("   Please check your AWS_ACCESS_KEY_ID.\n", file=sys.stderr)
        elif error_code == "SignatureDoesNotMatch":
            print("ERROR: AWS secret access key does not match access key ID.", file=sys.stderr)
            print("   Please check your AWS_SECRET_ACCESS_KEY.\n", file=sys.stderr)
        else:
            print(f"ERROR: Failed to validate AWS credentials: {error_msg}", file=sys.stderr)
        raise SystemExit(1)
    except BotoCoreError as e:
        print(f"ERROR: Failed to connect to AWS: {e}", file=sys.stderr)
        print("   Please check your network connection and AWS endpoint configuration.", file=sys.stderr)
        raise SystemExit(1)


def get_all_regions(session: boto3.Session, base_region: str = "us-east-1") -> List[str]:
    """Ask AWS for all enabled regions for this account."""
    ec2 = session.client("ec2", region_name=base_region)
    resp = ec2.describe_regions(AllRegions=False)
    regions = sorted(r["RegionName"] for r in resp.get("Regions", []))
    return regions


def get_instance_type_specs(
    session: boto3.Session, instance_type: str, region: str = "us-east-1"
) -> Optional[Dict]:
    """
    Fetch instance type specifications from AWS.
    Returns a dict with key specs, or None if instance type not found.
    """
    try:
        config = Config(
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=10,
            read_timeout=30,
        )
        ec2 = session.client("ec2", region_name=region, config=config)
        resp = ec2.describe_instance_types(InstanceTypes=[instance_type])
        
        if not resp.get("InstanceTypes"):
            return None
        
        instance_info = resp["InstanceTypes"][0]
        return instance_info
    except ClientError as e:
        # If instance type not found or other error, return None
        return None


def print_instance_specs(instance_type: str, instance_info: Optional[Dict]) -> None:
    """Print a brief description of instance type specifications."""
    print(f"\nInstance Type: {instance_type}")
    print("=" * 60)
    
    if instance_info is None:
        print("  (Specifications not available - instance type may not exist in this region)")
        return
    
    # Extract key specifications
    vcpu = instance_info.get("VCpuInfo", {}).get("DefaultVCpus", "N/A")
    memory_gib = instance_info.get("MemoryInfo", {}).get("SizeInMiB")
    if memory_gib is not None:
        memory_gib = memory_gib / 1024  # Convert MiB to GiB
        memory_str = f"{memory_gib:.1f} GiB"
    else:
        memory_str = "N/A"
    
    # Network performance
    network_info = instance_info.get("NetworkInfo", {})
    network_perf = network_info.get("NetworkPerformance", "N/A")
    max_network_throughput = network_info.get("MaximumNetworkThroughput")
    if max_network_throughput is not None:
        # Convert from Gbps to Mbps if needed, or use as-is
        if isinstance(max_network_throughput, (int, float)):
            max_network_str = f" ({max_network_throughput} Mbps)"
        else:
            max_network_str = ""
    else:
        max_network_str = ""
    
    # EBS performance
    ebs_info = instance_info.get("EbsInfo", {})
    ebs_optimized = ebs_info.get("EbsOptimizedSupport", "N/A")
    ebs_bandwidth = ebs_info.get("EbsOptimizedInfo", {}).get("MaximumBandwidthInMbps")
    if ebs_bandwidth:
        ebs_str = f" (up to {ebs_bandwidth} Mbps)"
    else:
        ebs_str = ""
    
    # Processor info
    processor_info = instance_info.get("ProcessorInfo", {})
    processor = processor_info.get("SupportedArchitectures", [])
    if processor:
        processor_str = ", ".join(processor)
    else:
        processor_str = "N/A"
    
    # Instance storage
    storage_info = instance_info.get("InstanceStorageInfo", {})
    if storage_info:
        total_size_gb = storage_info.get("TotalSizeInGB")
        if total_size_gb:
            storage_str = f"{total_size_gb} GB"
        else:
            storage_str = "Available"
    else:
        storage_str = "EBS only"
    
    # Print formatted specs
    print(f"  vCPU:              {vcpu}")
    print(f"  Memory:            {memory_str}")
    print(f"  Network:           {network_perf}{max_network_str}")
    print(f"  EBS Optimized:     {ebs_optimized}{ebs_str}")
    print(f"  Architecture:      {processor_str}")
    print(f"  Instance Storage:  {storage_str}")
    
    # Additional useful info
    hypervisor = instance_info.get("Hypervisor", "N/A")
    if hypervisor != "N/A":
        print(f"  Hypervisor:        {hypervisor}")
    
    print("=" * 60)
    print()


def fetch_spot_history_for_region(
    session: boto3.Session,
    region: str,
    instance_type: str,
    product_description: str,
    start_time: datetime,
    end_time: datetime,
    max_items_per_call: int = 1000,
) -> List[SpotRecord]:
    """
    Fetch spot price history for one region, paginating until complete.
    """
    # modest retry behavior + sane timeouts
    config = Config(
        retries={"max_attempts": 10, "mode": "standard"},
        connect_timeout=10,
        read_timeout=60,
    )
    ec2 = session.client("ec2", region_name=region, config=config)

    records: List[SpotRecord] = []
    next_token: Optional[str] = None

    while True:
        kwargs = dict(
            StartTime=start_time,
            EndTime=end_time,
            InstanceTypes=[instance_type],
            ProductDescriptions=[product_description],
            MaxResults=max_items_per_call,
        )
        if next_token:
            kwargs["NextToken"] = next_token

        resp = ec2.describe_spot_price_history(**kwargs)

        for r in resp.get("SpotPriceHistory", []):
            # Timestamp is timezone-aware; keep UTC
            ts = r["Timestamp"]
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)

            records.append(
                SpotRecord(
                    region=region,
                    availability_zone=r["AvailabilityZone"],
                    instance_type=r["InstanceType"],
                    product_description=r["ProductDescription"],
                    timestamp_utc=ts.astimezone(timezone.utc),
                    spot_price_usd=float(r["SpotPrice"]),
                )
            )

        next_token = resp.get("NextToken")
        if not next_token:
            break

    return records


def summarize(records: Sequence[SpotRecord]) -> None:
    if not records:
        print("No records returned.")
        return

    # summary: min/median/max by region+AZ
    from statistics import median

    buckets: Dict[Tuple[str, str], List[float]] = {}
    for rec in records:
        key = (rec.region, rec.availability_zone)
        buckets.setdefault(key, []).append(rec.spot_price_usd)

    print(f"Total records: {len(records)}")
    print(f"Distinct (region, AZ): {len(buckets)}")
    print("Price summary by (region, AZ):")
    for (region, az), prices in sorted(buckets.items()):
        prices_sorted = sorted(prices)
        print(
            f"  {region:12s} {az:16s} "
            f"min={prices_sorted[0]:.6f}  med={median(prices_sorted):.6f}  max={prices_sorted[-1]:.6f}  n={len(prices_sorted)}"
        )


def write_csv(path: str, records: Sequence[SpotRecord]) -> None:
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "region",
                "availability_zone",
                "instance_type",
                "product_description",
                "timestamp_utc",
                "spot_price_usd",
            ]
        )
        for r in sorted(records, key=lambda x: (x.region, x.availability_zone, x.timestamp_utc)):
            w.writerow(
                [
                    r.region,
                    r.availability_zone,
                    r.instance_type,
                    r.product_description,
                    r.timestamp_utc.isoformat(),
                    f"{r.spot_price_usd:.6f}",
                ]
            )


def main() -> int:
    args = parse_args()
    session = boto3.Session()
    
    # Check credentials before attempting any AWS API calls
    check_aws_credentials(session)

    end_time = utc_now()
    start_time = end_time - timedelta(days=args.days)

    if args.out is None:
        safe_it = args.instance_type.replace(".", "_")
        args.out = f"spot_{safe_it}_{args.days}d.csv"

    if args.regions.strip().lower() == "all":
        regions = get_all_regions(session)
    else:
        regions = [r.strip() for r in args.regions.split(",") if r.strip()]

    if not regions:
        print("No regions selected.", file=sys.stderr)
        return 2

    # Fetch and print instance type specifications
    instance_info = get_instance_type_specs(session, args.instance_type, regions[0])
    print_instance_specs(args.instance_type, instance_info)

    all_records: List[SpotRecord] = []

    for i, region in enumerate(regions, start=1):
        try:
            recs = fetch_spot_history_for_region(
                session=session,
                region=region,
                instance_type=args.instance_type,
                product_description=args.product,
                start_time=start_time,
                end_time=end_time,
                max_items_per_call=args.max_items_per_call,
            )
            all_records.extend(recs)
            print(f"[{i}/{len(regions)}] {region}: {len(recs)} records")
        except (ClientError, BotoCoreError) as e:
            print(f"[{i}/{len(regions)}] {region}: ERROR: {e}", file=sys.stderr)
        time.sleep(args.sleep)

    write_csv(args.out, all_records)
    print(f"Wrote CSV: {args.out}")
    summarize(all_records)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
