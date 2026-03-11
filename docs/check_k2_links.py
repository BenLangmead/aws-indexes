#!/usr/bin/env python3
"""
Check that all https:// URLs in k2.md are accessible.

Usage:
    python check_k2_links.py [k2.md]
    python check_k2_links.py --verbose [k2.md]

Uses HEAD requests where possible (fallback to GET for 405).
Exits with 0 if all URLs are accessible, 1 otherwise.
"""

from __future__ import annotations

import argparse
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def find_https_urls(text: str) -> list[str]:
    """Extract all https:// URLs from text. Deduplicate and preserve order."""
    # Match https:// and then characters that are valid in URLs (stop at ), ], space, newline, ", `, etc.)
    pattern = r"https://[^\s\)\]\"\s<>`]+"
    urls = re.findall(pattern, text)
    seen = set()
    unique = []
    for u in urls:
        # Strip trailing markdown/sentence punctuation only (don't strip . which is in .tar.gz etc.)
        u = u.rstrip("),;:\"'")
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def check_url(url: str, timeout: float = 15.0) -> tuple[str, bool, str]:
    """
    Return (url, ok, message). Uses HEAD first, then GET if 405.
    """
    try:
        req = Request(url, method="HEAD")
        req.add_header("User-Agent", "check_k2_links.py (link checker)")
        with urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            if 200 <= code < 400:
                return (url, True, f"{code}")
            return (url, False, f"HTTP {code}")
    except HTTPError as e:
        if e.code == 405:
            # Method Not Allowed; try GET
            try:
                req = Request(url)
                req.add_header("User-Agent", "check_k2_links.py (link checker)")
                with urlopen(req, timeout=timeout) as resp:
                    code = resp.getcode()
                    if 200 <= code < 400:
                        return (url, True, f"{code}")
                    return (url, False, f"HTTP {code}")
            except (HTTPError, URLError) as e2:
                return (url, False, str(e2).split("\n")[0])
        return (url, False, f"HTTP {e.code} {e.reason}")
    except URLError as e:
        return (url, False, str(e.reason or e).split("\n")[0])
    except Exception as e:
        return (url, False, str(e).split("\n")[0])


def main() -> int:
    parser = argparse.ArgumentParser(description="Check https:// URLs in k2.md")
    parser.add_argument(
        "file",
        nargs="?",
        default="k2.md",
        help="Markdown file to check (default: k2.md)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print status for every URL",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="Request timeout in seconds (default: 15)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Concurrent requests (default: 8)",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"Error: not a file: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    urls = find_https_urls(text)
    if not urls:
        print("No https:// URLs found.", file=sys.stderr)
        return 0

    print(f"Checking {len(urls)} unique URL(s) from {path}...", file=sys.stderr)
    failed = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(check_url, u, args.timeout): u for u in urls}
        for future in as_completed(futures):
            url, ok, msg = future.result()
            if ok:
                if args.verbose:
                    print(f"  OK {msg}: {url}", file=sys.stderr)
            else:
                failed.append((url, msg))
                print(f"  FAIL: {url}", file=sys.stderr)
                print(f"        {msg}", file=sys.stderr)

    if failed:
        print(f"\n{len(failed)} of {len(urls)} URL(s) failed.", file=sys.stderr)
        return 1
    print(f"All {len(urls)} URL(s) are accessible.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
