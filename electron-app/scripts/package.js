#!/usr/bin/env node

/**
 * PrivAI Desktop - Packaging Script
 * 
 * This script creates platform-specific packages for the PrivAI desktop application.
 * It supports Windows, macOS, and Linux packaging with appropriate installers.
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

// Configuration
const CONFIG = {
  projectRoot: path.join(__dirname, '..'),
  distPath: path.join(__dirname, '../dist'),
  buildPath: path.join(__dirname, '../build'),
  platforms: {
    win32: {
      name: 'Windows',
      targets: ['nsis', 'portable'],
      arch: ['x64', 'ia32']
    },
    darwin: {
      name: 'macOS',
      targets: ['dmg', 'zip'],
      arch: ['x64', 'arm64']
    },
    linux: {
      name: 'Linux',
      targets: ['AppImage', 'deb', 'rpm'],
      arch: ['x64', 'arm64']
    }
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
function execCommand(command, cwd = process.cwd()) {
  try {
    log(`🔧 Executing: ${command}`, 'cyan');
    const result = execSync(command, { 
      cwd, 
      stdio: 'inherit'
    });
    return result;
  } catch (error) {
    log(`❌ Command failed: ${command}`, 'red');
    throw error;
  }
}

/**
 * Get platform configuration
 */
function getPlatformConfig() {
  const platform = process.platform;
  const config = CONFIG.platforms[platform];
  
  if (!config) {
    throw new Error(`Unsupported platform: ${platform}`);
  }
  
  return { platform, ...config };
}

/**
 * Clean previous builds
 */
function cleanBuilds() {
  log('🧹 Cleaning previous builds...', 'blue');
  
  if (fs.existsSync(CONFIG.distPath)) {
    execCommand(`rm -rf ${CONFIG.distPath}`);
  }
  
  if (fs.existsSync(CONFIG.buildPath)) {
    execCommand(`rm -rf ${CONFIG.buildPath}`);
  }
  
  log('✅ Build directories cleaned', 'green');
}

/**
 * Build application
 */
function buildApplication() {
  log('🔨 Building application...', 'blue');
  
  // Build frontend
  log('📦 Building frontend...', 'cyan');
  execCommand('npm run build-frontend');
  
  // Build backend
  log('🐍 Preparing backend...', 'cyan');
  execCommand('npm run build-backend');
  
  log('✅ Application built successfully', 'green');
}

/**
 * Package for current platform
 */
function packageForPlatform() {
  const { platform, name, targets, arch } = getPlatformConfig();
  
  log(`📦 Packaging for ${name}...`, 'blue');
  log(`Targets: ${targets.join(', ')}`, 'cyan');
  log(`Architectures: ${arch.join(', ')}`, 'cyan');
  
  // Build for current platform
  execCommand('npm run dist');
  
  log(`✅ ${name} packaging completed`, 'green');
}

/**
 * Package for specific platform
 */
function packageForSpecificPlatform(targetPlatform) {
  const config = CONFIG.platforms[targetPlatform];
  
  if (!config) {
    throw new Error(`Unsupported target platform: ${targetPlatform}`);
  }
  
  const { name, targets, arch } = config;
  
  log(`📦 Cross-compiling for ${name}...`, 'blue');
  log(`Targets: ${targets.join(', ')}`, 'cyan');
  log(`Architectures: ${arch.join(', ')}`, 'cyan');
  
  // Build for specific platform
  const command = `npm run dist-${targetPlatform}`;
  execCommand(command);
  
  log(`✅ ${name} cross-compilation completed`, 'green');
}

/**
 * Package for all platforms
 */
function packageForAllPlatforms() {
  log('🌍 Packaging for all platforms...', 'blue');
  
  const platforms = Object.keys(CONFIG.platforms);
  
  for (const platform of platforms) {
    try {
      packageForSpecificPlatform(platform);
    } catch (error) {
      log(`❌ Failed to package for ${platform}: ${error.message}`, 'red');
    }
  }
  
  log('✅ All platform packaging completed', 'green');
}

/**
 * Create installer packages
 */
function createInstallers() {
  log('📦 Creating installer packages...', 'blue');
  
  const { platform } = getPlatformConfig();
  
  switch (platform) {
    case 'win32':
      createWindowsInstallers();
      break;
    case 'darwin':
      createMacOSInstallers();
      break;
    case 'linux':
      createLinuxInstallers();
      break;
  }
  
  log('✅ Installer packages created', 'green');
}

/**
 * Create Windows installers
 */
function createWindowsInstallers() {
  log('🪟 Creating Windows installers...', 'blue');
  
  // NSIS installer
  log('📦 Creating NSIS installer...', 'cyan');
  execCommand('npm run dist-win');
  
  // Portable version
  log('📦 Creating portable version...', 'cyan');
  execCommand('npm run dist-win -- --config.win.target=portable');
  
  log('✅ Windows installers created', 'green');
}

