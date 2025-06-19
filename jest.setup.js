// Propagate the logs, but only show warnings and errors
// Problems of this propagation approach: Node.js prints log buffer in bulk, so console logs and the associated tests that fail don't get placed together to one another.
// Let's try to keep it like that for now and see the results, but let's keep in mind that this still has room for improvement.
// Override console to only show warnings and errors
console.info('Jest custom setup installed.');

const originalConsole = global.console;
global.console = {
  ...originalConsole,
  log: () => {}, // Suppress console.log
  info: () => {}, // Suppress console.info
  debug: () => {}, // Suppress console.debug
  // Keep warn and error
  warn: originalConsole.warn,
  error: originalConsole.error,
};

const originalBeforeEach = global.beforeEach;

global.beforeEach = (fn, timeout) => {
  originalBeforeEach(async () => {
    try {
      await fn();
    } catch (err) {
      expect(`beforeEach failed: ${err.message}`).toBe('beforeEach should not fail');
      throw err;
    }
  }, timeout);
};
