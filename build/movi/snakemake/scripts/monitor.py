#!/usr/bin/env python3
"""Run a command under peak-resource monitoring, independent of any external
(e.g. ssh) observer, so a stage's footprint is captured even when nobody is
watching live.

Records to a small TSV (one header + one data row):
  label, exit, wall_s, peak_rss_gib, cpu_core_s, mean_cpu_cores, peak_cpu_cores,
  peak_disk_bytes, peak_disk_gib, watch

Measurement:
  * peak RSS   -- summed over the whole process SUBTREE rooted at the command
                  (walks /proc ppid links each sample), so worker children /
                  dispatched binaries are included. Tracks the max.
  * CPU        -- authoritative total CPU seconds for the command AND all
                  descendants it reaped, via os.wait4() rusage (ru_utime+
                  ru_stime); mean_cpu_cores = cpu_core_s / wall_s. A best-effort
                  peak_cpu_cores also comes from per-sample subtree jiffy deltas.
  * peak disk  -- max summed `du -sB1` of the --watch dirs (transient temp
                  footprint, e.g. grlBWT grltmp), sampled on a slower cadence
                  because du over a multi-TB tree is expensive.

Usage:
  monitor.py --label L --out FILE [--watch DIR]... [--interval S]
             [--disk-interval S] -- CMD [ARG...]

Exits with CMD's exit status. All monitoring is best-effort: a sampling error
never disturbs or fails the wrapped command. The command runs in the wrapper's
own session/process-group (NOT detached), so Slurm/Snakemake cancellation still
propagates to it normally.
"""
import argparse
import os
import subprocess
import sys
import time

PAGE = os.sysconf("SC_PAGE_SIZE")
CLK = os.sysconf("SC_CLK_TCK")


def _stat_fields(pid):
    """Return /proc/<pid>/stat fields from field 3 onward (0-indexed: fields[0]
    is field 3 = state), robust to spaces/parens in comm. None on failure."""
    try:
        with open("/proc/%s/stat" % pid) as fh:
            data = fh.read()
    except OSError:
        return None
    rp = data.rfind(")")
    if rp < 0:
        return None
    return data[rp + 2:].split()


def _ppid_map():
    m = {}
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        f = _stat_fields(name)
        if f:  # field 4 (ppid) -> fields[1]
            try:
                m[int(name)] = int(f[1])
            except (ValueError, IndexError):
                pass
    return m


def _subtree(root, ppid_map):
    children = {}
    for pid, ppid in ppid_map.items():
        children.setdefault(ppid, []).append(pid)
    seen, stack = set(), [root]
    while stack:
        p = stack.pop()
        if p in seen:
            continue
        seen.add(p)
        stack.extend(children.get(p, ()))
    return seen


def _rss_kb(pid):
    try:
        with open("/proc/%s/statm" % pid) as fh:
            resident_pages = int(fh.read().split()[1])
        return resident_pages * PAGE // 1024
    except (OSError, IndexError, ValueError):
        return 0


def _cpu_jiffies(fields):
    # utime = field 14 -> fields[11]; stime = field 15 -> fields[12]
    try:
        return int(fields[11]) + int(fields[12])
    except (IndexError, ValueError):
        return 0


def _du_bytes(path):
    try:
        r = subprocess.run(["du", "-sB1", path], capture_output=True,
                           text=True, timeout=900)
        parts = r.stdout.split()
        if r.returncode == 0 and parts:
            return int(parts[0])
    except Exception:
        pass
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="stage")
    ap.add_argument("--out", required=True)
    ap.add_argument("--watch", action="append", default=[])
    ap.add_argument("--interval", type=float, default=30.0,
                    help="RSS/CPU sampling period (s)")
    ap.add_argument("--disk-interval", type=float, default=300.0,
                    help="du sampling period (s); du over big trees is costly")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()

    cmd = a.cmd[1:] if (a.cmd and a.cmd[0] == "--") else a.cmd
    if not cmd:
        sys.stderr.write("monitor.py: no command given\n")
        return 2

    out_dir = os.path.dirname(os.path.abspath(a.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    peak_rss_kb = 0
    peak_disk = 0
    peak_cpu_cores = 0.0
    last_j = None
    last_t = None
    next_disk = 0.0

    def sample_rss_cpu():
        nonlocal peak_rss_kb, peak_cpu_cores, last_j, last_t
        ppm = _ppid_map()
        tree = _subtree(proc.pid, ppm)
        rss = 0
        jiff = 0
        for p in tree:
            rss += _rss_kb(p)
            f = _stat_fields(p)
            if f:
                jiff += _cpu_jiffies(f)
        if rss > peak_rss_kb:
            peak_rss_kb = rss
        now = time.time()
        if last_j is not None and now > last_t:
            cores = (jiff - last_j) / CLK / (now - last_t)
            if cores > peak_cpu_cores:
                peak_cpu_cores = cores
        last_j, last_t = jiff, now

    def sample_disk():
        nonlocal peak_disk
        tot = 0
        for d in a.watch:
            if os.path.exists(d):
                tot += _du_bytes(d)
        if tot > peak_disk:
            peak_disk = tot

    start = time.time()
    # Own session preserved (no setsid): cancellation still reaches the child.
    proc = subprocess.Popen(cmd)

    status = 0
    while True:
        wpid, status, ru = os.wait4(proc.pid, os.WNOHANG)
        if wpid == proc.pid:
            break
        try:
            sample_rss_cpu()
        except Exception:
            pass
        if a.watch and time.time() >= next_disk:
            try:
                sample_disk()
            except Exception:
                pass
            next_disk = time.time() + a.disk_interval
        time.sleep(a.interval)

    # Keep Popen from trying to reap again.
    proc.returncode = os.waitstatus_to_exitcode(status)
    wall = max(time.time() - start, 1e-9)
    # One last disk sample (peak may occur right before exit for some stages).
    if a.watch:
        try:
            sample_disk()
        except Exception:
            pass

    cpu_core_s = ru.ru_utime + ru.ru_stime          # incl. reaped descendants
    mean_cores = cpu_core_s / wall
    peak_rss_gib = peak_rss_kb / 1048576.0
    peak_disk_gib = peak_disk / (1024.0 ** 3)
    rc = proc.returncode

    row = [
        a.label,
        str(rc),
        "%.1f" % wall,
        "%.2f" % peak_rss_gib,
        "%.1f" % cpu_core_s,
        "%.2f" % mean_cores,
        "%.2f" % peak_cpu_cores,
        str(peak_disk),
        "%.2f" % peak_disk_gib,
        ",".join(a.watch) if a.watch else "-",
    ]
    header = ["label", "exit", "wall_s", "peak_rss_gib", "cpu_core_s",
              "mean_cpu_cores", "peak_cpu_cores", "peak_disk_bytes",
              "peak_disk_gib", "watch"]
    try:
        with open(a.out, "w") as fh:
            fh.write("\t".join(header) + "\n")
            fh.write("\t".join(row) + "\n")
    except OSError as e:
        sys.stderr.write("monitor.py: could not write %s: %s\n" % (a.out, e))

    sys.stderr.write(
        "[monitor] %s: wall=%.0fs peak_rss=%.1fGiB mean_cpu=%.1f cores "
        "peak_cpu=%.1f cores peak_disk=%.1fGiB exit=%d\n"
        % (a.label, wall, peak_rss_gib, mean_cores, peak_cpu_cores,
           peak_disk_gib, rc))
    return rc


if __name__ == "__main__":
    sys.exit(main())
