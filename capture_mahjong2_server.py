#!/usr/bin/env python3
"""Capture Mahjong2 server bet responses into uploadable JSONL.

Default mode is dry-run. Add --send to perform real server requests.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_ENDPOINT = "https://ceshislot.osshaiwai.com/mahjong2/mahjong2Bet"
DEFAULT_TOKEN = "436475c81b51e6893c740657870f86b7"
CONTINUE_STATES = {4, 21, 22}
DEFAULT_HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://fish-games.s3.amazonaws.com",
    "Referer": "https://fish-games.s3.amazonaws.com/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
    ),
}


def _float_or_int(value: float) -> int | float:
    return int(value) if value == int(value) else value


def _new_spin_id(sequence: int) -> str:
    return f"{random.randint(100, 999)}{int(time.time() * 1000)}{sequence % 1000:03d}"


def _load_har_template(path: Path) -> tuple[str, dict[str, Any], dict[str, str]]:
    har = json.loads(path.read_text(encoding="utf-8"))
    for entry in har.get("log", {}).get("entries", []):
        request = entry.get("request") or {}
        if request.get("method") != "POST" or "mahjong2Bet" not in request.get("url", ""):
            continue
        post_data = request.get("postData") or {}
        text = post_data.get("text") or ""
        if not text.strip():
            continue
        try:
            body = json.loads(text)
        except json.JSONDecodeError:
            continue
        if not isinstance(body, dict):
            continue
        headers = {
            item.get("name"): item.get("value")
            for item in request.get("headers", [])
            if item.get("name") in {"Origin", "Referer", "User-Agent"}
        }
        return request.get("url") or DEFAULT_ENDPOINT, body, {k: v for k, v in headers.items() if v}
    raise ValueError(f"no POST mahjong2Bet request with JSON body found in {path}")


def _request_body(args: argparse.Namespace, template: dict[str, Any] | None, sequence: int) -> dict[str, Any]:
    body = dict(template or {})
    token = args.token or body.get("token") or os.environ.get("MAHJONG2_TOKEN") or DEFAULT_TOKEN
    body.update({
        "token": token,
        "chip": _float_or_int(args.chip),
        "size": _float_or_int(args.size),
        "level": args.level,
        "symbol": args.symbol,
        "lotteryId": args.lottery_id,
        "buyFree": args.buy_free,
        "spinId": _new_spin_id(sequence),
    })
    return body


def _post_json(endpoint: str, headers: dict[str, str], body: dict[str, Any], timeout: float) -> dict[str, Any]:
    payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(endpoint, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {text[:500]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"request failed: {exc}") from exc

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"response is not JSON: {text[:500]}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"response root is not object: {text[:500]}")
    return data


def _continue_state(response: dict[str, Any]) -> int | None:
    data = response.get("data")
    if not isinstance(data, dict):
        return None
    try:
        return int(data.get("nst"))
    except (TypeError, ValueError):
        return None


def _response_line(response: dict[str, Any]) -> str:
    data = response.get("data")
    if isinstance(data, dict):
        return json.dumps({"data": data}, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(response, ensure_ascii=False, separators=(",", ":"))


def capture(args: argparse.Namespace) -> int:
    endpoint = args.endpoint
    template: dict[str, Any] | None = None
    headers = dict(DEFAULT_HEADERS)
    if args.from_har:
        endpoint, template, har_headers = _load_har_template(Path(args.from_har))
        headers.update(har_headers)

    output = Path(args.output or f"xxbet_capture_mahjong2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    first_body = _request_body(args, template, 1)

    if not args.send:
        print("DRY RUN: no server request was sent.")
        print(f"endpoint: {endpoint}")
        print(f"output: {output}")
        target = args.target_responses or f"{args.spins} paid spin chains"
        print(f"target: {target}, max_chain_requests: {args.max_chain_requests}")
        print("first request body:")
        print(json.dumps(first_body, ensure_ascii=False, indent=2))
        print("Add --send to perform real requests. This may consume test account balance.")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    total_requests = 0
    paid_spin = 0
    with output.open("w", encoding="utf-8") as file:
        while True:
            if args.target_responses is None and paid_spin >= args.spins:
                break
            if args.target_responses is not None and total_requests >= args.target_responses:
                break
            paid_spin += 1
            chain_requests = 0
            while True:
                total_requests += 1
                chain_requests += 1
                body = _request_body(args, template, total_requests)
                response = _post_json(endpoint, headers, body, args.timeout)
                file.write(_response_line(response) + "\n")

                data = response.get("data") if isinstance(response, dict) else None
                if isinstance(data, dict):
                    print(
                        f"line={total_requests} paid_spin={paid_spin} chain_request={chain_requests} "
                        f"sid={data.get('sid')} st={data.get('st')} nst={data.get('nst')} "
                        f"tb={data.get('tb')} aw={data.get('aw')}"
                    )
                else:
                    print(f"line={total_requests} paid_spin={paid_spin} chain_request={chain_requests} response_code={response.get('code')}")

                nst = _continue_state(response)
                if nst not in CONTINUE_STATES:
                    break
                if chain_requests >= args.max_chain_requests:
                    raise RuntimeError(
                        f"chain exceeded --max-chain-requests={args.max_chain_requests}; "
                        "stop to avoid runaway capture"
                    )
                time.sleep(args.interval)
            time.sleep(args.interval)

    print(f"wrote {total_requests} responses from {paid_spin} paid spin chains to {output}")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture Mahjong2 server responses into uploadable txt.")
    parser.add_argument("--from-har", help="Use first POST mahjong2Bet request in a HAR as template.")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--token", default=os.environ.get("MAHJONG2_TOKEN"))
    parser.add_argument("--spins", type=int, default=1, help="Number of paid spin chains to capture.")
    parser.add_argument("--target-responses", type=int, help="Capture until at least this many response lines, then finish current chain.")
    parser.add_argument("--max-chain-requests", type=int, default=80)
    parser.add_argument("--chip", type=float, default=40.0)
    parser.add_argument("--size", type=float, default=2.0)
    parser.add_argument("--level", type=int, default=1)
    parser.add_argument("--symbol", type=int, default=20)
    parser.add_argument("--lottery-id", type=int, default=1)
    parser.add_argument("--buy-free", action="store_true")
    parser.add_argument("--interval", type=float, default=0.2)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--output")
    parser.add_argument("--send", action="store_true", help="Actually send requests to server.")
    return parser.parse_args()


def main() -> int:
    return capture(_parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
