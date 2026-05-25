# SKILL: Fix Apify NoneType Error

## Context
This skill addresses the recurring issue where the system runs in fallback mode due to Apify returning a NoneType object that cannot be unpacked.

## Trigger
- Error message: 'cannot unpack non-iterable NoneType object'

## Actions
1. Implement a check to verify if the data received from Apify is not None before attempting to unpack.
2. If None, log a specific error message and skip unpacking process.
3. Send a notification to the system administrator with details of the error.

## Testing
- Simulate Apify returning None and verify that the new error handling logic is triggered correctly without causing a fallback mode.