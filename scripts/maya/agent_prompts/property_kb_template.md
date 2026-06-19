# Property Knowledge Base — TEMPLATE (one per property)

Fill EVERY field before a property goes live. Maya answers ONLY from this KB. Blank field =
Maya will say "I'll log it and someone will follow up" instead of guessing.

property_id: PROP-____
nickname:
full_address:                         # not read aloud unless verifying the guest
check_in_time:
check_out_time:
check_in_process:                     # smart lock? lockbox? code delivery timing?
door_code / lock instructions:
wifi_network:
wifi_password:
parking:                              # where, permit?, street rules
trash_recycling:                      # days, location
house_rules:                          # quiet hours, pets, smoking, max occupancy
amenities:                            # pool, laundry, AC type, thermostat notes
nearby_essentials:                    # nearest grocery, pharmacy, hospital
known_quirks:                         # finicky shower, breaker location, etc.

## Emergency contacts (used by escalation)
escalation_primary: Priscila          # (phone stored as secret MF_PRISCILA_PHONE — never here)
escalation_fallback: Michael          # (phone stored as secret MF_MICHAEL_PHONE — never here)
local_emergency: 911

> PII rule: never write guest data or real phone numbers into this file. Phone numbers live in
> GitHub secrets. Share the filled KB only with the service account for ingestion.
