#!/usr/bin/env python3
"""
Extract and verify links in local site sources under docs/ (not the built _site tree).

Scans:
  - *.md excluding _site/
  - _layouts/*.html

- http(s):// and ftp:// — HEAD (fallback GET on 405), concurrent. Paths are re-encoded
  before fetch so literal "+" in object keys (e.g. Amazon S3) is sent as "%2B".

- Relative / site-root paths — resolved against docs/; must point at an existing file
  (tries path as given, then .md, then directory/index.md)
- s3:// — optional HEAD via virtual-host HTTPS (--check-s3); otherwise reported as skipped
- ftp:// — off by default (--check-ftp); many public FTP servers limit concurrent sessions.

Skips: mailto:, javascript:, data:, tel:, pure #fragments, URLs inside fenced ``` code blocks,
example hosts (localhost, …), and URLs containing Liquid ({{).
By default, `docs/skills/` is excluded; use --include-skills to scan it.

`--request-delay SECONDS` enforces a minimum spacing between outbound requests (reduces
throttling / "connection reset" under parallel `--workers`). Transient connection errors and
HTTP 429 are retried with backoff.

Usage:
  cd docs && python3 check_site_links.py
  python3 docs/check_site_links.py --root docs
  python3 check_site_links.py --verbose --workers 12
"""

from __future__ import annotations

import argparse
import re
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse, urlsplit, urlunsplit
from urllib.request import Request, urlopen


# https:// or http:// or ftp:// (same trimming as check_k2_links.py).
# Do not run this on raw files: use text with fenced code blocks removed so
# shell globs like curl ...7z.[001-071] are not parsed as URLs.
_HREF_ABSOLUTE = re.compile(
    r"(?:https?|ftp)://[^\s\)\]\"'<>`]+", re.IGNORECASE
)
# Markdown [text](url) — url must not be liquid
_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# <a href="...">
_HTML_HREF = re.compile(
    r"""href\s*=\s*(['"])(.*?)\1""", re.IGNORECASE | re.DOTALL
)
# Reference-style: [label]: url  or  [label]: <url>
_MD_REF = re.compile(
    r"^\s{0,3}\[[^\]]+\]:\s*(?:<([^>\s]+)>|(\S+))",
    re.MULTILINE,
)

SKIP_DIR_NAMES = frozenset({"_site", ".jekyll-cache"})

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 check_site_links/1.0"
)


def fenced_code_spans(text: str) -> list[tuple[int, int]]:
    return [
        (m.start(), m.end())
        for m in re.finditer(
            r"^```.*?^```", text, flags=re.MULTILINE | re.DOTALL
        )
    ]


def inside_any_span(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= pos < end for start, end in spans)


def normalize_external_url(u: str) -> str:
    u = u.rstrip("),;:\"'")
    return unquote(u)


def url_for_fetch(url: str) -> str:
    """
    Rebuild URL with path properly percent-encoded. unquote+quote ensures characters
    like '+' (common in S3 keys) are sent as %2B, which S3 expects for literal plus.
    """
    u = url.strip()
    parts = urlsplit(u)
    scheme = (parts.scheme or "").lower()
    if scheme not in ("http", "https", "ftp"):
        return u
    path = quote(unquote(parts.path), safe="/")
    return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def transient_connection_error(msg: str) -> bool:
    m = msg.lower().replace(" ", "")
    return any(
        p in m
        for p in (
            "connectionreset",
            "resetbypeer",
            "econnreset",
            "brokenpipe",
            "connectionaborted",
        )
    )


def should_skip_scheme(url: str) -> bool:
    lowered = url.lower()
    return lowered.startswith(
        ("mailto:", "javascript:", "data:", "tel:", "#")
    )


def is_liquid(url: str) -> bool:
    return "{{" in url or "{%" in url


