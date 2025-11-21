### Implementing Incremental Data Sync

Incremental data synchronization retrieves only records that have been created or updated since the time of the last successful sync.

This process requires reading the timestamp of the last successful data extraction from the state object. After every successful sync, this timestamp gets updated automatically.

### When to handle incremental mode and how to check if we're in incremental mode

Incremental mode should only be handled if the "event_type" is `EXTRACTION_DATA_START`. To check if we're in incremental mode, you should check if the value of `adapter.event.payload.event_context.mode` is `SyncMode.INCREMENTAL`.

### ts-adaas Library Details

The information about the last successful sync is stored in the `adapter.state.lastSuccessfulSyncStarted` property (of format ISO 8601 Extended Format with timezone).

Here are some further remarks:
- Field `adapter.state.lastSuccessfulSyncStarted` should be the source of truth for the last successful sync time. `adapter.state.lastSuccessfulSyncStarted` should be read *only* from `adapter.state` (e.g. not from the `adapter.event.payload`). No need to define the `adapter.state.lastSuccessfulSyncStarted` in The State Object explicitly.
- Field `adapter.state.LastSyncStarted` *should not* play a role in the incremental mode (`adapter.state.lastSuccessfulSyncStarted` contains all the information needed).

### High level: How to implement incremental mode

Here's how to handle incremental mode:

- Reset The Extraction State, indicating the sync hasn't been completed yet for all data types that we support incremental mode.
- Set field "modifiedSince" (The Modified Since Field) to the value of `adapter.state.lastSuccessfulSyncStarted`
- Then, you should retrieve and push only the resources from the API that have been modified since The Modified Since Field (either server side, if the API supports it, or client-side, if the API doesn't support it).


#### Remember the last successful sync time

If the sync is successful, update the state object with the current time.

Note: No need to modify any time-related properties in adapter.state object. 

#### Example

Let's imagine the following scenario:

We're extracting the following resources from the 3rd party system:

- Users
- Tasks
- Attachments (Attachments are tied to Tasks)

To persist information over multiple syncs, we're using the following The State Object.

```typescript
export interface ExtractorState {
  users: {
    completed: boolean;
  };
  tasks: {
    completed: boolean;
    modifiedSince?: string;
  };
  attachments: {
    completed: boolean;
  };
}

export const initialState: ExtractorState = {
  users: { completed: false },
  tasks: { completed: false },
  attachments: { completed: false },
};
```

Our goal is to support incremental mode for the Tasks resource. To do that, we need to reset The State Object for the Tasks resource and set the modifiedSince field to the value of the last successful sync time. Since Attachments are tied to Tasks, we need to reset the Attachments resource as well.

This is how we are going to handle the incremental mode in The Worker Thread:

```typescript
processTask<ExtractorState>({
    task: async ({ adapter }) => {
      // ... ... 
      if (adapter.event.payload.event_type === EventType.ExtractionDataStart) {

        // If this is an incremental sync, we need to reset the state for the item types.
        if (adapter.event.payload.event_context.mode === SyncMode.INCREMENTAL) {
          adapter.state.tasks = initialState.tasks;  // Or something along the lines of adapter.state.tasks.completed = false;
          adapter.state.attachments = initialState.attachments;  // Or something along the lines of adapter.state.attachments.completed = false;
          adapter.state.tasks.modifiedSince = adapter.state.lastSuccessfulSyncStarted;
        }
      }

      // TODO: Here, fetch only the tasks that have been modified since the last successful sync time and push only those to the designated repository.
    }
    onTimeout: async ({ adapter }) => {
      // ... ... 
    }
})
```