Here are the rules when `EXTRACTION_DATA_START` or `EXTRACTION_DATA_CONTINUE` event is received by the snap-in:

- If there's a timeout ("onTimeout" method in "spawn" method), the snap-in should emit an event with type `EXTRACTION_DATA_PROGRESS` (no "data" payload).
- If the extraction is rate-limited by the external system, the snap-in should emit an event with type `EXTRACTION_DATA_DELAY` ("data" payload should contain attribute "delay" - delay in seconds as an integer).
- If the extraction is successful and all the resources have been extracted, the snap-in should emit an event with type `EXTRACTION_DATA_DONE` (no "data" payload).
- In case of unexpected error, the snap-in should emit an event with type `EXTRACTION_DATA_ERROR` ("data" payload should contain attribute "error" - error message as a string).

NOTE: In all cases, only a single event should be emitted.