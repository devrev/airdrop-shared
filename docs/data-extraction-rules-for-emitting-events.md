# Data Extraction Rules for Emitting Events

## Input event: `EXTRACTION_DATA_START` or `EXTRACTION_DATA_CONTINUE`

Here are the rules when `EXTRACTION_DATA_START` or `EXTRACTION_DATA_CONTINUE` event is received by the snap-in:

- The `EXTRACTION_DATA_PROGRESS` event *MUST* only be emitted from within the "onTimeout" handler of "processTask" method.
- The `EXTRACTION_DATA_PROGRESS` event *MUST NEVER* be emitted from within the "task" handler of "processTask" method.
- If the extraction is successful and all the resources have been extracted, the snap-in should emit an event with type `EXTRACTION_DATA_DONE` (no "data" payload).
- In case of unexpected error, the snap-in should emit an event with type `EXTRACTION_DATA_ERROR` ("data" payload should contain attribute "error" - error message as a string).
- In case of rate limiting (status code 429) for "data extraction", the snap-in _must_ emit an event with type `EXTRACTION_DATA_DELAY`. If emitting event of type `EXTRACTION_DATA_DELAY`, you _must_ also provide a "delay" attribute, specifying the delay in seconds as an integer.
  - Example: `await adapter.emit(ExtractorEventType.ExtractionDataDelay, { delay: "30" });`
  - If rate limiting is encountered at ANY point during data extraction (including nexted API calls) the snap-in _must_ emit an event with type `EXTRACTION_DATA_DELAY`.
  - The delay attribute should be extracted from the API response.
  - Rate limiting should be checked immediately after each API call, before proceeding with further processing.
  - If rate limiting is encountered at ANY point during data extraction (including nested API calls within Promise.all, async operations, or iterations over an array) the snap-in _must_ emit an event with type `EXTRACTION_DATA_DELAY` and IMMEDIATELY RETURN from the task function.
  - Rate limiting MUST be checked immediately after EACH AND EVERY API call, before proceeding with any further processing.
  - For asynchronous operations (e.g., Promise.all), rate limiting must be checked within each async function and propagated appropriately.
  - Example pattern for checking rate limiting:
    - In case we're making a single API call:
      ```typescript
      const response = await trelloClient.someMethod();
      if (response.status_code === 429) {
        await adapter.emit(ExtractorEventType.ExtractionDataDelay, {
          delay: response.api_delay,
        });
        return; // Must return immediately
      }
      ```

    - In case we're iterating over an array and making API calls within the iteration:
      ```typescript
      let rateLimited = false;
      let delay = 0;

      const results = await Promise.all(
        items.map(async (item) => {
          // Skip if already rate limited
          if (rateLimited) return null;

          // Make API request
          const response = await apiClient.someMethod();
          
          // Handle rate limiting (HTTP 429)
          if (response.status_code === 429) {
            rateLimited = true;
            delay = response.api_delay; // calculate delay from response
            return null;
          }

          return response.data // or similar
        })
      );

      if (rateLimited) {
        await adapter.emit(ExtractorEventType.ExtractionDataDelay, {
          delay: delay,
        });
        return;
      }
      ```
      NOTE: You **MUST NOT** throw an error inside the `Promise.all` block (this would kill the data extraction process).


## Input event: `EXTRACTION_EXTERNAL_SYNC_UNITS_START`

Here are the rules when `EXTRACTION_EXTERNAL_SYNC_UNITS_START` event is received by the snap-in:

- If "external sync unit extraction" is successful and the snap-in has extracted all the external sync units, the snap-in should emit an event with type `EXTRACTION_EXTERNAL_SYNC_UNITS_DONE` (no "data" payload).
- In case of unexpected error, the snap-in should emit an event with type `EXTRACTION_EXTERNAL_SYNC_UNITS_ERROR` ("data" payload should contain attribute "error" - error message as a string).
- In case of rate limiting (status code 429) for "external sync unit extraction", the snap-in should also emit an event with type `EXTRACTION_EXTERNAL_SYNC_UNITS_ERROR`.

## Input event: `EXTRACTION_METADATA_START`

Here are the rules when `EXTRACTION_METADATA_START` event is received by the snap-in:

- If "metadata extraction" is successful and the snap-in has extracted all the metadata, the snap-in should emit an event with type `EXTRACTION_METADATA_DONE` (no "data" payload).
- In case of unexpected error, the snap-in should emit an event with type `EXTRACTION_METADATA_ERROR` ("data" payload should contain attribute "error" - error message as a string).

## Input event: `EXTRACTION_ATTACHMENTS_START` or `EXTRACTION_ATTACHMENTS_CONTINUE`

Here are the rules when `EXTRACTION_ATTACHMENTS_START` or `EXTRACTION_ATTACHMENTS_CONTINUE` event is received by the snap-in:

- If "attachments extraction" is successful and the snap-in has extracted all the attachments, the snap-in should emit an event with type "EXTRACTION_ATTACHMENTS_DONE"
- If case of unexpected error, the snap-in should emit an event with type "EXTRACTION_ATTACHMENTS_ERROR" ("data" payload should contain attribute "error" - error message as a string).
- In case of rate limiting (status code 429) for "attachments extraction", the snap-in should also emit an event with type "EXTRACTION_ATTACHMENTS_DELAY". If emitting event of type "EXTRACTION_ATTACHMENTS_DELAY", you *must* also provide a "delay" attribute, specifying the delay in seconds as an integer.
  - Example: `await adapter.emit(ExtractorEventType.ExtractionAttachmentsDelay, { delay: "30" });`
- If there's a timeout ("onTimeout" method in "spawn" method), the snap-in should emit an event with type "EXTRACTION_ATTACHMENTS_PROGRESS".

## IMPORTANT FOR ALL INPUT EVENTS

- In all cases, only a single event should be emitted.

