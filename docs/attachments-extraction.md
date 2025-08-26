# Attachments Extraction Worker

## Overview
This worker handles the extraction of attachments from an external system and streams them to the Airdrop platform. It's designed to work with the `@devrev/ts-adaas` library and follows the Airdrop platform's event-driven architecture.

## Dependencies
```typescript
import {
  axios,
  axiosClient,
  ExternalSystemAttachmentStreamingParams,
  ExternalSystemAttachmentStreamingResponse,
  ExtractorEventType,
  processTask,
  serializeAxiosError,
} from '@devrev/ts-adaas';
```

## Core Components

### 1. Attachment Stream Handler
The `getAttachmentStream` function is responsible for fetching and streaming attachments from their source URLs.

```typescript
const getAttachmentStream = async ({
  item,
}: ExternalSystemAttachmentStreamingParams): Promise<ExternalSystemAttachmentStreamingResponse> => {
  const { id, url } = item;

  try {
    const fileStreamResponse = await axiosClient.get(url, {
      responseType: 'stream',
      headers: {
        'Accept-Encoding': 'identity',
      },
    });

    return { httpStream: fileStreamResponse };
  } catch (error) {
    // Error handling logic
    if (axios.isAxiosError(error)) {
      console.warn(`Error while fetching attachment ${id} from URL.`, serializeAxiosError(error));
      console.warn('Failed attachment metadata', item);
    } else {
      console.warn(`Error while fetching attachment ${id} from URL.`, error);
      console.warn('Failed attachment metadata', item);
    }

    return {
      error: {
        message: 'Error while fetching attachment ' + id + ' from URL.',
      },
    };
  }
};
```

### 2. Task Processing
The main task processing logic is implemented using the `processTask` function from the Airdrop SDK.

```typescript
processTask({
  task: async ({ adapter }) => {
    try {
      const response = await adapter.streamAttachments({
        stream: getAttachmentStream,
      });

      // Handle different response scenarios
      if (response?.delay) {
        await adapter.emit(ExtractorEventType.ExtractionAttachmentsDelay, {
          delay: response.delay,
        });
      } else if (response?.error) {
        await adapter.emit(ExtractorEventType.ExtractionAttachmentsError, {
          error: response.error,
        });
      } else {
        await adapter.emit(ExtractorEventType.ExtractionAttachmentsDone);
      }
    } catch (error) {
      console.error('An error occured while processing a task.', error);
    }
  },
  onTimeout: async ({ adapter }) => {
    await adapter.emit(ExtractorEventType.ExtractionAttachmentsProgress, {
      progress: 50,
    });
  },
});
```

## Implementation Details

### Attachment Streaming
- The worker uses `axiosClient` to fetch attachments as streams
- Headers are set to prevent compression (`'Accept-Encoding': 'identity'`)
- The response is returned as a stream for efficient handling of large files

### Error Handling
- Axios errors are handled separately using `serializeAxiosError`
- Failed attachment metadata is logged for debugging
- Error responses include the attachment ID for traceability

### Event Emission
The worker emits different events based on the processing outcome:
- `ExtractionAttachmentsDelay`: When processing needs to be delayed
- `ExtractionAttachmentsError`: When an error occurs
- `ExtractionAttachmentsDone`: When processing completes successfully
- `ExtractionAttachmentsProgress`: During timeout handling

### Timeout Handling
- On timeout, the current state is posted to the platform
- A progress event is emitted with 50% completion
- This allows the platform to resume processing from the last known state

## Usage
This worker is typically called by the Airdrop platform when it's time to process attachments. The platform will:
1. Initialize the worker with the necessary context
2. Provide attachment metadata through the `ExternalSystemAttachmentStreamingParams`
3. Handle the streaming response through the Airdrop platform's infrastructure

## Best Practices
1. Always handle both Axios and general errors
2. Log failed attachment metadata for debugging
3. Use appropriate event types for different scenarios
4. Implement timeout handling to prevent data loss
5. Use streaming for efficient handling of large files

## Related Types
- `ExternalSystemAttachmentStreamingParams`: Contains the attachment metadata
- `ExternalSystemAttachmentStreamingResponse`: Contains either the stream or error information
- `ExtractorEventType`: Enum containing all possible event types for the extraction process
