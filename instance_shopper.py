#!/usr/bin/env python3

"""
instance_shopper.py

Filter EC2 instances from a CSV file based on specified requirements.
Allows filtering by vCPUs, memory, compute family, network performance, price, and more.

Usage:
    python instance_shopper.py --min-vcpus 8 --min-memory 32 --max-price 1.0
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


def parse_memory(memory_str: str) -> Optional[float]:
    """Parse memory string like '32 GiB' or '16 GiB' to float (GiB)."""
    if not memory_str or memory_str.strip() == "":
        return None
    match = re.search(r"([\d.]+)\s*GiB", memory_str, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


def parse_vcpus(vcpu_str: str) -> Optional[int]:
    """Parse vCPU string like '8 vCPUs' to int."""
    if not vcpu_str or vcpu_str.strip() == "":
        return None
    match = re.search(r"(\d+)\s*vCPU", vcpu_str, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def parse_price(price_str: str) -> Optional[float]:
    """Parse price string like '$0.204 hourly' to float."""
    if not price_str or price_str.strip() == "":
        return None
    match = re.search(r"\$([\d.]+)", price_str)
    if match:
        return float(match.group(1))
    return None


def parse_coremark(coremark_str: str) -> Optional[float]:
    """Parse CoreMark score string like '95,158.796' to float."""
    if not coremark_str or coremark_str.strip() == "":
        return None
    # Remove commas and convert to float
    try:
        return float(coremark_str.replace(",", ""))
    except ValueError:
        return None


def load_instances(csv_path: str) -> List[Dict]:
    """Load instances from CSV file and parse numeric fields."""
    instances = []
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse numeric fields
            instance = dict(row)
            instance["_memory_gib"] = parse_memory(row.get("Instance Memory", ""))
            instance["_vcpus"] = parse_vcpus(row.get("vCPUs", ""))
            instance["_on_demand_price"] = parse_price(row.get("On Demand", ""))
            instance["_spot_price"] = parse_price(row.get("Linux Spot Minimum cost", ""))
            instance["_reserved_price"] = parse_price(row.get("Linux Reserved cost", ""))
            instance["_coremark"] = parse_coremark(row.get("CoreMark Score", ""))
            instances.append(instance)
    
    return instances


def matches_filters(instance: Dict, args: argparse.Namespace) -> bool:
    """Check if instance matches all specified filters."""
    # vCPU filters
    vcpus = instance.get("_vcpus")
    if vcpus is not None:
        if args.min_vcpus is not None and vcpus < args.min_vcpus:
            return False
        if args.max_vcpus is not None and vcpus > args.max_vcpus:
            return False
    
    # Memory filters
    memory = instance.get("_memory_gib")
    if memory is not None:
        if args.min_memory is not None and memory < args.min_memory:
            return False
        if args.max_memory is not None and memory > args.max_memory:
            return False
    
    # Compute family filter
    if args.compute_family:
        family = instance.get("Compute Family", "").lower()
        if args.compute_family.lower() not in family:
            return False
    
    # Network performance filter
    if args.network:
        network = instance.get("Network Performance", "").lower()
        if args.network.lower() not in network:
            return False
    
    # Instance storage filter
    if args.storage:
        storage = instance.get("Instance Storage", "").lower()
        if args.storage.lower() not in storage:
            return False
    
    # API name pattern filter
    if args.name_pattern:
        api_name = instance.get("API Name", "").lower()
        if args.name_pattern.lower() not in api_name:
            return False
    
    # Price filters
    if args.max_on_demand_price is not None:
        price = instance.get("_on_demand_price")
        if price is not None and price > args.max_on_demand_price:
            return False
    
    if args.max_spot_price is not None:
        price = instance.get("_spot_price")
        if price is not None and price > args.max_spot_price:
            return False
    
    if args.max_reserved_price is not None:
        price = instance.get("_reserved_price")
        if price is not None and price > args.max_reserved_price:
            return False
    
    # CoreMark score filter
    if args.min_coremark is not None:
        coremark = instance.get("_coremark")
        if coremark is not None and coremark < args.min_coremark:
            return False
    
    return True


def format_price(price_str: str) -> str:
    """Extract just the dollar amount from price string like '$0.204 hourly'."""
    if not price_str or price_str.strip() == "":
        return "N/A"
    match = re.search(r"(\$[\d.]+)", price_str)
    if match:
        return match.group(1)
    return price_str


def print_instance(instance: Dict, show_all: bool = False) -> None:
    """Print instance details in a formatted way."""
    if show_all:
        # Print all fields
        print(f"Name: {instance.get('Name', 'N/A')}")
        print(f"  API Name: {instance.get('API Name', 'N/A')}")
        print(f"  vCPUs: {instance.get('vCPUs', 'N/A')}")
        print(f"  Memory: {instance.get('Instance Memory', 'N/A')}")
        print(f"  Compute Family: {instance.get('Compute Family', 'N/A')}")
        print(f"  Network: {instance.get('Network Performance', 'N/A')}")
        print(f"  Storage: {instance.get('Instance Storage', 'N/A')}")
        print(f"  On Demand: {instance.get('On Demand', 'N/A')}")
        print(f"  Spot (min): {instance.get('Linux Spot Minimum cost', 'N/A')}")
        print(f"  Reserved: {instance.get('Linux Reserved cost', 'N/A')}")
        if instance.get('CoreMark Score'):
            print(f"  CoreMark: {instance.get('CoreMark Score', 'N/A')}")
        print()
    else:
        # Compact format
        api_name = instance.get("API Name", "N/A")
        
        # Extract vCPU number
        vcpus = instance.get("_vcpus")
        vcpus_str = str(vcpus) if vcpus is not None else "N/A"
        
        # Extract memory number
        memory = instance.get("_memory_gib")
        memory_str = f"{memory:.1f}" if memory is not None else "N/A"
        
        # Extract price amounts
        on_demand = format_price(instance.get("On Demand", ""))
        spot = format_price(instance.get("Linux Spot Minimum cost", ""))
        
        print(
            f"{api_name:20s} {vcpus_str:10s} {memory_str:12s} "
            f"{on_demand:12s} {spot:12s}"
        )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(
        description="Filter EC2 instances from CSV based on requirements.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find instances with at least 8 vCPUs and 32 GiB memory
  python instance_shopper.py --min-vcpus 8 --min-memory 32

  # Find compute-optimized instances under $1/hour
  python instance_shopper.py --compute-family compute --max-on-demand-price 1.0

  # Find instances with specific network performance
  python instance_shopper.py --network "10 Gigabit" --min-vcpus 16

  # Find instances by name pattern
  python instance_shopper.py --name-pattern "c5" --max-spot-price 0.5
        """,
    )
    
    # vCPU filters
    p.add_argument("--min-vcpus", type=int, help="Minimum number of vCPUs")
    p.add_argument("--max-vcpus", type=int, help="Maximum number of vCPUs")
    
    # Memory filters
    p.add_argument("--min-memory", type=float, help="Minimum memory in GiB")
    p.add_argument("--max-memory", type=float, help="Maximum memory in GiB")
    
    # Compute family filter
    p.add_argument("--compute-family", help="Filter by compute family (e.g., 'General purpose', 'Compute optimized')")
    
    # Network filter
    p.add_argument("--network", help="Filter by network performance (substring match)")
    
    # Storage filter
    p.add_argument("--storage", help="Filter by storage type (e.g., 'EBS only', 'SSD')")
    
    # Name pattern filter
    p.add_argument("--name-pattern", help="Filter by API name pattern (substring match)")
    
    # Price filters
    p.add_argument("--max-on-demand-price", type=float, help="Maximum on-demand price per hour")
    p.add_argument("--max-spot-price", type=float, help="Maximum spot price per hour")
    p.add_argument("--max-reserved-price", type=float, help="Maximum reserved price per hour")
    
    # CoreMark filter
    p.add_argument("--min-coremark", type=float, help="Minimum CoreMark score")
    
    # Output options
    p.add_argument("--csv", default="instances_20260123.csv", help="Path to instances CSV file (default: instances_20260123.csv)")
    p.add_argument("--verbose", "-v", action="store_true", help="Show all fields for each instance")
    p.add_argument("--sort", choices=["name", "vcpus", "memory", "price", "spot"], default="name", help="Sort results by field (default: name)")
    
    return p.parse_args()


