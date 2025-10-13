import { processTask } from '@devrev/ts-adaas';
  
processTask({
  task: async ({ adapter }) => {},
  onTimeout: async ({ adapter }) => {},
});