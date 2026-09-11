"""Read-only audit of what OPC ads actually link to, and which phone numbers are live.

SELECT-only. Never mutates the account. Companion to ads_report.py, which reports
where traffic LANDED; this one reports what the ads are CONFIGURED to send people to.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any

from ads_report import load_config, ads_search

EXPECTED_PHONE = os.environ.get("ADS_EXPECTED_PHONE", "9542586769")


def digits(value: str) -> str:
    return "".join(c for c in str(value or "") if c.isdigit())


AD_QUERY = """
    SELECT
      campaign.name,
      campaign.status,
      ad_group.name,
      ad_group_ad.status,
      ad_group_ad.ad.id,
      ad_group_ad.ad.type,
      ad_group_ad.ad.final_urls
    FROM ad_group_ad
    WHERE ad_group_ad.status != 'REMOVED'
    LIMIT 200
"""

ASSET_QUERY = """
    SELECT
      asset.id,
      asset.type,
      asset.name,
      asset.call_asset.phone_number,
      asset.call_asset.country_code,
      asset.sitelink_asset.link_text,
      asset.final_urls
    FROM asset
    WHERE asset.type IN ('CALL', 'SITELINK')
    LIMIT 200
"""

CAMPAIGN_ASSET_QUERY = """
    SELECT
      campaign.name,
      campaign.status,
      campaign_asset.status,
      campaign_asset.field_type,
      asset.type,
      asset.call_asset.phone_number,
      asset.final_urls
    FROM campaign_asset
    WHERE campaign_asset.status != 'REMOVED'
    LIMIT 200
"""


def main() -> int:
    config = load_config()
    out: dict[str, Any] = {"expected_phone": EXPECTED_PHONE}

    print("=" * 70)
    print("AD FINAL URLS (what each ad is configured to open)")
    print("=" * 70)
    ads = ads_search(config, AD_QUERY)
    out["ads"] = ads
    for row in ads:
        ad = row.get("adGroupAd", {}).get("ad", {})
        urls = ad.get("finalUrls") or []
        print(
            f"[{row.get('campaign', {}).get('status')}] "
            f"{row.get('campaign', {}).get('name')} / {row.get('adGroup', {}).get('name')} "
            f"| ad {ad.get('id')} ({ad.get('type')}) "
            f"| status={row.get('adGroupAd', {}).get('status')}"
        )
        for u in urls or ["(NO FINAL URL)"]:
            print(f"    -> {u}")

    print()
    print("=" * 70)
    print(f"ASSETS — call + sitelink (expected phone: {EXPECTED_PHONE})")
    print("=" * 70)
    assets = ads_search(config, ASSET_QUERY)
    out["assets"] = assets
    for row in assets:
        a = row.get("asset", {})
        call = a.get("callAsset") or {}
        phone = call.get("phoneNumber")
        flag = ""
        if phone:
            flag = "  ✅ MATCHES" if digits(phone).endswith(digits(EXPECTED_PHONE)) else "  ❌ WRONG NUMBER"
        print(
            f"asset {a.get('id')} [{a.get('type')}] {a.get('name') or ''} "
            f"{(a.get('sitelinkAsset') or {}).get('linkText') or ''}"
        )
        if phone:
            print(f"    phone: {phone} ({call.get('countryCode')}){flag}")
        for u in a.get("finalUrls") or []:
            print(f"    -> {u}")

    print()
    print("=" * 70)
    print("CAMPAIGN-LEVEL ASSETS (which are actually attached & serving)")
    print("=" * 70)
    camp_assets = ads_search(config, CAMPAIGN_ASSET_QUERY)
    out["campaign_assets"] = camp_assets
    for row in camp_assets:
        a = row.get("asset", {})
        call = a.get("callAsset") or {}
        phone = call.get("phoneNumber")
        flag = ""
        if phone:
            flag = "  ✅ MATCHES" if digits(phone).endswith(digits(EXPECTED_PHONE)) else "  ❌ WRONG NUMBER"
        print(
            f"[{row.get('campaign', {}).get('status')}] {row.get('campaign', {}).get('name')} "
            f"| {row.get('campaignAsset', {}).get('fieldType')} "
            f"| asset_status={row.get('campaignAsset', {}).get('status')}"
            + (f" | phone {phone}{flag}" if phone else "")
        )
        for u in a.get("finalUrls") or []:
            print(f"    -> {u}")

    with open("ads_links_audit.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print("\nWrote ads_links_audit.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
