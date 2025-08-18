### Implementing Incremental Data Sync

Incremental data synchronization retrieves only records that have been created or updated since the last successful sync. This process requires persistently tracking the timestamp of the last successful data extraction. On subsequent runs, this timestamp is used to query the source system for changes.

Incremental mode should only be handled if the "event_type" is `EXTRACTION_DATA_START`.

To check if we're in incremental mode, you should check if the value of `adapter.event.payload.event_context.mode` is `SyncMode.INCREMENTAL`.

#### How implement incremental mode

If we're in incremental mode, you should reset The Extraction State, indicating the sync hasn't been completed yet for all data types that we support incremental mode.

Value of `adapter.state.lastSuccessfulSyncStarted` (of format ISO 8601 Extended Format with timezone) represents you the information since when you should query resources from the 3rd party API.

To retrieve only the resources from the API that have to be updated, filtering on The API should be implemented.

Note:
- `adapter.state.lastSuccessfulSyncStarted` and `adapter.state.lastSyncStarted` are internal properties of the ts-adaas library, so no need to define it. This should be a read-only property.

#### Remember the last successful sync time

If the sync is successful, update the state object with the current time.

Note: No need to modify any time-related properties in adapter.state object. 