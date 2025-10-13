import { ExtractorEventType, processTask } from '@devrev/ts-adaas';
import { ExtractorState } from "../index";

processTask<ExtractorState>({
  task: async ({ adapter }) => {},
  onTimeout: async ({ adapter }) => {
    await adapter.emit(ExtractorEventType.ExtractionAttachmentsProgress);
  },
});