def main() -> int:
    args = parse_args()
    
    # Check if CSV file exists
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"ERROR: CSV file not found: {csv_path}", file=sys.stderr)
        return 1
    
    # Load instances
    try:
        instances = load_instances(str(csv_path))
    except Exception as e:
        print(f"ERROR: Failed to load CSV file: {e}", file=sys.stderr)
        return 1
    
    # Filter instances
    filtered = [inst for inst in instances if matches_filters(inst, args)]
    
    if not filtered:
        print("No instances match the specified criteria.", file=sys.stderr)
        return 0
    
    # Sort results
    if args.sort == "vcpus":
        filtered.sort(key=lambda x: x.get("_vcpus") or 0, reverse=True)
    elif args.sort == "memory":
        filtered.sort(key=lambda x: x.get("_memory_gib") or 0, reverse=True)
    elif args.sort == "price":
        filtered.sort(key=lambda x: x.get("_on_demand_price") or float("inf"))
    elif args.sort == "spot":
        filtered.sort(key=lambda x: x.get("_spot_price") or float("inf"))
    else:  # name
        filtered.sort(key=lambda x: x.get("API Name", ""))
    
    # Print header
    if not args.verbose:
        print(f"{'API Name':20s} {'vCPUs':10s} {'Memory (GiB)':12s} {'OnDemand':12s} {'Spot':12s}")
        print("=" * 80)
    
    # Print results
    for instance in filtered:
        print_instance(instance, show_all=args.verbose)
    
    print(f"\nFound {len(filtered)} matching instance(s) out of {len(instances)} total.", file=sys.stderr)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
