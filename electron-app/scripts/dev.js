#!/usr/bin/env node

/**
 * PrivAI Desktop - Development Script
 * 
 * This script starts the development environment for the PrivAI desktop application,
 * including the backend, frontend, and Electron app in development mode.
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const CONFIG = {
  projectRoot: path.join(__dirname, '..'),
  frontendPath: path.join(__dirname, '../../frontend'),
  backendPath: path.join(__dirname, '../../backend'),
  electronPath: path.join(__dirname, '..')
};

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

/**
 * Log with color and timestamp
 */
function log(message, color = 'reset', process = 'DEV') {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`${colors[color]}[${timestamp}] [${process}] ${message}${colors.reset}`);
}

/**
 * Start backend process
 */
function startBackend() {
  return new Promise((resolve, reject) => {
    log('🐍 Starting FastAPI backend...', 'blue', 'BACKEND');
    
    const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';
    const backendScript = path.join(CONFIG.backendPath, 'app', 'main_simple.py');
    
    const backendProcess = spawn(pythonCommand, [backendScript], {
      cwd: CONFIG.backendPath,
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: process.platform === 'win32'
    });
    
    backendProcess.stdout.on('data', (data) => {
      log(data.toString().trim(), 'cyan', 'BACKEND');
    });
    
    backendProcess.stderr.on('data', (data) => {
      log(data.toString().trim(), 'red', 'BACKEND');
    });
    
    backendProcess.on('close', (code) => {
      if (code !== 0) {
        log(`Backend process exited with code ${code}`, 'red', 'BACKEND');
        reject(new Error(`Backend process exited with code ${code}`));
      }
    });
    
    backendProcess.on('error', (error) => {
      log(`Failed to start backend: ${error.message}`, 'red', 'BACKEND');
      reject(error);
    });
    
    // Wait for backend to start
    setTimeout(() => {
      log('✅ Backend started successfully', 'green', 'BACKEND');
      resolve(backendProcess);
    }, 3000);
  });
}

/**
 * Start frontend process
 */
function startFrontend() {
  return new Promise((resolve, reject) => {
    log('🎨 Starting React frontend...', 'blue', 'FRONTEND');
    
    // Check if frontend dependencies are installed
    const nodeModulesPath = path.join(CONFIG.frontendPath, 'node_modules');
    if (!fs.existsSync(nodeModulesPath)) {
      log('📦 Installing frontend dependencies...', 'yellow', 'FRONTEND');
      exec('npm install', { cwd: CONFIG.frontendPath }, (error) => {
        if (error) {
          log(`Failed to install dependencies: ${error.message}`, 'red', 'FRONTEND');
          reject(error);
          return;
        }
        startFrontendProcess();
      });
    } else {
      startFrontendProcess();
    }
    
    function startFrontendProcess() {
      const frontendProcess = spawn('npm', ['start'], {
        cwd: CONFIG.frontendPath,
        stdio: ['pipe', 'pipe', 'pipe'],
        shell: true
      });
      
      frontendProcess.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output.includes('Local:') || output.includes('On Your Network:')) {
          log('✅ Frontend started successfully', 'green', 'FRONTEND');
          resolve(frontendProcess);
        }
        log(output, 'cyan', 'FRONTEND');
      });
      
      frontendProcess.stderr.on('data', (data) => {
        log(data.toString().trim(), 'red', 'FRONTEND');
      });
      
      frontendProcess.on('close', (code) => {
        if (code !== 0) {
          log(`Frontend process exited with code ${code}`, 'red', 'FRONTEND');
          reject(new Error(`Frontend process exited with code ${code}`));
        }
      });
      
      frontendProcess.on('error', (error) => {
        log(`Failed to start frontend: ${error.message}`, 'red', 'FRONTEND');
        reject(error);
      });
    }
  });
}

/**
 * Start Electron process
 */
function startElectron() {
  return new Promise((resolve, reject) => {
    log('⚡ Starting Electron app...', 'blue', 'ELECTRON');
    
    // Set development environment
    process.env.NODE_ENV = 'development';
    
    const electronProcess = spawn('npm', ['start'], {
      cwd: CONFIG.electronPath,
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: true,
      env: { ...process.env, NODE_ENV: 'development' }
    });
    
    electronProcess.stdout.on('data', (data) => {
      log(data.toString().trim(), 'magenta', 'ELECTRON');
    });
    
    electronProcess.stderr.on('data', (data) => {
      log(data.toString().trim(), 'red', 'ELECTRON');
    });
    
    electronProcess.on('close', (code) => {
      log(`Electron process exited with code ${code}`, 'yellow', 'ELECTRON');
      resolve();
    });
    
    electronProcess.on('error', (error) => {
      log(`Failed to start Electron: ${error.message}`, 'red', 'ELECTRON');
      reject(error);
    });
    
    // Wait a bit for Electron to start
    setTimeout(() => {
      log('✅ Electron started successfully', 'green', 'ELECTRON');
      resolve(electronProcess);
    }, 2000);
  });
}