def find_markdown_files(root: Path, include_skills: bool) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("*.md"):
        if any(part in SKIP_DIR_NAMES for part in p.parts):
            continue
        if not include_skills:
            try:
                p.relative_to(root / "skills")
                continue
            except ValueError:
                pass
        out.append(p)
    out.sort()
    return out


def find_layout_files(root: Path) -> list[Path]:
    layouts = root / "_layouts"
    if not layouts.is_dir():
        return []
    return sorted(layouts.glob("*.html"))


def extract_urls_with_lines(text: str) -> list[tuple[int, str]]:
    """Return (line_number, url) for each occurrence."""
    found: list[tuple[int, str]] = []
    spans = fenced_code_spans(text)

    def line_no(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    for m in _HREF_ABSOLUTE.finditer(text):
        if inside_any_span(m.start(), spans):
            continue
        found.append((line_no(m.start()), normalize_external_url(m.group(0))))

    for m in _MD_LINK.finditer(text):
        if inside_any_span(m.start(), spans):
            continue
        u = m.group(1).strip()
        if is_liquid(u):
            continue
        u = u.split()[0] if u else ""
        if not u or u.startswith("#"):
            continue
        found.append((line_no(m.start()), u))

    for m in _HTML_HREF.finditer(text):
        if inside_any_span(m.start(), spans):
            continue
        u = m.group(2).strip()
        if is_liquid(u):
            continue
        if not u or u.startswith("#"):
            continue
        found.append((line_no(m.start()), u))

    for m in _MD_REF.finditer(text):
        if inside_any_span(m.start(), spans):
            continue
        u = (m.group(1) or m.group(2) or "").strip()
        if not u or is_liquid(u):
            continue
        found.append((line_no(m.start()), u))

    return found


def s3_to_https_virtual(host: str, key: str) -> str:
    host = host.strip("/")
    key = key.lstrip("/")
    return f"https://{host}.s3.amazonaws.com/{key}"


def check_url(
    url: str,
    timeout: float,
    pre_request: Callable[[], None] | None = None,
) -> tuple[bool, str]:
    fetch_url = url_for_fetch(url)

    def do_get() -> tuple[bool, str]:
        req = Request(fetch_url)
        req.add_header("User-Agent", UA)
        with urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            if code is None:
                return (True, "ok")
            if 200 <= code < 400:
                return (True, f"GET {code}")
            return (False, f"HTTP {code}")

    def one_round() -> tuple[bool, str]:
        if pre_request:
            pre_request()
        try:
            req = Request(fetch_url, method="HEAD")
            req.add_header("User-Agent", UA)
            with urlopen(req, timeout=timeout) as resp:
                code = resp.getcode()
                if code is None:
                    return (True, "ok")
                if 200 <= code < 400:
                    return (True, f"{code}")
                return (False, f"HTTP {code}")
        except HTTPError as e:
            if e.code == 405:
                try:
                    return do_get()
                except (HTTPError, URLError) as e2:
                    return (False, str(e2).split("\n")[0])
            if e.code in (403, 501):
                try:
                    return do_get()
                except HTTPError as e2:
                    return (False, f"HTTP {e2.code} {e2.reason}")
                except URLError as e2:
                    return (False, str(e2.reason or e2).split("\n")[0])
            return (False, f"HTTP {e.code} {e.reason}")
        except URLError as e:
            return (False, str(e.reason or e).split("\n")[0])
        except Exception as e:
            return (False, str(e).split("\n")[0])

    last_msg = "unknown"
    for round_i in range(5):
        ok, msg = one_round()
        last_msg = msg
        if ok:
            return (True, msg)
        if "429" in msg:
            time.sleep(2.0 * (round_i + 1))
            continue
        if transient_connection_error(msg):
            time.sleep(min(8.0, 0.35 * (2**round_i)))
            continue
        return (False, msg)
    return (False, last_msg)


def skip_external_url(url: str) -> bool:
    """Skip example / placeholder hosts."""
    try:
        parsed = urlparse(url)
    except Exception:
        return True
    host = (parsed.hostname or "").lower()
    if host in ("localhost", "127.0.0.1", "0.0.0.0"):
        return True
    if host in ("...", "example.com", "www.example.com"):
        return True
    return False


def resolve_internal(
    raw: str, source_file: Path, docs_root: Path
) -> tuple[Path | None, str]:
    """
    Return (resolved_path, error_message). resolved_path set if file exists.
    """
    raw = raw.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()
    path_part, _, _frag = raw.partition("#")
    path_part = path_part.strip()
    if not path_part:
        return (None, "")

    if path_part.startswith("/"):
        rel = path_part.lstrip("/")
        candidate = (docs_root / rel).resolve()
    else:
        candidate = (source_file.parent / path_part).resolve()

    try:
        candidate.relative_to(docs_root.resolve())
    except ValueError:
        return (None, "resolves outside docs root")

    if candidate.is_file():
        return (candidate, "")

    md = candidate.with_suffix(".md")
    if md.is_file():
        return (md, "")

    idx = candidate / "index.md"
    if idx.is_file():
        return (idx, "")

    # bare name without suffix: k2 -> k2.md at docs root
    if not candidate.suffix and candidate.parent == docs_root:
        alt = docs_root / f"{candidate.name}.md"
        if alt.is_file():
            return (alt, "")

    return (None, f"missing file: {candidate}")


def classify(
    raw: str,
) -> tuple[str, str | None]:
    """
    Return (kind, normalized_url_for_fetch).
    kind is 'external' | 'internal' | 's3' | 'skip'
    """
    if is_liquid(raw):
        return ("skip", None)
    raw = raw.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()

    path_part, _, frag = raw.partition("#")
    path_part = path_part.strip()

    if not path_part:
        return ("skip", None)
    if should_skip_scheme(path_part):
        return ("skip", None)

    lowered = path_part.lower()
    if lowered.startswith("s3://"):
        rest = path_part[5:]
        if "/" not in rest:
            return ("s3", None)
        bucket, _, key = rest.partition("/")
        return ("s3", s3_to_https_virtual(bucket, key))

    if lowered.startswith(("http://", "https://", "ftp://")):
        return ("external", normalize_external_url(path_part))

    return ("internal", None)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Check links in local docs/ sources (excludes _site/)."
    )
    ap.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Site source root (default: parent directory of this script)",
    )
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--timeout", type=float, default=25.0)
    ap.add_argument("--workers", type=int, default=4, help="Concurrent requests (default: 4)")
    ap.add_argument(
        "--check-s3",
        action="store_true",
        help="HEAD check s3:// URLs via https://bucket.s3.amazonaws.com/key",
    )
    ap.add_argument(
        "--no-network",
        action="store_true",
        help="Only verify internal paths; skip HTTP/FTP/S3 checks",
    )
    ap.add_argument(
        "--include-skills",
        action="store_true",
        help="Also scan docs/skills/**/*.md (off by default)",
    )
    ap.add_argument(
        "--check-ftp",
        action="store_true",
        help="Verify ftp:// links (off by default; servers often rate-limit)",
    )
    ap.add_argument(
        "--request-delay",
        type=float,
        default=0.0,
        metavar="SEC",
        help="Minimum spacing between outbound requests (0=off; e.g. 0.2 if throttled)",
    )
    args = ap.parse_args()

    script_dir = Path(__file__).resolve().parent
    docs_root = (args.root if args.root is not None else script_dir).resolve()
    if not docs_root.is_dir():
        print(f"Error: not a directory: {docs_root}", file=sys.stderr)
        return 2

    files = find_markdown_files(docs_root, args.include_skills) + find_layout_files(
        docs_root
    )
    if not files:
        print("No source files found.", file=sys.stderr)
        return 0

    # (source_file, line, raw) per occurrence
    occurrences: list[tuple[Path, int, str]] = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        for line, raw in extract_urls_with_lines(text):
            occurrences.append((f, line, raw))

    external_by_url: dict[str, list[tuple[Path, int]]] = defaultdict(list)
    internal_checks: list[tuple[Path, int, str]] = []
    skipped_s3: list[tuple[Path, int, str]] = []
    skipped_ftp: list[tuple[Path, int, str]] = []

    for src, line, raw in occurrences:
        kind, remote = classify(raw)
        if kind == "skip":
            continue
        if kind == "internal":
            internal_checks.append((src, line, raw))
            continue
        if kind == "s3":
            if args.check_s3 and remote and not args.no_network:
                external_by_url[remote].append((src, line))
            else:
                skipped_s3.append((src, line, raw))
            continue
        if kind == "external":
            if args.no_network:
                continue
            assert remote is not None
            if skip_external_url(remote):
                if args.verbose:
                    print(
                        f"  SKIP example-host {src.relative_to(docs_root)}:{line}: {remote}",
                        file=sys.stderr,
                    )
                continue
            if remote.lower().startswith("ftp:") and not args.check_ftp:
                skipped_ftp.append((src, line, raw))
                continue
            external_by_url[remote].append((src, line))

    failures: list[str] = []

    for src, line, raw in internal_checks:
        resolved, err = resolve_internal(raw, src, docs_root)
        if resolved is not None:
            if args.verbose:
                rel = resolved.relative_to(docs_root)
                print(f"  OK internal {src.relative_to(docs_root)}:{line} -> {rel}", file=sys.stderr)
        else:
            msg = f"{src.relative_to(docs_root)}:{line}: broken internal link {raw!r} ({err})"
            failures.append(msg)
            print(f"  FAIL {msg}", file=sys.stderr)

    if skipped_s3 and args.verbose:
        for src, line, raw in skipped_s3:
            print(
                f"  SKIP s3 {src.relative_to(docs_root)}:{line}: {raw}",
                file=sys.stderr,
            )
    elif skipped_s3:
        print(
            f"Note: {len(skipped_s3)} s3:// link(s) skipped (use --check-s3 to verify).",
            file=sys.stderr,
        )

    if skipped_ftp and args.verbose:
        for src, line, raw in skipped_ftp:
            print(
                f"  SKIP ftp {src.relative_to(docs_root)}:{line}: {raw}",
                file=sys.stderr,
            )
    elif skipped_ftp:
        print(
            f"Note: {len(skipped_ftp)} ftp:// link(s) skipped (use --check-ftp to verify).",
            file=sys.stderr,
        )

    throttle_lock = threading.Lock()
    throttle_last: list[float] = [0.0]

    def pre_request() -> None:
        with throttle_lock:
            now = time.monotonic()
            wait = args.request_delay - (now - throttle_last[0])
            if wait > 0:
                time.sleep(wait)
            throttle_last[0] = time.monotonic()

    pre_cb: Callable[[], None] | None = pre_request if args.request_delay > 0 else None

    if external_by_url:
        print(
            f"Checking {len(external_by_url)} unique remote URL(s) "
            f"({sum(len(v) for v in external_by_url.values())} reference(s))...",
            file=sys.stderr,
        )
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
            futures = {
                ex.submit(check_url, url, args.timeout, pre_cb): url
                for url in external_by_url
            }
            for fut in as_completed(futures):
                url = futures[fut]
                ok, msg = fut.result()
                if ok:
                    if args.verbose:
                        for src, line in external_by_url[url]:
                            print(
                                f"  OK {msg} {src.relative_to(docs_root)}:{line}: {url}",
                                file=sys.stderr,
                            )
                else:
                    for src, line in external_by_url[url]:
                        m = f"{src.relative_to(docs_root)}:{line}: {url} -> {msg}"
                        failures.append(m)
                        print(f"  FAIL {m}", file=sys.stderr)

    if failures:
        print(f"\n{len(failures)} problem(s).", file=sys.stderr)
        return 1
    print("All checked links OK.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
