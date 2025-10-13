import { convertToAirdropEvent } from '../../core/utils';
import { FunctionInput } from '../../core/types';
import { spawn, EventType } from '@devrev/ts-adaas';

function getWorkerPerExtractionPhase(event: FunctionInput) {
  let path;
  switch (event.payload.event_type) {
    case EventType.ExtractionExternalSyncUnitsStart:
      path = __dirname + '/workers/external-sync-units-extraction';
      break;
    case EventType.ExtractionMetadataStart:
      path = __dirname + '/workers/metadata-extraction';
      break;
    case EventType.ExtractionDataStart:
    case EventType.ExtractionDataContinue:
      path = __dirname + '/workers/data-extraction';
      break;
    case EventType.ExtractionAttachmentsStart:
    case EventType.ExtractionAttachmentsContinue:
      path = __dirname + '/workers/attachments-extraction';
      break;
  }
  return path;
}

const run = async (events: FunctionInput[]) => {
  for (const event of events) {
    const file = getWorkerPerExtractionPhase(event);
    await spawn({
      event: convertToAirdropEvent(event),
      workerPath: file,
      initialState: {},
    });
  }
};

export default run;
