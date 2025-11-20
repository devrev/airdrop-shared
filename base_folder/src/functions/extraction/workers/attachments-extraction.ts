import { ExtractorEventType, processTask } from '@devrev/ts-adaas';

processTask({
  task: async ({ adapter }) => {},
  onTimeout: async ({ adapter }) => {
    await adapter.emit(ExtractorEventType.ExtractionAttachmentsProgress);
  },
});