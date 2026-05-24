import datetime as dt
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "index_zone_usage.py"
SPEC = importlib.util.spec_from_file_location("index_zone_usage", MODULE_PATH)
usage = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = usage
SPEC.loader.exec_module(usage)


def make_line(
    *,
    timestamp="22/May/2026:22:52:54 +0000",
    remote_ip="120.225.2.100",
    operation="REST.GET.OBJECT",
    key="kraken/k2_standard_20260226.tar.gz",
    status="206",
    bytes_sent="8388608",
    object_size="16777216",
    request_id="REQ1",
):
    return (
        "5481e6e8fc7823993e0d6cb1f6030bbb4d29c3e64d2bd7648fea1acc10842a4f "
        f"genome-idx [{timestamp}] {remote_ip} - {request_id} {operation} {key} "
        f'"GET /{key} HTTP/1.1" {status} - {bytes_sent} {object_size} 3244 159 '
        '"-" "aws-cli/2.34.51 md/command#s3.cp" - '
        "hostid SigV4 TLS_AES_128_GCM_SHA256 - genome-idx.s3.amazonaws.com "
        "TLSv1.3 - - -"
    )


class S3AccessLogTests(unittest.TestCase):
    def test_parse_s3_access_log_line(self):
        record = usage.parse_s3_access_log_line(make_line())

        self.assertEqual(record.bucket, "genome-idx")
        self.assertEqual(record.operation, "REST.GET.OBJECT")
        self.assertEqual(record.key, "kraken/k2_standard_20260226.tar.gz")
        self.assertEqual(record.prefix, "kraken")
        self.assertEqual(record.http_status, 206)
        self.assertEqual(record.bytes_sent, 8388608)
        self.assertEqual(record.object_size, 16777216)
        self.assertEqual(record.time.year, 2026)

    def test_summarize_logs_counts_raw_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.log"
            path.write_text(make_line() + "\n" + make_line(request_id="REQ2") + "\n")
            args = type(
                "Args",
                (),
                {
                    "inputs": [str(path)],
                    "cache_dir": None,
                    "start": None,
                    "end": None,
                    "skip_bad_lines": False,
                },
            )()

            rows = usage.summarize_logs(args)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["raw_requests"], 2)
        self.assertEqual(rows[0]["bytes_sent"], 16777216)
        self.assertEqual(rows[0]["max_object_size"], 16777216)

    def test_coalesce_range_gets_into_one_complete_session(self):
        records = [
            usage.parse_s3_access_log_line(make_line(request_id="REQ1")),
            usage.parse_s3_access_log_line(
                make_line(timestamp="22/May/2026:22:53:01 +0000", request_id="REQ2")
            ),
        ]

        sessions = usage.coalesce_download_sessions(records, window=dt.timedelta(minutes=15))

        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].raw_get_requests, 2)
        self.assertEqual(sessions[0].bytes_sent, 16777216)
        self.assertTrue(sessions[0].is_complete(0.95))

    def test_coalesce_splits_sessions_after_window(self):
        records = [
            usage.parse_s3_access_log_line(make_line(request_id="REQ1")),
            usage.parse_s3_access_log_line(
                make_line(timestamp="22/May/2026:23:20:00 +0000", request_id="REQ2")
            ),
        ]

        sessions = usage.coalesce_download_sessions(records, window=dt.timedelta(minutes=15))

        self.assertEqual(len(sessions), 2)


if __name__ == "__main__":
    unittest.main()
