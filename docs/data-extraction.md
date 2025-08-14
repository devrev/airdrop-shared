# Data Extraction

In the data extraction phase, the extractor is expected to call the external system's APIs
to retrieve all the items that should be synced with DevRev.

If the current run is an initial sync, this means all the items should be extracted.
Otherwise the extractor should retrieve all the items that were changed since the start of the last extraction.

Each snap-in invocation runs in a separate runtime instance with a maximum execution time of 13 minutes. 
After 10 minutes, the Airdrop platform sends a message to the snap-in to gracefully exit.

If a large amount of data needs to be extracted, it might not all be extracted within this time frame. 
To handle such situations, the snap-in uses a state object. 
This state object is shared across all invocations and keeps track of where the previous snap-in invocations ended in the extraction process.

## Triggering event

Airdrop initiates data extraction by starting the snap-in with a message with event type
`EXTRACTION_DATA_START` when transitioning to the data extraction phase.

During the data extraction phase, the snap-in extracts data from an external system,
prepares batches of data and uploads them in the form of artifacts (files) to DevRev.

If there's timeout, the snap-in must respond to Airdrop with a message with event type of `EXTRACTION_DATA_PROGRESS`,
together with an optional progress estimate when the maximum Airdrop snap-in runtime (13 minutes) has been reached.

If the extraction has been rate-limited by the external system and back-off is required, the snap-in
must respond to Airdrop with a message with event type `EXTRACTION_DATA_DELAY` and specifying
back-off time with `delay` attribute (in seconds as an integer).

In both cases, Airdrop starts the snap-in with a message with event type `EXTRACTION_DATA_CONTINUE`.
In case of `EXTRACTION_DATA_PROGRESS` the restarting is immediate,
meanwhile in case of `EXTRACTION_DATA_DELAY` the restarting is delayed for the given number of seconds.

Once the data extraction is done, the snap-in must respond to Airdrop with a message with event type `EXTRACTION_DATA_DONE`.

If data extraction failed in any moment of extraction, the snap-in must respond to Airdrop with a
message with event type `EXTRACTION_DATA_ERROR`.

## Implementation

The snap-in must respond to Airdrop with a message, that signals either success, a delay, progress, or an error.

```typescript
await adapter.emit(ExtractorEventType.ExtractionDataDone);
```

```typescript
await adapter.emit(ExtractorEventType.ExtractionDataDelay, {
  delay: "30",
});
```

```typescript
await adapter.emit(ExtractorEventType.ExtractionDataProgress);
```

```typescript
await adapter.emit(ExtractorEventType.ExtractionDataError, {
  error: {
    message: "Failed to extract data.",
  },
});
```

<Note>The snap-in must always emit a single message.</Note>

### Extracting and storing the data

The SDK library includes a repository system for handling extracted items.
Each item type, such as users, tasks, or issues, has its own repository. 
These are defined in the `repos` array as `itemType`. 
The `itemType` name should match the `record_type` specified in the provided metadata.

```typescript
const repos = [
  {
    itemType: 'todos',
  },
  {
    itemType: 'users',
  },
  {
    itemType: 'attachments',
  },
];
```

The `initializeRepos` function initializes the repositories and should be the first step when the process begins.

```typescript
processTask<ExtractorState>({
  task: async ({ adapter }) => {
    adapter.initializeRepos(repos);
    // ...
  },
  onTimeout: async ({ adapter }) => {
    // ...
  },
});
```

After initialization of repositories using `initializeRepos`,
items should be then retrieved from the external system and stored in the correct repository by calling the `push` function.

```typescript
await adapter.getRepo('users')?.push(items);
```

Behind the scenes, the SDK library stores items pushed to the repository and uploads them in batches to the Airdrop platform.

### Data normalization

Extracted data must be normalized to fit the domain metadata defined in the `external-domain-metadata.json` file. 

Normalization rules:

- Null values: All fields without a value should either be omitted or set to null.
  For example, if an external system provides values such as "", –1 for missing values,
  those must be set to null.
- Timestamps: Full-precision timestamps should be formatted as RFC3339 (`1972-03-29T22:04:47+01:00`),
  and dates should be just `2020-12-31`.
- References: references must be strings, not numbers or objects.
- Number fields must be valid JSON numbers (not strings).
- Multiselect fields must be provided as an array (not CSV).
- Rich text: Strings from 3rd party services should be converted to the rich text by splitting the string by newlines, filtering out empty lines, and returning an array of strings.

Extracted items are automatically normalized when pushed to the `repo` if a normalization function is provided under the `normalize` key in the repo object.

```typescript
const repos = [
  {
    itemType: 'todos',
    normalize: normalizeTodo,
  },
  {
    itemType: 'users',
    normalize: normalizeUser,
  },
  {
    itemType: 'attachments',
    normalize: normalizeAttachment,
  },
];
```

Each line of the file contains `id`, `created_date`, and `modified_date` fields
in the beginning of the record. These fields are required.
All other fields are contained within the `data` attribute.

```json {2-4}
{
  "id": "2102e01F",
  "created_date": "1972-03-29T22:04:47+01:00",
  "modified_date": "1970-01-01T01:00:04+01:00",
  "data": {
    "actual_close_date": "1970-01-01T02:33:18+01:00",
    "creator": "b8",
    "owner": "A3A",
    "rca": null,
    "severity": "fatal",
    "summary": "Lorem ipsum",
  }
}
```

If the item you are normalizing is a work item (a ticket, task, issue, or similar),
it should also contain the `item_url_field` within the `data` attribute. 
This field should be assigned a URL that points to the item in the external system.
This link is visible in the airdropped item in the DevRev app, 
helping users to easily locate the item in the external system.

```json {12}
{
  "id": "2102e01F",
  "created_date": "1972-03-29T22:04:47+01:00",
  "modified_date": "1970-01-01T01:00:04+01:00",
  "data": {
    "actual_close_date": "1970-01-01T02:33:18+01:00",
    "creator": "b8",
    "owner": "A3A",
    "rca": null,
    "severity": "fatal",
    "summary": "Lorem ipsum",
    "item_url_field": "https://external-system.com/issue/123"
  }
}
```

## State handling

To enable information passing between invocations and runs, a limited amount of data can be saved as the snap-in `state`. 
Snap-in `state` persists between phases in one sync run as well as between multiple sync runs.

You can access the `state` through SDK's `adapter` object.

```typescript
adapter.state['users'].completed = true;
```

A snap-in must consult its state to obtain information on when the last successful forward sync started.

- The snap-in's `state` is loaded at the start of each invocation and saved at its end.
- The snap-in's `state` must be a valid JSON object.
- Each sync direction (to DevRev and from DevRev) has its own `state` object that is not shared.
- The snap-in `state` should be smaller than 1 MB, which maps to approximately 500,000 characters.

Effective use of the state and breaking down the problem into smaller chunks are crucial for good performance and user experience. Without knowing what has been processed, the snap-in extracts the same data multiple times, using valuable API capacity and time, and possibly duplicates the data inside DevRev or the external application.

Adding more data to the state can help with pagination and rate limiting by saving the point at which extraction was left off.

```typescript
export const initialExtractorState: ExtractorState = {
  todos: { completed: false },
  users: { completed: false },
  attachments: { completed: false },
};
```

To test the state during snap-in development, you can pass in the option to decrease the timeout between snap-in invocations.

```typescript
await spawn<DummyExtractorState>({
    ...,
    option: {
        timeout: 1 * 60 * 1000; // 1 minute in milliseconds
    }
});
```
