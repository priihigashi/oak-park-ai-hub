"""
ads_conversion_audit.py — read-only audit of all conversion actions on the
OPC Regular account (894-588-9168). Created 2026-06-16 to hand Priscila the
exact keep-Primary vs flip-Secondary list for the conversion-tracking fix.

NO mutations — pure GAQL SELECT. Mirrors ads_diagnose.py auth pattern.
"""
import os
from google.ads.googleads.client import GoogleAdsClient

CUSTOMER_ID = "8945889168"  # 894-588-9168 Oak Park Construction (Regular)

config = {
    "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
    "client_id":       os.environ["GOOGLE_ADS_CLIENT_ID"],
    "client_secret":   os.environ["GOOGLE_ADS_CLIENT_SECRET"],
    "refresh_token":   os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
    "login_customer_id": os.environ.get("GOOGLE_ADS_MCC_ID", "5870713494").replace("-", ""),
    "use_proto_plus": True,
}
client = GoogleAdsClient.load_from_dict(config)
ga = client.get_service("GoogleAdsService")

query = """
    SELECT
        conversion_action.name,
        conversion_action.status,
        conversion_action.type,
        conversion_action.category,
        conversion_action.primary_for_goal,
        conversion_action.origin,
        conversion_action.value_settings.default_value,
        conversion_action.value_settings.default_currency_code,
        conversion_action.counting_type
    FROM conversion_action
    ORDER BY conversion_action.primary_for_goal DESC, conversion_action.name
"""

rows = list(ga.search(customer_id=CUSTOMER_ID, query=query))

print("=" * 90)
print(f"CONVERSION ACTIONS — account {CUSTOMER_ID} — total: {len(rows)}")
print("=" * 90)
print(f"{'PRIMARY':<8} {'STATUS':<9} {'VALUE':>8}  {'CATEGORY':<22} {'NAME'}")
print("-" * 90)
for r in rows:
    c = r.conversion_action
    primary = "PRIMARY" if c.primary_for_goal else "second."
    val = c.value_settings.default_value
    val_s = f"${val:.0f}" if val else "$0"
    print(f"{primary:<8} {c.status.name:<9} {val_s:>8}  {c.category.name:<22} {c.name}  [{c.type_.name} / {c.origin.name}]")

print("-" * 90)
n_primary = sum(1 for r in rows if r.conversion_action.primary_for_goal)
n_zero = sum(1 for r in rows if not r.conversion_action.value_settings.default_value)
print(f"PRIMARY count: {n_primary}/{len(rows)}   |   zero-value count: {n_zero}/{len(rows)}")
