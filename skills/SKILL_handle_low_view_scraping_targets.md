# SKILL: Handle Low-View Scraping Targets (Oak Park Construction)

## Trigger
Apify scrape returns 0 results passing the 10k views filter.

## Problem
The scraping targets list contains accounts that consistently produce content below the 10,000 views threshold. This has caused 5 out of 6 recent runs to either fail or fall back to fallback mode, meaning the agent almost never gets fresh competitive content to work with.

## Rule
1. **Before raising an exception**, if zero results pass the 10k views filter, automatically lower the threshold in steps:
   - First fallback: try 5,000 views minimum
   - Second fallback: try 1,000 views minimum
   - Log which threshold was actually used so the human can see trending data quality.
2. **If even the 1,000 views threshold yields zero results**, then run in fallback mode (existing behavior) but **do NOT raise an exception** — just log a warning.
3. **After every run**, append a row to the `Scraping Health Log` tab (or create it) in the Google Sheet with:
   - Date/time
   - Number of posts scraped
   - Number passing 10k / 5k / 1k thresholds
   - List of accounts that returned zero qualifying posts
4. **After 3 consecutive runs where the primary 10k filter yields zero results**, auto-create a Google Calendar reminder titled "Oak Park Construction: Refresh Scraping Targets" with a description telling the human to review and replace underperforming accounts.

## Why This Matters
The agent is designed to learn from high-performing competitor content. If the scraping targets aren't producing visible content, the entire content pipeline runs on stale/fallback ideas, reducing output quality.