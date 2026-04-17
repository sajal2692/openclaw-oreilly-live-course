#!/usr/bin/env python3
"""
Search Craigslist for apartment listings matching criteria.
Outputs JSON array of new listings (deduped against tracked listings file).

Usage:
    python3 search_craigslist.py [options]

Options:
    --city NAME         Craigslist city subdomain (default: vancouver)
    --max-price N       Maximum rent (default: 3500)
    --min-price N       Minimum rent (default: 2000)
    --beds N            Minimum bedrooms (default: 2)
    --baths N           Minimum bathrooms (default: 1)
    --min-sqft N        Minimum square footage (default: 700)
    --area CODE         Craigslist sub-area codes, comma-separated (optional)
    --max-results N     Max detail pages to fetch (default: 20)
    --tracked-file PATH Path to tracked listings markdown file for dedup
    --raw               Dump raw search HTML to stderr (for debugging)
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print(
        "Missing dependencies. Run:\n  pip3 install requests beautifulsoup4",
        file=sys.stderr,
    )
    sys.exit(1)


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
DELAY_BETWEEN_REQUESTS = 1.5  # seconds


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"})
    return s


def fetch(url, session):
    resp = session.get(url, timeout=15)
    resp.raise_for_status()
    return resp.text


# ---------------------------------------------------------------------------
# Search results parsing (multiple strategies for resilience)
# ---------------------------------------------------------------------------

def build_search_url(base_url, area, params):
    qs = urlencode(params)
    if area:
        return f"{base_url}/search/{area}/apa?{qs}"
    return f"{base_url}/search/apa?{qs}"


def parse_search_results(html, base_url):
    """Return list of {title, url, price} from a Craigslist search page."""
    soup = BeautifulSoup(html, "html.parser")
    results = []

    def _abs(href):
        if href.startswith("http"):
            return href
        return base_url + href

    # Strategy 1: modern CL layout (2024+)
    for item in soup.select("li.cl-static-search-result, li.cl-search-result"):
        link = item.find("a", href=True)
        if not link:
            continue
        href = _abs(link["href"])
        title_el = item.select_one(".title, .titlestring")
        title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
        price = _extract_price_from_el(item)
        results.append({"title": title, "url": href, "price": price})

    # Strategy 2: older CL layout
    if not results:
        for item in soup.select("li.result-row, .result-row"):
            link = item.select_one("a.result-title, a.titlestring, a.posting-title")
            if not link:
                continue
            href = _abs(link["href"])
            title = link.get_text(strip=True)
            price = _extract_price_from_el(item)
            results.append({"title": title, "url": href, "price": price})

    # Strategy 3: brute-force - find all posting links
    if not results:
        seen = set()
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if re.search(r"/\d{9,}\.html", href) and href not in seen:
                seen.add(href)
                results.append({
                    "title": link.get_text(strip=True) or "Unknown",
                    "url": _abs(href),
                    "price": None,
                })

    return results


# ---------------------------------------------------------------------------
# Detail page parsing
# ---------------------------------------------------------------------------

def parse_detail(html):
    """Parse a single Craigslist listing page into structured data."""
    soup = BeautifulSoup(html, "html.parser")
    d = {}

    # Title
    el = soup.select_one("#titletextonly, .postingtitletext > #titletextonly")
    if el:
        d["title"] = el.get_text(strip=True)

    # Price
    el = soup.select_one(".price")
    if el:
        d["price"] = _parse_price(el.get_text(strip=True))

    # Attributes (beds, baths, sqft, housing type, laundry, parking, pets)
    attr_text = ""
    for group in soup.select(".attrgroup"):
        for span in group.find_all("span"):
            t = span.get_text(strip=True)
            attr_text += " " + t.lower()

            m = re.search(r"(\d+)\s*br", t, re.I)
            if m:
                d["beds"] = int(m.group(1))

            m = re.search(r"(\d+(?:\.\d+)?)\s*ba", t, re.I)
            if m:
                d["baths"] = int(float(m.group(1)))

            m = re.search(r"(\d[\d,]*)\s*ft", t, re.I)
            if m:
                d["sqft"] = int(m.group(1).replace(",", ""))

            t_lower = t.lower()
            if "apartment" in t_lower:
                d["type"] = "Apartment"
            elif "condo" in t_lower:
                d["type"] = "Condo"
            elif "townhouse" in t_lower:
                d["type"] = "Townhouse"
            elif "house" in t_lower:
                d["type"] = "House"

    # Pets
    if "cats are ok" in attr_text or "dogs are ok" in attr_text:
        d["pets"] = True
    elif "no pets" in attr_text:
        d["pets"] = False

    # Address
    el = soup.select_one(".mapaddress")
    if el:
        d["address"] = el.get_text(strip=True)

    # Map coordinates
    el = soup.select_one("#map")
    if el:
        lat = el.get("data-latitude")
        lon = el.get("data-longitude")
        if lat and lon:
            d["latitude"] = lat
            d["longitude"] = lon

    # Description
    el = soup.select_one("#postingbody")
    if el:
        for rm in el.select(
            ".print-information, .print-qrcode-label, .print-qrcode-container"
        ):
            rm.decompose()
        d["description"] = el.get_text(strip=True)[:1000]

    # Date posted
    el = soup.select_one("time.date, time.timeago, time[datetime]")
    if el and el.get("datetime"):
        d["date_posted"] = el["datetime"][:10]

    return d


# ---------------------------------------------------------------------------
# Dedup: load tracked listing URLs from markdown file
# ---------------------------------------------------------------------------

def load_tracked_urls(tracked_file):
    """Extract listing URLs from a markdown tracker file.

    Scans for URLs matching Craigslist listing patterns in the file.
    Returns a set of URLs and a set of Craigslist posting IDs.
    """
    urls = set()
    cl_ids = set()

    if not tracked_file:
        return urls, cl_ids

    path = Path(tracked_file)
    if not path.is_file():
        return urls, cl_ids

    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return urls, cl_ids

    # Find all Craigslist URLs in the file
    for match in re.finditer(r"https?://[a-z]+\.craigslist\.org/\S+\.html", text):
        url = match.group(0).rstrip("|) ")
        urls.add(url)
        cid = _extract_cl_id(url)
        if cid:
            cl_ids.add(cid)

    return urls, cl_ids


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_price_from_el(el):
    for sel in [".priceinfo", ".result-price", ".price"]:
        p = el.select_one(sel)
        if p:
            return _parse_price(p.get_text(strip=True))
    # Fallback: regex on the element text
    m = re.search(r"\$\s*([\d,]+)", el.get_text())
    if m:
        return int(m.group(1).replace(",", ""))
    return None


def _parse_price(text):
    m = re.search(r"[\d,]+", text.replace("$", ""))
    if m:
        return int(m.group(0).replace(",", ""))
    return None


def _extract_cl_id(url):
    m = re.search(r"/(\d{9,})\.html", url)
    return m.group(1) if m else None


def _is_duplicate(listing_url, existing_urls, existing_cl_ids):
    if listing_url in existing_urls:
        return True
    cid = _extract_cl_id(listing_url)
    if cid and cid in existing_cl_ids:
        return True
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Search Craigslist for apartment listings"
    )
    parser.add_argument(
        "--city", default="vancouver",
        help="Craigslist city subdomain (default: vancouver). "
             "Examples: seattle, sfbay, newyork, toronto, chicago, losangeles"
    )
    parser.add_argument("--min-price", type=int, default=2000, help="Minimum rent")
    parser.add_argument("--max-price", type=int, default=3500, help="Maximum rent")
    parser.add_argument("--beds", type=int, default=2, help="Minimum bedrooms")
    parser.add_argument("--baths", type=int, default=1, help="Minimum bathrooms")
    parser.add_argument("--min-sqft", type=int, default=700, help="Minimum square footage")
    parser.add_argument(
        "--area", default="",
        help="Craigslist sub-area codes, comma-separated (optional). "
             "City-specific, e.g.: bnc, sfc, mnh"
    )
    parser.add_argument(
        "--max-results", type=int, default=20,
        help="Max detail pages to fetch"
    )
    parser.add_argument(
        "--tracked-file",
        help="Path to markdown file containing tracked listings (for dedup)"
    )
    parser.add_argument(
        "--raw", action="store_true",
        help="Dump raw search HTML to stderr (for debugging)"
    )
    args = parser.parse_args()

    base_url = f"https://{args.city}.craigslist.org"
    session = make_session()

    # Load tracked listings for dedup
    existing_urls, existing_cl_ids = load_tracked_urls(args.tracked_file)
    if existing_urls:
        print(
            f"Loaded {len(existing_urls)} tracked listing URLs for dedup",
            file=sys.stderr,
        )

    # Build search params
    search_params = {
        "min_price": args.min_price,
        "max_price": args.max_price,
        "min_bedrooms": args.beds,
        "min_bathrooms": args.baths,
        "minSqft": args.min_sqft,
        "sort": "date",
        "availabilityMode": 0,
    }

    # Search each area (or whole city if no area specified)
    all_search_results = []
    areas = [a.strip() for a in args.area.split(",") if a.strip()] if args.area else [""]

    for area in areas:
        url = build_search_url(base_url, area, search_params)
        print(f"Searching: {url}", file=sys.stderr)

        try:
            html = fetch(url, session)
        except Exception as e:
            print(f"ERROR fetching search results for {area or 'all'}: {e}", file=sys.stderr)
            continue

        if args.raw:
            print(
                f"\n--- RAW HTML ({area or 'all'}) ---\n{html[:5000]}\n--- END ---\n",
                file=sys.stderr,
            )

        results = parse_search_results(html, base_url)
        print(f"  Parsed {len(results)} listings from {area or 'all areas'}", file=sys.stderr)
        all_search_results.extend(results)

    if not all_search_results:
        print("No listings found. The HTML structure may have changed.", file=sys.stderr)
        print("Run with --raw to dump search HTML for debugging.", file=sys.stderr)
        print("[]")
        return

    # Deduplicate across areas (by URL)
    seen_urls = set()
    unique_results = []
    for r in all_search_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)

    # Filter out already-tracked listings
    new_results = []
    for r in unique_results:
        if _is_duplicate(r["url"], existing_urls, existing_cl_ids):
            print(f"  SKIP (already tracked): {r['title']}", file=sys.stderr)
            continue
        new_results.append(r)

    print(
        f"{len(new_results)} new listings after dedup (from {len(unique_results)} total)",
        file=sys.stderr,
    )

    # Fetch detail pages
    listings = []
    to_fetch = new_results[: args.max_results]

    for i, result in enumerate(to_fetch):
        if i > 0:
            time.sleep(DELAY_BETWEEN_REQUESTS)

        print(
            f"  Fetching [{i + 1}/{len(to_fetch)}]: {result['title'][:60]}",
            file=sys.stderr,
        )

        try:
            html = fetch(result["url"], session)
            detail = parse_detail(html)
        except Exception as e:
            print(f"    ERROR: {e}", file=sys.stderr)
            continue

        # Merge search-level data with detail-level data
        listing = {
            "title": detail.get("title") or result.get("title", ""),
            "price": detail.get("price") or result.get("price"),
            "beds": detail.get("beds"),
            "baths": detail.get("baths"),
            "sqft": detail.get("sqft"),
            "type": detail.get("type", ""),
            "address": detail.get("address", ""),
            "pets": detail.get("pets"),
            "listing_url": result["url"],
            "date_posted": detail.get("date_posted", ""),
            "description": detail.get("description", ""),
            "latitude": detail.get("latitude"),
            "longitude": detail.get("longitude"),
        }

        # Post-filter: skip listings that clearly don't meet criteria
        if listing["beds"] is not None and listing["beds"] < args.beds:
            print(f"    SKIP: {listing['beds']}BR < {args.beds}BR required", file=sys.stderr)
            continue
        if listing["baths"] is not None and listing["baths"] < args.baths:
            print(
                f"    SKIP: {listing['baths']}BA < {args.baths}BA required",
                file=sys.stderr,
            )
            continue
        if listing["sqft"] is not None and listing["sqft"] < args.min_sqft:
            print(
                f"    SKIP: {listing['sqft']}sqft < {args.min_sqft}sqft required",
                file=sys.stderr,
            )
            continue

        listings.append(listing)

    print(f"\n{len(listings)} listings passed all filters", file=sys.stderr)
    print(json.dumps(listings, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