/**
 * Create macOS installers
 */
function createMacOSInstallers() {
  log('🍎 Creating macOS installers...', 'blue');
  
  // DMG installer
  log('📦 Creating DMG installer...', 'cyan');
  execCommand('npm run dist-mac');
  
  // ZIP archive
  log('📦 Creating ZIP archive...', 'cyan');
  execCommand('npm run dist-mac -- --config.mac.target=zip');
  
  log('✅ macOS installers created', 'green');
}

/**
 * Create Linux installers
 */
function createLinuxInstallers() {
  log('🐧 Creating Linux installers...', 'blue');
  
  // AppImage
  log('📦 Creating AppImage...', 'cyan');
  execCommand('npm run dist-linux -- --config.linux.target=AppImage');
  
  // DEB package
  log('📦 Creating DEB package...', 'cyan');
  execCommand('npm run dist-linux -- --config.linux.target=deb');
  
  // RPM package
  log('📦 Creating RPM package...', 'cyan');
  execCommand('npm run dist-linux -- --config.linux.target=rpm');
  
  log('✅ Linux installers created', 'green');
}

/**
 * Verify packages
 */
function verifyPackages() {
  log('🔍 Verifying packages...', 'blue');
  
  if (!fs.existsSync(CONFIG.distPath)) {
    throw new Error('Distribution directory not found');
  }
  
  const files = fs.readdirSync(CONFIG.distPath);
  if (files.length === 0) {
    throw new Error('No distribution files found');
  }
  
  log(`✅ Found ${files.length} distribution files:`, 'green');
  
  files.forEach(file => {
    const filePath = path.join(CONFIG.distPath, file);
    const stats = fs.statSync(filePath);
    const size = (stats.size / 1024 / 1024).toFixed(2);
    const type = getFileType(file);
    
    log(`📄 ${file} (${size} MB) - ${type}`, 'cyan');
  });
}

/**
 * Get file type description
 */
function getFileType(filename) {
  const ext = path.extname(filename).toLowerCase();
  
  const types = {
    '.exe': 'Windows Executable',
    '.msi': 'Windows Installer',
    '.dmg': 'macOS Disk Image',
    '.pkg': 'macOS Package',
    '.zip': 'ZIP Archive',
    '.tar.gz': 'TAR GZ Archive',
    '.AppImage': 'Linux AppImage',
    '.deb': 'Debian Package',
    '.rpm': 'RPM Package'
  };
  
  return types[ext] || 'Unknown';
}

/**
 * Create distribution summary
 */
function createDistributionSummary() {
  log('📋 Creating distribution summary...', 'blue');
  
  const summary = {
    timestamp: new Date().toISOString(),
    platform: process.platform,
    arch: process.arch,
    nodeVersion: process.version,
    files: []
  };
  
  if (fs.existsSync(CONFIG.distPath)) {
    const files = fs.readdirSync(CONFIG.distPath);
    
    files.forEach(file => {
      const filePath = path.join(CONFIG.distPath, file);
      const stats = fs.statSync(filePath);
      
      summary.files.push({
        name: file,
        size: stats.size,
        sizeMB: (stats.size / 1024 / 1024).toFixed(2),
        type: getFileType(file),
        created: stats.birthtime.toISOString()
      });
    });
  }
  
  const summaryPath = path.join(CONFIG.distPath, 'distribution-summary.json');
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
  
  log(`✅ Distribution summary created: ${summaryPath}`, 'green');
}

/**
 * Main packaging function
 */
async function package() {
  try {
    const args = process.argv.slice(2);
    const targetPlatform = args[0];
    
    log('🚀 Starting PrivAI Desktop packaging...', 'bright');
    log('=' * 60, 'blue');
    
    // Clean previous builds
    cleanBuilds();
    
    // Build application
    buildApplication();
    
    // Package for platform
    if (targetPlatform) {
      if (targetPlatform === 'all') {
        packageForAllPlatforms();
      } else {
        packageForSpecificPlatform(targetPlatform);
      }
    } else {
      packageForPlatform();
    }
    
    // Create installers
    createInstallers();
    
    // Verify packages
    verifyPackages();
    
    // Create distribution summary
    createDistributionSummary();
    
    log('=' * 60, 'green');
    log('🎉 PrivAI Desktop packaging completed successfully!', 'bright');
    log(`📁 Distribution files: ${CONFIG.distPath}`, 'cyan');
    
  } catch (error) {
    log('=' * 60, 'red');
    log(`❌ Packaging failed: ${error.message}`, 'red');
    process.exit(1);
  }
}

// Run packaging if called directly
if (require.main === module) {
  package();
}

module.exports = { package, CONFIG };
