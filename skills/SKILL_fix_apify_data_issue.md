# SKILL: Fix Apify Data Issue

## Context
When the system runs in fallback mode due to missing Apify data, it encounters an error: 'cannot unpack non-iterable NoneType object'. This indicates that the expected data structure is not being returned, leading to a failure in data processing.

## Objective
Implement a check to verify if Apify data is available before proceeding with data unpacking. If the data is missing, trigger a notification or retry mechanism to obtain the data.

## Steps
1. Before unpacking data from Apify, implement a conditional check to verify that the data is not None.
2. If data is None, log an error message and initiate a retry mechanism to fetch the data again.
3. If retries fail, send a notification to the system administrator to manually check the Apify integration.

## Implementation
- Add a pre-processing step to validate Apify data availability.
- Implement retry logic with a maximum of 3 attempts to fetch the data.
- Log detailed error messages for failed attempts.
- Send an alert email or message to the system administrator if data retrieval fails after retries.
