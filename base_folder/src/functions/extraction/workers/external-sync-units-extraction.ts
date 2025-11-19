import { ExtractorEventType, processTask } from "@devrev/ts-adaas";

processTask({
  task: async ({ adapter }) => {},
  onTimeout: async ({ adapter }) => {
    await adapter.emit(ExtractorEventType.ExtractionExternalSyncUnitsError, {
      error: {
        message: 'Failed to extract external sync units. Lambda timeout.',
      },
    });
  },
});
