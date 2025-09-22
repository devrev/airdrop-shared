import { AirdropEvent, AirdropMessage } from '@devrev/ts-adaas';
import { FunctionInput } from './types';

export function convertToAirdropEvent(fi: FunctionInput): AirdropEvent {
    // Create a properly structured AirdropMessage
    const airdropMessage: AirdropMessage = {
      connection_data: fi.payload.connection_data,
      event_context: {
        ...fi.payload.event_context,
        ...fi.context,
        request_id: fi.execution_metadata?.request_id,
      },
      event_type: fi.payload.event_type,
      event_data: fi.payload.event_data || {},
    };
    
    return {
      context: {
        ...fi.context,
        secrets: {
          service_account_token: fi.context.secrets?.service_account_token || '',
          ...fi.context.secrets,
        },
      },
      payload: airdropMessage,
      execution_metadata: fi.execution_metadata,
      input_data: fi.input_data,
    };
  }
  