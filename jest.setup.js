let logBuffer = [];

const methods = ['log', 'info', 'warn', 'error'];

const formatArg = (arg) => {
  if (typeof arg === 'string') return arg;
  if (typeof arg === 'number' || typeof arg === 'boolean' || arg === null) return String(arg);
  try {
    return JSON.stringify(arg, null, 2);
  } catch {
    return '[Unserializable Object]';
  }
};

const originalConsole = {};

// Override console methods to buffer logs
methods.forEach((method) => {
  originalConsole[method] = console[method];
  console[method] = (...args) => {
    logBuffer.push({ method, args });
  };
});

// Monkey-patch test to track failure
const originalTest = global.test;

global.test = (name, fn, timeout) => {
  originalTest(name, async () => {
    let failed = false;
    logBuffer = [];

    try {
      await fn();
    } catch (err) {
      failed = true;
      throw err;
    } finally {
      if (failed && logBuffer.length > 0) {
        const { testPath, currentTestName } = expect.getState();

        const suite = currentTestName?.replace(name, '').trim() || '(unknown suite)';

        const start_banner = [
          '─'.repeat(12),
          `Test "${suite}" > "${name}" failed — console output follows:`,
          '─'.repeat(12),
          '',
        ].join('\n');
    
        process.stdout.write(start_banner + '\n');
  
        logBuffer.forEach(({ method, args }) => {
          const prefix = {
            log: 'console.log ',
            info: 'console.info',
            warn: 'console.warn',
            error: 'console.error',
          }[method] || 'console.log';

          const msg = args.map(formatArg).join(' ');

          process.stdout.write(`${prefix}: ${msg}\n\n`);
        });

        const end_banner = [
          '─'.repeat(12),
          `End of console output.`,
          '─'.repeat(12),
          '',
        ].join('\n');
    
        process.stdout.write(end_banner + '\n');
      }
    }
  }, timeout);
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
