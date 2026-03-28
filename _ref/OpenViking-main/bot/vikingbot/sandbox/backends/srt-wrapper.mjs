#!/usr/bin/env node
/**
 * SRT (Sandbox Runtime) Node.js wrapper for Python IPC
 * 
 * This script provides an IPC interface between Python and @anthropic-ai/sandbox-runtime
 * through JSON messages over stdin/stdout.
 */

import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { createRequire } from 'module';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const require = createRequire(import.meta.url);

// Use an async IIFE to handle module loading properly
(async () => {
  // Try multiple strategies to import SandboxManager
  let SandboxManager;
  let importError = null;

  // Strategy 1: Direct ESM import
  try {
    const module = await import('@anthropic-ai/sandbox-runtime');
    SandboxManager = module.SandboxManager;
    console.error('[SRT wrapper] Successfully imported via ESM');
  } catch (e) {
    importError = e;
    console.error('[SRT wrapper] ESM import failed:', e.message);
    
    // Strategy 2: Try to find the package in common locations
    try {
      const paths = [
        // Project local node_modules
        join(__dirname, '..', '..', '..', 'node_modules'),
        // Global node_modules (common locations)
        '/usr/local/lib/node_modules',
        '/usr/lib/node_modules',
        ...(require.resolve.paths('') || []).map(p => join(p, '..', 'node_modules')),
      ];
      
      for (const basePath of paths) {
        try {
          const pkgPath = join(basePath, '@anthropic-ai', 'sandbox-runtime');
          const pkgJsonPath = join(pkgPath, 'package.json');
          
          // Check if package exists
          try {
            const pkgJson = require(pkgJsonPath);
            const mainPath = join(pkgPath, pkgJson.module || pkgJson.main || 'index.js');
            
            // Try to import from found path
            const module = await import(mainPath);
            SandboxManager = module.SandboxManager;
            console.error(`[SRT wrapper] Successfully imported from: ${pkgPath}`);
            importError = null;
            break;
          } catch (innerErr) {
            // Continue to next path
            continue;
          }
        } catch (pathErr) {
          continue;
        }
      }
    } catch (strategy2Err) {
      console.error('[SRT wrapper] Strategy 2 failed:', strategy2Err.message);
    }
  }

  // If all strategies failed, provide helpful error
  if (!SandboxManager) {
    console.error('[SRT wrapper] FATAL: Failed to import @anthropic-ai/sandbox-runtime');
    console.error('[SRT wrapper] Please install it with: npm install -g @anthropic-ai/sandbox-runtime');
    if (importError) {
      console.error('[SRT wrapper] Original error:', importError);
    }
    process.exit(1);
  }

  // Now continue with the rest of the script
  let initialized = false;

  // Process incoming messages from stdin
  process.stdin.setEncoding('utf8');

  let buffer = '';

  process.stdin.on('data', (chunk) => {
    buffer += chunk;
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';
    
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const message = JSON.parse(line);
        handleMessage(message);
      } catch (error) {
        sendError('Failed to parse message: ' + error.message);
      }
    }
  });

  process.stdin.on('end', () => {
    if (buffer.trim()) {
      try {
        const message = JSON.parse(buffer);
        handleMessage(message);
      } catch (error) {
        sendError('Failed to parse final message: ' + error.message);
      }
    }
  });

  async function handleMessage(message) {
    try {
      switch (message.type) {
        case 'initialize':
          await initialize(message.config);
          break;
        case 'execute':
          await executeCommand(message.command, message.timeout, message.customConfig);
          break;
        case 'read_file':
          await readFile(message.path);
          break;
        case 'write_file':
          await writeFile(message.path, message.content);
          break;
        case 'list_dir':
          await listDir(message.path);
          break;
        case 'update_config':
          updateConfig(message.config);
          break;
        case 'get_proxy_ports':
          getProxyPorts();
          break;
        case 'reset':
          await reset();
          break;
        case 'ping':
          sendResponse({ type: 'pong' });
          break;
        default:
          sendError('Unknown message type: ' + message.type);
      }
    } catch (error) {
      sendError(error.message);
    }
  }

  async function initialize(config) {
    if (initialized) {
      sendError('Already initialized');
      return;
    }
    
    // Check dependencies first
    const deps = SandboxManager.checkDependencies();
    if (deps.errors.length > 0) {
      sendResponse({
        type: 'initialize_failed',
        errors: deps.errors,
        warnings: deps.warnings
      });
      return;
    }
    
    try {
      await SandboxManager.initialize(config);
      initialized = true;
      
      sendResponse({
        type: 'initialized',
        warnings: deps.warnings
      });
    } catch (error) {
      sendResponse({
        type: 'initialize_failed',
        errors: [error.message]
      });
    }
  }

  async function executeCommand(command, timeout, customConfig) {
    if (!initialized) {
      sendError('Not initialized');
      return;
    }
    
    try {
      const sandboxedCommand = await SandboxManager.wrapWithSandbox(
        command,
        undefined,
        customConfig
      );
      
      // Execute the sandboxed command
      const { exec } = await import('child_process');
      const { promisify } = await import('util');
      const execAsync = promisify(exec);
      
      let stdout = '';
      let stderr = '';
      let exitCode = 0;
      
      try {
        const result = await execAsync(sandboxedCommand, {
          timeout: timeout || 60000,
          cwd: process.argv[3] || process.cwd()
        });
        stdout = result.stdout;
        stderr = result.stderr;
        exitCode = 0;
      } catch (error) {
        stdout = error.stdout || '';
        stderr = error.stderr || '';
        exitCode = error.code || 1;
      }
      
      // Get violations
      const violationStore = SandboxManager.getSandboxViolationStore();
      const violations = violationStore.getViolationsForCommand(command);
      
      sendResponse({
        type: 'executed',
        stdout,
        stderr,
        exitCode,
        violations: violations.map(v => ({
          line: v.line,
          timestamp: v.timestamp.toISOString(),
          command: v.command
        }))
      });
    } catch (error) {
      sendError('Execution failed: ' + error.message);
    }
  }

  async function readFile(path) {
    if (!initialized) {
      sendError('Not initialized');
      return;
    }
    
    try {
      // Use cat command through sandbox to read file
      const result = await executeCommandInternal(`cat "${path}"`, 30000);
      
      if (result.exitCode !== 0) {
        sendError('Read file failed: ' + (result.stderr || 'Unknown error'));
        return;
      }
      
      sendResponse({
        type: 'file_read',
        content: result.stdout
      });
    } catch (error) {
      sendError('Read file failed: ' + error.message);
    }
  }

  async function writeFile(path, content) {
    if (!initialized) {
      sendError('Not initialized');
      return;
    }
    
    try {
      // Escape content for shell
      const escapedContent = content.replace(/'/g, "'\\''");
      const escapedPath = path.replace(/'/g, "'\\''");
      
      // First ensure directory exists, then write file through sandbox
      const { dirname } = await import('path');
      const dir = dirname(path);
      const escapedDir = dir.replace(/'/g, "'\\''");
      
      // Create directory first
      const mkdirResult = await executeCommandInternal(`mkdir -p '${escapedDir}'`, 30000);
      if (mkdirResult.exitCode !== 0) {
        sendError('Create directory failed: ' + (mkdirResult.stderr || 'Unknown error'));
        return;
      }
      
      // Write file using here-doc through sandbox
      const writeResult = await executeCommandInternal(`cat > '${escapedPath}' << 'EOF_SANDBOX'\n${content}\nEOF_SANDBOX`, 30000);
      
      if (writeResult.exitCode !== 0) {
        sendError('Write file failed: ' + (writeResult.stderr || 'Unknown error'));
        return;
      }
      
      sendResponse({
        type: 'file_written'
      });
    } catch (error) {
      sendError('Write file failed: ' + error.message);
    }
  }

  async function listDir(path) {
    if (!initialized) {
      sendError('Not initialized');
      return;
    }
    
    try {
      // Use ls -la command through sandbox to list directory
      const escapedPath = path.replace(/'/g, "'\\''");
      const result = await executeCommandInternal(`ls -la '${escapedPath}'`, 30000);
      
      if (result.exitCode !== 0) {
        sendError('List dir failed: ' + (result.stderr || 'Unknown error'));
        return;
      }
      
      // Parse ls -la output to get items
      const items = [];
      const lines = result.stdout.trim().split('\n');
      
      // Skip first two lines (total and .)
      for (let i = 2; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        const parts = line.split(/\s+/);
        if (parts.length >= 9) {
          const name = parts.slice(8).join(' ');
          if (name === '.' || name === '..') continue;
          
          const isDir = parts[0].startsWith('d');
          items.push({
            name: name,
            is_dir: isDir
          });
        }
      }
      
      sendResponse({
        type: 'dir_listed',
        items: items
      });
    } catch (error) {
      sendError('List dir failed: ' + error.message);
    }
  }

  async function executeCommandInternal(command, timeout) {
    const sandboxedCommand = await SandboxManager.wrapWithSandbox(command);
    
    const { exec } = await import('child_process');
    const { promisify } = await import('util');
    const execAsync = promisify(exec);
    
    let stdout = '';
    let stderr = '';
    let exitCode = 0;
    
    try {
      const result = await execAsync(sandboxedCommand, {
        timeout: timeout || 60000,
        cwd: process.argv[3] || process.cwd()
      });
      stdout = result.stdout;
      stderr = result.stderr;
      exitCode = 0;
    } catch (error) {
      stdout = error.stdout || '';
      stderr = error.stderr || '';
      exitCode = error.code || 1;
    }
    
    return { stdout, stderr, exitCode };
  }

  function updateConfig(config) {
    if (!initialized) {
      sendError('Not initialized');
      return;
    }
    
    SandboxManager.updateConfig(config);
    sendResponse({ type: 'config_updated' });
  }

  function getProxyPorts() {
    if (!initialized) {
      sendError('Not initialized');
      return;
    }
    
    const httpProxyPort = SandboxManager.getProxyPort();
    const socksProxyPort = SandboxManager.getSocksProxyPort();
    
    sendResponse({
      type: 'proxy_ports',
      httpProxyPort,
      socksProxyPort
    });
  }

  async function reset() {
    if (!initialized) {
      sendError('Not initialized');
      return;
    }
    
    try {
      await SandboxManager.reset();
      initialized = false;
      sendResponse({ type: 'reset' });
    } catch (error) {
      sendError('Reset failed: ' + error.message);
    }
  }

  function sendResponse(response) {
    process.stdout.write(JSON.stringify(response) + '\n');
  }

  function sendError(message) {
    sendResponse({
      type: 'error',
      message
    });
  }

  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    if (initialized) {
      try {
        await SandboxManager.reset();
      } catch (error) {
        // Ignore cleanup errors on shutdown
      }
    }
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    if (initialized) {
      try {
        await SandboxManager.reset();
      } catch (error) {
        // Ignore cleanup errors on shutdown
      }
    }
    process.exit(0);
  });

  // Send ready signal
  sendResponse({ type: 'ready' });
})();
