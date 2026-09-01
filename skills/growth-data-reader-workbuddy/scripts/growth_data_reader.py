#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def config() -> tuple[str, str]:
    url = os.environ.get("GROWTH_DATA_API_URL", "").strip().rstrip("/")
    token = os.environ.get("GROWTH_DATA_READER_TOKEN", "").strip()
    if not url or not token:
        raise RuntimeError(
            "Persistent Growth Data Reader credentials are unavailable."
        )
    return url, token


def read_body(path: str | None):
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    if sys.stdin.isatty():
        raise RuntimeError("Provide --request FILE or pipe a JSON body to stdin.")
    return json.load(sys.stdin)


def call(path: str, *, method: str, body=None):
    base_url, token = config()
    headers = {
        "Accept": "application/json",
        "X-GROWTH-DATA-TOKEN": token,
    }
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}{path}", data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gateway returned HTTP {exc.code}: {message}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Cannot reach Gateway: {exc.reason}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Growth Data Reader client")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--profile", action="store_true")
    modes.add_argument("--ga4", action="store_true")
    modes.add_argument("--gsc", action="store_true")
    modes.add_argument("--gsc-inspect", action="store_true")
    modes.add_argument("--gsc-sitemaps", action="store_true")
    modes.add_argument("--ads", action="store_true")
    parser.add_argument("--request")
    args = parser.parse_args()
    try:
        if args.profile:
            result = call("/v1/profile", method="GET")
        elif args.gsc_sitemaps:
            result = call("/v1/gsc/sitemaps", method="GET")
        else:
            if args.ga4:
                path = "/v1/ga4/report"
            elif args.gsc:
                path = "/v1/gsc/query"
            elif args.gsc_inspect:
                path = "/v1/gsc/inspect"
            else:
                path = "/v1/google-ads/query"
            result = call(path, method="POST", body=read_body(args.request))
    except (RuntimeError, json.JSONDecodeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
