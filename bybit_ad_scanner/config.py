import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class AppConfig:
    serp_provider: str
    serper_api_key: Optional[str]
    serpapi_api_key: Optional[str]
    default_keyword: str
    default_engine: str
    default_market: str


def load_config() -> AppConfig:
    load_dotenv(override=False)

    serp_provider = os.getenv("SERP_PROVIDER", "serper").strip().lower()
    serper_api_key = os.getenv("SERPER_API_KEY")
    serpapi_api_key = os.getenv("SERPAPI_API_KEY")
    default_keyword = os.getenv("DEFAULT_KEYWORD", "bybit")
    default_engine = os.getenv("DEFAULT_ENGINE", "google")
    default_market = os.getenv("DEFAULT_MARKET", "us")

    return AppConfig(
        serp_provider=serp_provider,
        serper_api_key=serper_api_key,
        serpapi_api_key=serpapi_api_key,
        default_keyword=default_keyword,
        default_engine=default_engine,
        default_market=default_market,
    )

