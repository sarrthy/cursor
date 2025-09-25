## Bybit Ad Scanner

Scans search engine results for the keyword "bybit", identifies the first sponsored ad, resolves its final URL, and extracts Bybit referral codes (e.g., `ref=JYAZKJN`) if present. Saves results to JSON/CSV.

### Features
- Uses a SERP API provider (SerpAPI or Serper.dev) to fetch ads
- Picks the first sponsored ad and follows redirects
- Extracts referral code from Bybit invite URLs
- Outputs JSON and/or CSV

### Setup
1. Create a Python virtual environment (optional) and install dependencies:
```bash
pip install -r requirements.txt
```
2. Configure environment variables in `.env` (or your shell):
```bash
cp .env.example .env
# edit .env with your keys
```

### Environment
- `SERP_PROVIDER`: `serper` or `serpapi` (default: `serper`)
- `SERPER_API_KEY`: API key for Serper.dev (if using `serper`)
- `SERPAPI_API_KEY`: API key for SerpAPI (if using `serpapi`)

### Usage
Run the CLI:
```bash
python -m bybit_ad_scanner --keyword "bybit" --format json,csv --out results --provider serper
```

Options:
- `--keyword`/`-k`: search keyword (default: `bybit`)
- `--provider`: `serper` or `serpapi`
- `--market`: market/country code (e.g., `us`)
- `--engine`: search engine (provider dependent; default: google)
- `--format`: comma-separated `json` and/or `csv`
- `--out`: output basename (without extension)
- `--limit`: number of ad results to scan (default: 1 for "first ad")

### Notes
- Respect provider TOS. Avoid scraping Google directly without an API.
- Redirect resolution is best-effort and may not capture JS-based redirects.
