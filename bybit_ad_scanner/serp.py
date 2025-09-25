import json
from typing import Dict, List, Optional

import backoff
import requests


UserAgent = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class SerpError(RuntimeError):
    pass


def _normalize_ads(records: List[Dict]) -> List[Dict]:
    normalized: List[Dict] = []
    for item in records or []:
        link = item.get("link") or item.get("url") or item.get("trackingUrl")
        title = item.get("title") or item.get("headline")
        source = item.get("source") or item.get("position")
        if not link:
            continue
        normalized.append({"title": title, "link": link, "source": source})
    return normalized


@backoff.on_exception(backoff.expo, (requests.RequestException, SerpError), max_tries=3)
def fetch_ads_serper(
    api_key: str,
    keyword: str,
    market: Optional[str] = None,
    engine: str = "google",
) -> List[Dict]:
    if not api_key:
        raise SerpError("Serper API key missing")
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload: Dict = {"q": keyword}
    if market:
        payload["gl"] = market
    if engine and engine != "google":
        payload["engine"] = engine
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    if resp.status_code != 200:
        raise SerpError(f"Serper HTTP {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    ads = data.get("ads") or []
    return _normalize_ads(ads)


@backoff.on_exception(backoff.expo, (requests.RequestException, SerpError), max_tries=3)
def fetch_ads_serpapi(
    api_key: str,
    keyword: str,
    market: Optional[str] = None,
    engine: str = "google",
) -> List[Dict]:
    if not api_key:
        raise SerpError("SerpAPI API key missing")
    url = "https://serpapi.com/search.json"
    params: Dict = {"q": keyword, "engine": engine or "google", "api_key": api_key}
    if market:
        params["gl"] = market
    headers = {"User-Agent": UserAgent}
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise SerpError(f"SerpAPI HTTP {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    ads = data.get("ads") or data.get("top_ads") or []
    return _normalize_ads(ads)


def fetch_ads(
    provider: str,
    keyword: str,
    market: Optional[str],
    engine: str,
    serper_api_key: Optional[str],
    serpapi_api_key: Optional[str],
) -> List[Dict]:
    provider = (provider or "serper").lower()
    if provider == "serper":
        return fetch_ads_serper(serper_api_key or "", keyword, market, engine)
    if provider == "serpapi":
        return fetch_ads_serpapi(serpapi_api_key or "", keyword, market, engine)
    raise SerpError(f"Unknown provider: {provider}")

