import extraction from './functions/extraction';

export const functionFactory = {
  // Add your functions here
  extraction,
} as const;

export type FunctionFactoryType = keyof typeof functionFactory;
