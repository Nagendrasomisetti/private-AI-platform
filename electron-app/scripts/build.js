#!/usr/bin/env node

/**
 * PrivAI Desktop - Build Script
 * 
 * This script handles the complete build process for the PrivAI desktop application,
 * including frontend build, backend preparation, and Electron packaging.
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const rimraf = require('rimraf');

// Configuration
const CONFIG = {
  projectRoot: path.join(__dirname, '..'),
  frontendPath: path.join(__dirname, '../../frontend'),
  backendPath: path.join(__dirname, '../../backend'),
  buildPath: path.join(__dirname, '../build'),
  distPath: path.join(__dirname, '../dist'),
  platforms: {
    win32: 'windows',
    darwin: 'macos',
    linux: 'linux'
  }
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
 * Log with color
 */
function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

/**
 * Execute command with error handling
 */
function execCommand(command, cwd = process.cwd(), options = {}) {
  try {
    log(`🔧 Executing: ${command}`, 'cyan');
    const result = execSync(command, { 
      cwd, 
      stdio: 'inherit',
      ...options 
    });
    return result;
  } catch (error) {
    log(`❌ Command failed: ${command}`, 'red');
    log(`Error: ${error.message}`, 'red');
    throw error;
  }
}

/**
 * Check if command exists
 */
function commandExists(command) {
  try {
    execSync(`which ${command}`, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

/**
 * Check prerequisites
 */
function checkPrerequisites() {
  log('🔍 Checking prerequisites...', 'blue');
  
  const checks = [
    { name: 'Node.js', command: 'node --version' },
    { name: 'npm', command: 'npm --version' },
    { name: 'Python', command: 'python --version' }
  ];
  
  for (const check of checks) {
    try {
      const version = execSync(check.command, { encoding: 'utf8' }).trim();
      log(`✅ ${check.name}: ${version}`, 'green');
    } catch (error) {
      log(`❌ ${check.name} not found`, 'red');
      throw new Error(`${check.name} is required but not found`);
    }
  }
  
  log('✅ All prerequisites met', 'green');
}

/**
 * Clean build directories
 */
function cleanBuild() {
  log('🧹 Cleaning build directories...', 'blue');
  
  const dirsToClean = [
    CONFIG.buildPath,
    CONFIG.distPath,
    path.join(CONFIG.frontendPath, 'build'),
    path.join(CONFIG.frontendPath, 'node_modules'),
    path.join(CONFIG.backendPath, '__pycache__'),
    path.join(CONFIG.backendPath, '*.pyc')
  ];
  
  for (const dir of dirsToClean) {
    if (fs.existsSync(dir)) {
      log(`🗑️  Removing: ${dir}`, 'yellow');
      rimraf.sync(dir);
    }
  }
  
  log('✅ Build directories cleaned', 'green');
}

/**
 * Build frontend
 */
function buildFrontend() {
  log('🎨 Building frontend...', 'blue');
  
  // Install frontend dependencies
  log('📦 Installing frontend dependencies...', 'cyan');
  execCommand('npm install', CONFIG.frontendPath);
  
  // Build React app
  log('🔨 Building React application...', 'cyan');
  execCommand('npm run build', CONFIG.frontendPath);
  
  // Verify build
  const buildPath = path.join(CONFIG.frontendPath, 'build');
  if (!fs.existsSync(buildPath)) {
    throw new Error('Frontend build failed - build directory not found');
  }
  
  log('✅ Frontend build completed', 'green');
}

/**
 * Prepare backend
 */
function prepareBackend() {
  log('🐍 Preparing backend...', 'blue');
  
  // Install backend dependencies
  log('📦 Installing backend dependencies...', 'cyan');
  execCommand('pip install -r requirements.txt', CONFIG.backendPath);
  
  // Create backend startup script
  const startupScript = `#!/usr/bin/env python3
"""
PrivAI Backend Startup Script for Electron
This script starts the FastAPI backend for the Electron app.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Start the FastAPI backend
if __name__ == "__main__":
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start the backend
        subprocess.run([
            sys.executable, "-m", "app.main_simple"
        ], check=True)
    except Exception as e:
        print(f"Error starting backend: {e}")
        sys.exit(1)
`;
  
  const scriptPath = path.join(CONFIG.backendPath, 'start_backend.py');
  fs.writeFileSync(scriptPath, startupScript);
  
  // Make script executable on Unix systems
  if (process.platform !== 'win32') {
    execCommand(`chmod +x ${scriptPath}`);
  }
  
  log('✅ Backend prepared', 'green');
}

/**
 * Build Electron app
 */
function buildElectron() {
  log('⚡ Building Electron application...', 'blue');
  
  // Install Electron dependencies
  log('📦 Installing Electron dependencies...', 'cyan');
  execCommand('npm install', CONFIG.projectRoot);
  
  // Build Electron app
  log('🔨 Building Electron app...', 'cyan');
  execCommand('npm run pack', CONFIG.projectRoot);
  
  log('✅ Electron build completed', 'green');
}

/**
 * Create distribution packages
 */
function createDistributions() {
  log('📦 Creating distribution packages...', 'blue');
  
  const platform = process.platform;
  const platformName = CONFIG.platforms[platform] || platform;
  
  log(`🏗️  Building for ${platformName}...`, 'cyan');
  
  try {
    execCommand('npm run dist', CONFIG.projectRoot);
    log(`✅ ${platformName} distribution created`, 'green');
  } catch (error) {
    log(`❌ Failed to create ${platformName} distribution: ${error.message}`, 'red');
    throw error;
  }
}

/**
 * Verify build
 */
function verifyBuild() {
  log('🔍 Verifying build...', 'blue');
  
  const distDir = CONFIG.distPath;
  if (!fs.existsSync(distDir)) {
    throw new Error('Distribution directory not found');
  }
  
  const files = fs.readdirSync(distDir);
  if (files.length === 0) {
    throw new Error('No distribution files found');
  }
  
  log(`✅ Build verification passed - ${files.length} files created`, 'green');
  
  // List created files
  files.forEach(file => {
    const filePath = path.join(distDir, file);
    const stats = fs.statSync(filePath);
    const size = (stats.size / 1024 / 1024).toFixed(2);
    log(`📄 ${file} (${size} MB)`, 'cyan');
  });
}

/**
 * Main build function
 */
async function build() {
  try {
    log('🚀 Starting PrivAI Desktop build process...', 'bright');
    log('=' * 60, 'blue');
    
    // Check prerequisites
    checkPrerequisites();
    
    // Clean build directories
    cleanBuild();
    
    // Build frontend
    buildFrontend();
    
    // Prepare backend
    prepareBackend();
    
    // Build Electron app
    buildElectron();
    
    // Create distributions
    createDistributions();
    
    // Verify build
    verifyBuild();
    
    log('=' * 60, 'green');
    log('🎉 PrivAI Desktop build completed successfully!', 'bright');
    log(`📁 Distribution files: ${CONFIG.distPath}`, 'cyan');
    
  } catch (error) {
    log('=' * 60, 'red');
    log(`❌ Build failed: ${error.message}`, 'red');
    process.exit(1);
  }
}

// Run build if called directly
if (require.main === module) {
  build();
}

module.exports = { build, CONFIG };
