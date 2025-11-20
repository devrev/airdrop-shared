import { processTask, ExtractorEventType } from '@devrev/ts-adaas';
  
processTask({
  task: async ({ adapter }) => {},
  onTimeout: async ({ adapter }) => {
    await adapter.emit(ExtractorEventType.ExtractionMetadataError, {
      error: { message: 'Failed to extract metadata. Lambda timeout.' },
    });
  },
});