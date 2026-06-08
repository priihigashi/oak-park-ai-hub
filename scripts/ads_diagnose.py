"""
ads_diagnose.py — one-off diagnostic: why is MGC Leads-Search-Calls #2 at $0?
2026-06-08: created to answer "when did the campaign stop and who paused it."
"""
import os, sys
from google.ads.googleads.client import GoogleAdsClient

CUSTOMER_ID = "8945889168"
CAMPAIGN_ID = "23314409466"

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

def q(query):
    return list(ga.search(customer_id=CUSTOMER_ID, query=query))

print("=" * 70)
print("CAMPAIGN STATUS")
print("=" * 70)
for r in q(f"""
    SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
           campaign.start_date, campaign.end_date,
           campaign_budget.amount_micros, campaign_budget.status,
           campaign.bidding_strategy_type
    FROM campaign
    WHERE campaign.id = {CAMPAIGN_ID}
"""):
    c = r.campaign
    b = r.campaign_budget
    print(f"  Name:             {c.name}")
    print(f"  Status:           {c.status.name}")
    print(f"  Serving status:   {c.serving_status.name}")
    print(f"  Start / End:      {c.start_date} / {c.end_date}")
    print(f"  Daily budget:     ${b.amount_micros / 1_000_000:.2f}/day")
    print(f"  Budget status:    {b.status.name}")
    print(f"  Bid strategy:     {c.bidding_strategy_type.name}")

print()
print("=" * 70)
print("LAST 30 DAYS — DAILY SPEND (find last day with $)")
print("=" * 70)
print(f"  {'Date':<12} {'Spend':>10} {'Clicks':>8} {'Impr':>8} {'Conv':>6}")
for r in q(f"""
    SELECT segments.date, metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions
    FROM campaign
    WHERE campaign.id = {CAMPAIGN_ID}
      AND segments.date DURING LAST_30_DAYS
    ORDER BY segments.date DESC
"""):
    m = r.metrics
    d = r.segments.date
    cost = m.cost_micros / 1_000_000
    marker = "  ⬅ last spend" if cost > 0 else ""
    print(f"  {d:<12} ${cost:>8.2f} {m.clicks:>8} {m.impressions:>8} {m.conversions:>6.1f}{marker}")

print()
print("=" * 70)
print("CHANGE EVENTS — LAST 60 DAYS (who/when/what)")
print("=" * 70)
events = q(f"""
    SELECT change_event.change_date_time, change_event.user_email,
           change_event.client_type, change_event.resource_change_operation,
           change_event.changed_fields, change_event.change_resource_type,
           change_event.campaign
    FROM change_event
    WHERE change_event.change_date_time DURING LAST_30_DAYS
      AND change_event.campaign = 'customers/{CUSTOMER_ID}/campaigns/{CAMPAIGN_ID}'
    ORDER BY change_event.change_date_time DESC
    LIMIT 50
""")
if not events:
    print("  (no change events found in last 30 days)")
for r in events:
    e = r.change_event
    print(f"  {e.change_date_time} | by={e.user_email} | {e.client_type.name} | {e.resource_change_operation.name} | {e.change_resource_type.name}")
    if e.changed_fields and e.changed_fields.paths:
        for p in e.changed_fields.paths:
            print(f"      changed field: {p}")

print()
print("=" * 70)
print("ACCOUNT BUDGET STATUS (billing/funding)")
print("=" * 70)
try:
    for r in q("""
        SELECT account_budget.id, account_budget.name, account_budget.status,
               account_budget.amount_served_micros, account_budget.total_adjustments_micros,
               account_budget.approved_start_date_time, account_budget.approved_end_date_time
        FROM account_budget
    """):
        a = r.account_budget
        print(f"  Name:    {a.name}")
        print(f"  Status:  {a.status.name}")
        print(f"  Served:  ${a.amount_served_micros / 1_000_000:.2f}")
        print(f"  Start/End: {a.approved_start_date_time} / {a.approved_end_date_time}")
except Exception as e:
    print(f"  (account_budget query failed — likely no manual budget set): {e}")

print()
print("=" * 70)
print("DONE")
print("=" * 70)
