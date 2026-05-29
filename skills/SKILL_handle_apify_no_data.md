# SKILL: Handle Apify No Data

## Purpose
This skill addresses the issue when the system runs in fallback mode due to no data being returned from Apify.

## Trigger
- When an Apify data retrieval results in zero results or an error indicating 'cannot unpack non-iterable NoneType object'.

## Actions
1. Implement a retry mechanism that retries the data fetch from Apify up to three times before falling back to the default mode.
2. Log detailed error information whenever the Apify data fetch fails, including timestamps and error messages.
3. Alert the development team if the retries fail, with details on the number of attempts and error messages.
4. Ensure the system can gracefully handle these situations without crashing or going into fallback mode inadvertently.

## Monitoring
- Log all retries and failures.
- Regularly review logs for recurring patterns and adjust the retry logic or alerting thresholds as necessary.