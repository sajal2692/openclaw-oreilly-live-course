---
name: rental-search
description: Search Craigslist for rental apartment listings in any North American city. Scrapes listings, filters by criteria, dedupes against previously seen results, and reports new matches. Use when the user asks to search for apartments, check for new listings, run the rental search, or scan Craigslist.
---

# Rental Search

Craigslist rental scraper that finds apartment listings matching configurable search criteria, deduplicates against previously tracked listings, and delivers a structured report of new matches.

## Configuration

- **Scraper script**: `skills/rental-search/scripts/search_craigslist.py`
- **Tracked listings file**: `notes/trackers/rentals.md`

### Default Search Criteria

| Parameter | Default | Notes |
|---|---|---|
| city | vancouver | Craigslist subdomain (e.g., vancouver, seattle, sfbay, newyork, chicago, toronto, losangeles) |
| min_price | 2000 | Minimum monthly rent |
| max_price | 3500 | Maximum monthly rent |
| beds | 2 | Minimum bedrooms |
| baths | 1 | Minimum bathrooms |
| min_sqft | 700 | Minimum square footage |
| area | (none) | Craigslist sub-area code (city-specific, e.g., bnc, sfc, brk). Omit to search the whole city. |

Override any of these when the user specifies different criteria.

## Workflow

### Step 1: Run the scraper

```bash
python3 "skills/rental-search/scripts/search_craigslist.py" \
  --city vancouver \
  --min-price 2000 \
  --max-price 3500 \
  --beds 2 \
  --baths 1 \
  --min-sqft 700 \
  --tracked-file "notes/trackers/rentals.md"
```

The script:
1. Builds a Craigslist search URL for the specified city and criteria
2. Parses search results using multiple HTML parsing strategies (resilient to Craigslist layout changes)
3. Deduplicates against listing URLs already present in the tracked listings file
4. Fetches detail pages for new listings (with polite delay between requests)
5. Post-filters: drops listings below bed/bath/sqft minimums
6. Outputs a JSON array to stdout (progress and skip messages go to stderr)

**Override defaults** with CLI args when the user requests different criteria:
```bash
python3 "skills/rental-search/scripts/search_craigslist.py" \
  --city seattle \
  --max-price 3000 \
  --beds 1 \
  --min-sqft 500 \
  --area see \
  --tracked-file "notes/trackers/rentals.md"
```

**If the scraper returns 0 results and you suspect an HTML parsing issue**, re-run with `--raw` to dump the search page HTML, then inspect and fix the selectors in the script.

### Step 2: Assess each listing

For each listing in the JSON output, evaluate:

1. **Value assessment**: Compare price vs sqft vs beds. Flag anything that looks like a particularly good deal or suspiciously cheap (possible scam).

2. **Red flags**: Check for common warning signs:
   - No address listed or very vague location
   - Description is generic or copy-pasted boilerplate
   - Asking for deposits before viewing
   - Shared accommodations disguised as full apartments
   - Price far below market rate for the area

3. **Highlights**: Note any standout features mentioned in the description (in-unit laundry, parking included, pets allowed, recently renovated, views, etc.)

### Step 3: Update tracked listings

Append new listings to `notes/trackers/rentals.md`. Each listing gets a row in the table:

```markdown
| Date | Address | Price | Beds/Baths | Sqft | Notes | URL | Status |
```

Set Status to `new` for freshly added listings. The user can later update this to `interested`, `contacted`, `visited`, `rejected`, etc.

If the tracked file does not exist, create it with the table header.

### Step 4: Report results

Present results to the user in a clear summary:

```
## Rental Search Results

Searched: {city} Craigslist
Found {N} new listings ({M} total on Craigslist, {K} already tracked, {J} filtered out)

### New Listings

For each new listing, include:
- Address and price
- Beds / baths / sqft
- Key highlights from description
- Any red flags
- Link to listing

### Standout Picks

Pick the 2-3 best listings based on value, features, and absence of red flags.
For each, write a 1-2 sentence pitch on why it stands out.

### Market Snapshot

Based on all listings seen in this run (not just new ones), note:
- Price range observed for the search criteria
- General availability (many listings vs slim pickings)
- Any patterns (e.g., most listings cluster around $X, few allow pets, etc.)

### Skipped

- {listing}: {reason}

### Flagged

- {any red flags or unusually good deals}
```

## Craigslist City Codes

Common Craigslist subdomains for North American cities:

| City | Code | Example Sub-areas |
|---|---|---|
| Vancouver | vancouver | bnc (Burnaby/New West), van (Vancouver) |
| Toronto | toronto | tor (Toronto proper), yrk (York Region) |
| Seattle | seattle | see (Seattle), est (Eastside), sno (Snohomish) |
| San Francisco | sfbay | sfc (SF), eby (East Bay), sby (South Bay) |
| New York | newyork | mnh (Manhattan), brk (Brooklyn), que (Queens) |
| Los Angeles | losangeles | wst (Westside), sfv (San Fernando Valley) |
| Chicago | chicago | chc (City of Chicago) |
| Portland | portland | mlt (Multnomah), wsc (Washington County) |
| Denver | denver | (no common sub-areas) |
| Austin | austin | (no common sub-areas) |

For the full list: `https://{city}.craigslist.org/search/apa`

## Debugging

If the scraper breaks (Craigslist HTML changes frequently):

1. Run with `--raw` to dump the actual search page HTML
2. Inspect the HTML structure for changed selectors
3. Update CSS selectors in `search_craigslist.py`:
   - `parse_search_results()`: search results page selectors
   - `parse_detail()`: individual listing page selectors
4. The script has 3 fallback parsing strategies for search results; usually only the detail page selectors need updating

## Scheduling

This skill works well as a scheduled task. Run it daily or every few hours to catch new listings before they are taken. Dedup ensures no duplicates across runs.
