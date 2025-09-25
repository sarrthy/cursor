import argparse
import csv
import json
from pathlib import Path
from typing import List

from .config import load_config
from .serp import fetch_ads
from .extract import collect_ref_codes_from_ads
from .extract import BYBIT_HOSTS


def parse_args():
    cfg = load_config()
    parser = argparse.ArgumentParser(description="Bybit ad scanner")
    parser.add_argument("--keyword", "-k", default=cfg.default_keyword)
    parser.add_argument("--provider", default=cfg.serp_provider, choices=["serper", "serpapi"])
    parser.add_argument("--engine", default=cfg.default_engine)
    parser.add_argument("--market", default=cfg.default_market)
    parser.add_argument("--limit", type=int, default=1, help="How many ads to scan (first N)")
    parser.add_argument(
        "--format",
        default="json",
        help="Comma-separated output formats: json,csv",
    )
    parser.add_argument("--out", default="bybit_ads", help="Output basename without extension")
    return parser.parse_args()


def write_json(path: Path, data) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        # create empty with headers
        rows = []
        fieldnames = ["ref_code", "final_url"]
    else:
        fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    args = parse_args()
    cfg = load_config()

    ads = fetch_ads(
        provider=args.provider,
        keyword=args.keyword,
        market=args.market,
        engine=args.engine,
        serper_api_key=cfg.serper_api_key,
        serpapi_api_key=cfg.serpapi_api_key,
    )

    ref_pairs = collect_ref_codes_from_ads(ads, limit=args.limit)
    records = [
        {"ref_code": ref_code, "final_url": final_url}
        for ref_code, final_url in ref_pairs
    ]

    first_ad_link = ads[0]["link"] if ads else None
    first_ad_is_bybit = bool(first_ad_link and any(host in first_ad_link for host in BYBIT_HOSTS))

    formats = [f.strip().lower() for f in args.format.split(",") if f.strip()]
    out_base = Path(args.out)
    if "json" in formats:
        write_json(out_base.with_suffix(".json"), records)
    if "csv" in formats:
        write_csv(out_base.with_suffix(".csv"), records)

    # Print a simple summary to stdout
    print(json.dumps({
        "keyword": args.keyword,
        "provider": args.provider,
        "num_ads_scanned": min(len(ads), max(1, args.limit)),
        "num_ref_codes_found": len(records),
        "ref_codes": [r["ref_code"] for r in records],
        "first_ad_link": first_ad_link,
        "first_ad_is_bybit": first_ad_is_bybit,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

