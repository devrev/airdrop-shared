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

// Function to reset the mock server state
const resetMockServer = async () => {
  try {
    const http = require('http');
    
    // Simple HTTP request that properly closes the connection
    const postData = '';
    const options = {
      hostname: 'localhost',
      port: 8003,
      path: '/reset-mock-server',
      method: 'POST',
      agent: false,
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const response = await new Promise((resolve, reject) => {
      const req = http.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => resolve({ status: res.statusCode, data }));
      });
      
      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });
      
      req.setTimeout(5000);
      req.write(postData);
      req.end();
    });
    
    if (response.status !== 200) {
      console.warn(`Failed to reset mock server: ${response.status}`);
    }
  } catch (error) {
    console.warn(`Could not connect to mock server for reset: ${error.message}`);
  }
};

// Function to end rate limiting
const endRateLimiting = async () => {
  try {
    const http = require('http');
    
    // Simple HTTP request that properly closes the connection
    const postData = '';
    const options = {
      hostname: 'localhost',
      port: 8004,
      path: '/end_rate_limiting',
      method: 'POST',
      agent: false,
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const response = await new Promise((resolve, reject) => {
      const req = http.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => resolve({ status: res.statusCode, data }));
      });
      
      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });
      
      req.setTimeout(5000);
      req.write(postData);
      req.end();
    });
    
    if (response.status !== 200) {
      console.warn(`Failed to end rate limiting: ${response.status}`);
    }
  } catch (error) {
    console.warn(`Could not connect to rate limiting server: ${error.message}`);
  }
};

// This hook runs BEFORE each test in every test file.
beforeEach(async () => {
  try {
    await resetMockServer();
    await endRateLimiting();
  } catch (error) {
    originalConsole.error(
      '[jest.setup.js] beforeEach: Failed to reset mock server. ' +
      `Error: ${error instanceof Error ? error.message : String(error)}`
    );
    // Don't throw - allow tests to run even if reset fails
    // The internal resetMockServer() already handles errors gracefully
  }
});