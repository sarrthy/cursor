import re
from typing import Dict, List, Optional, Tuple

import backoff
import requests


BYBIT_HOSTS = {
    "bybit.com",
    "www.bybit.com",
}


def _get_query_param(url: str, key: str) -> Optional[str]:
    match = re.search(rf"[?&]{re.escape(key)}=([^&#]+)", url)
    if match:
        return match.group(1)
    return None


def _is_bybit_invite(url: str) -> bool:
    return any(host in url for host in BYBIT_HOSTS) and "/invite/" in url


@backoff.on_exception(backoff.expo, (requests.RequestException,), max_tries=3)
def resolve_url(url: str, timeout_seconds: int = 20) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=timeout_seconds, allow_redirects=True)
    resp.raise_for_status()
    return resp.url


def extract_ref_code_from_url(url: str) -> Optional[str]:
    if not _is_bybit_invite(url):
        return None
    return _get_query_param(url, "ref")


def collect_ref_codes_from_ads(ads: List[Dict], limit: int = 1) -> List[Tuple[str, str]]:
    results: List[Tuple[str, str]] = []
    for ad in ads[: max(1, limit)]:
        link = ad.get("link")
        if not link:
            continue
        try:
            final_url = resolve_url(link)
        except Exception:
            final_url = link
        ref_code = extract_ref_code_from_url(final_url)
        if ref_code:
            results.append((ref_code, final_url))
    return results