/**
 * Handle process cleanup
 */
function setupCleanup(processes) {
  const cleanup = () => {
    log('🛑 Shutting down development environment...', 'yellow', 'CLEANUP');
    
    processes.forEach((proc, index) => {
      if (proc && !proc.killed) {
        log(`Stopping process ${index + 1}...`, 'yellow', 'CLEANUP');
        proc.kill();
      }
    });
    
    log('✅ Development environment shut down', 'green', 'CLEANUP');
    process.exit(0);
  };
  
  // Handle Ctrl+C
  process.on('SIGINT', cleanup);
  
  // Handle process exit
  process.on('exit', cleanup);
  
  // Handle uncaught exceptions
  process.on('uncaughtException', (error) => {
    log(`Uncaught exception: ${error.message}`, 'red', 'ERROR');
    cleanup();
  });
  
  // Handle unhandled rejections
  process.on('unhandledRejection', (reason, promise) => {
    log(`Unhandled rejection: ${reason}`, 'red', 'ERROR');
    cleanup();
  });
}

/**
 * Wait for service to be available
 */
function waitForService(url, maxAttempts = 30, delay = 1000) {
  return new Promise((resolve, reject) => {
    const http = require('http');
    const https = require('https');
    const client = url.startsWith('https') ? https : http;
    
    let attempts = 0;
    
    const checkService = () => {
      attempts++;
      
      const req = client.get(url, (res) => {
        if (res.statusCode === 200) {
          resolve();
        } else {
          if (attempts < maxAttempts) {
            setTimeout(checkService, delay);
          } else {
            reject(new Error(`Service not available after ${maxAttempts} attempts`));
          }
        }
      });
      
      req.on('error', () => {
        if (attempts < maxAttempts) {
          setTimeout(checkService, delay);
        } else {
          reject(new Error(`Service not available after ${maxAttempts} attempts`));
        }
      });
      
      req.setTimeout(5000, () => {
        req.destroy();
        if (attempts < maxAttempts) {
          setTimeout(checkService, delay);
        } else {
          reject(new Error(`Service not available after ${maxAttempts} attempts`));
        }
      });
    };
    
    checkService();
  });
}

/**
 * Main development function
 */
async function startDev() {
  try {
    log('🚀 Starting PrivAI Desktop development environment...', 'bright', 'DEV');
    log('=' * 60, 'blue');
    
    const processes = [];
    
    // Start backend
    const backendProcess = await startBackend();
    processes.push(backendProcess);
    
    // Wait for backend to be ready
    log('⏳ Waiting for backend to be ready...', 'yellow', 'DEV');
    await waitForService('http://localhost:8000/health');
    log('✅ Backend is ready', 'green', 'DEV');
    
    // Start frontend
    const frontendProcess = await startFrontend();
    processes.push(frontendProcess);
    
    // Wait for frontend to be ready
    log('⏳ Waiting for frontend to be ready...', 'yellow', 'DEV');
    await waitForService('http://localhost:3000');
    log('✅ Frontend is ready', 'green', 'DEV');
    
    // Start Electron
    const electronProcess = await startElectron();
    processes.push(electronProcess);
    
    // Setup cleanup
    setupCleanup(processes);
    
    log('=' * 60, 'green');
    log('🎉 Development environment started successfully!', 'bright', 'DEV');
    log('📱 Electron app should open automatically', 'cyan', 'DEV');
    log('🌐 Frontend: http://localhost:3000', 'cyan', 'DEV');
    log('🔧 Backend: http://localhost:8000', 'cyan', 'DEV');
    log('🛑 Press Ctrl+C to stop all processes', 'yellow', 'DEV');
    
  } catch (error) {
    log(`❌ Failed to start development environment: ${error.message}`, 'red', 'ERROR');
    process.exit(1);
  }
}

// Run development if called directly
if (require.main === module) {
  startDev();
}

module.exports = { startDev, CONFIG };
