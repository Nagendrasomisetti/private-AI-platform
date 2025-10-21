/**
 * PrivAI Desktop Application - Main Process
 * 
 * This is the main Electron process that manages the application lifecycle,
 * creates windows, handles system events, and manages the backend process.
 */

const { app, BrowserWindow, Menu, ipcMain, dialog, shell } = require('electron');
const { autoUpdater } = require('electron-updater');
const Store = require('electron-store');
const path = require('path');
const { spawn } = require('child_process');
const fetch = require('node-fetch');

// Initialize electron store for settings
const store = new Store();

// Backend process reference
let backendProcess = null;
let mainWindow = null;
let isBackendRunning = false;

// Application configuration
const APP_CONFIG = {
  name: 'PrivAI Desktop',
  version: '1.0.0',
  backendPort: 8000,
  frontendPort: 3000,
  backendUrl: `http://localhost:8000`,
  frontendUrl: `http://localhost:3000`,
  backendPath: path.join(__dirname, '../../backend'),
  frontendPath: path.join(__dirname, '../../frontend/build')
};

/**
 * Create the main application window
 */
function createMainWindow() {
  console.log('🚀 Creating main window...');
  
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: getAppIcon(),
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    show: false, // Don't show until ready
    title: APP_CONFIG.name
  });

  // Load the frontend
  const isDev = process.env.NODE_ENV === 'development';
  if (isDev) {
    mainWindow.loadURL(APP_CONFIG.frontendUrl);
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(APP_CONFIG.frontendPath, 'index.html'));
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    console.log('✅ Main window ready');
    mainWindow.show();
    
    // Focus on Windows
    if (process.platform === 'win32') {
      mainWindow.focus();
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Create application menu
  createMenu();

  console.log('✅ Main window created successfully');
}

/**
 * Start the FastAPI backend process
 */
async function startBackend() {
  console.log('🔧 Starting FastAPI backend...');
  
  try {
    // Check if backend is already running
    const isRunning = await checkBackendHealth();
    if (isRunning) {
      console.log('✅ Backend already running');
      isBackendRunning = true;
      return;
    }

    // Start backend process
    const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';
    const backendScript = path.join(APP_CONFIG.backendPath, 'app', 'main_simple.py');
    
    console.log(`🐍 Starting Python backend: ${pythonCommand} ${backendScript}`);
    
    backendProcess = spawn(pythonCommand, [backendScript], {
      cwd: APP_CONFIG.backendPath,
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: process.platform === 'win32'
    });

    // Handle backend process events
    backendProcess.stdout.on('data', (data) => {
      console.log(`[Backend] ${data.toString()}`);
    });

    backendProcess.stderr.on('data', (data) => {
      console.error(`[Backend Error] ${data.toString()}`);
    });

    backendProcess.on('close', (code) => {
      console.log(`[Backend] Process exited with code ${code}`);
      isBackendRunning = false;
      backendProcess = null;
    });

    backendProcess.on('error', (error) => {
      console.error(`[Backend] Failed to start: ${error.message}`);
      isBackendRunning = false;
      backendProcess = null;
    });

    // Wait for backend to start
    await waitForBackend();
    
  } catch (error) {
    console.error('❌ Failed to start backend:', error);
    showErrorDialog('Failed to start backend', error.message);
  }
}

/**
 * Check if backend is running and healthy
 */
async function checkBackendHealth() {
  try {
    const response = await fetch(`${APP_CONFIG.backendUrl}/health`, {
      timeout: 5000
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * Wait for backend to become available
 */
async function waitForBackend(maxAttempts = 30, delay = 1000) {
  console.log('⏳ Waiting for backend to start...');
  
  for (let i = 0; i < maxAttempts; i++) {
    const isHealthy = await checkBackendHealth();
    if (isHealthy) {
      console.log('✅ Backend is healthy and running');
      isBackendRunning = true;
      return;
    }
    
    console.log(`⏳ Attempt ${i + 1}/${maxAttempts} - Backend not ready yet...`);
    await new Promise(resolve => setTimeout(resolve, delay));
  }
  
  throw new Error('Backend failed to start within timeout period');
}

/**
 * Stop the backend process
 */
function stopBackend() {
  if (backendProcess) {
    console.log('🛑 Stopping backend process...');
    backendProcess.kill();
    backendProcess = null;
    isBackendRunning = false;
  }
}

/**
 * Create application menu
 */
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Session',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.send('new-session');
            }
          }
        },
        {
          label: 'Clear Data',
          accelerator: 'CmdOrCtrl+Shift+C',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.send('clear-data');
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectall' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About PrivAI',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About PrivAI',
              message: 'PrivAI Desktop',
              detail: `Version ${APP_CONFIG.version}\n\nPrivacy-first AI application for education.\nAll data processed locally.`
            });
          }
        },
        {
          label: 'Check for Updates',
          click: () => {
            autoUpdater.checkForUpdatesAndNotify();
          }
        },
        {
          label: 'Open Developer Tools',
          click: () => {
            mainWindow.webContents.openDevTools();
          }
        }
      ]
    }
  ];

  // macOS specific menu adjustments
  if (process.platform === 'darwin') {
    template.unshift({
      label: APP_CONFIG.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideothers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

/**
 * Get application icon based on platform
 */
function getAppIcon() {
  const iconName = process.platform === 'win32' ? 'icon.ico' : 
                   process.platform === 'darwin' ? 'icon.icns' : 'icon.png';
  return path.join(__dirname, '../assets', iconName);
}

/**
 * Show error dialog
 */
function showErrorDialog(title, message) {
  if (mainWindow) {
    dialog.showErrorBox(title, message);
  }
}

/**
 * Setup auto-updater
 */
function setupAutoUpdater() {
  console.log('🔄 Setting up auto-updater...');
  
  // Configure auto-updater
  autoUpdater.checkForUpdatesAndNotify();
  
  // Handle update events
  autoUpdater.on('checking-for-update', () => {
    console.log('🔍 Checking for updates...');
  });

  autoUpdater.on('update-available', (info) => {
    console.log('📦 Update available:', info.version);
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Available',
      message: 'A new version is available',
      detail: `Version ${info.version} is available. The update will be downloaded in the background.`
    });
  });

  autoUpdater.on('update-not-available', (info) => {
    console.log('✅ No updates available');
  });

  autoUpdater.on('error', (err) => {
    console.error('❌ Auto-updater error:', err);
  });

  autoUpdater.on('download-progress', (progressObj) => {
    console.log(`📥 Download progress: ${progressObj.percent}%`);
  });

  autoUpdater.on('update-downloaded', (info) => {
    console.log('✅ Update downloaded');
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Ready',
      message: 'Update downloaded successfully',
      detail: 'The application will restart to apply the update.',
      buttons: ['Restart Now', 'Later']
    }).then((result) => {
      if (result.response === 0) {
        autoUpdater.quitAndInstall();
      }
    });
  });
}

/**
 * Setup IPC handlers
 */
function setupIpcHandlers() {
  console.log('🔌 Setting up IPC handlers...');
  
  // Get backend status
  ipcMain.handle('get-backend-status', async () => {
    return {
      running: isBackendRunning,
      url: APP_CONFIG.backendUrl,
      port: APP_CONFIG.backendPort
    };
  });

  // Restart backend
  ipcMain.handle('restart-backend', async () => {
    try {
      stopBackend();
      await startBackend();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  // Get app info
  ipcMain.handle('get-app-info', () => {
    return {
      name: APP_CONFIG.name,
      version: APP_CONFIG.version,
      platform: process.platform,
      arch: process.arch
    };
  });

  // Open external URL
  ipcMain.handle('open-external', (event, url) => {
    shell.openExternal(url);
  });

  // Show message box
  ipcMain.handle('show-message-box', async (event, options) => {
    const result = await dialog.showMessageBox(mainWindow, options);
    return result;
  });

  console.log('✅ IPC handlers setup complete');
}

// Application event handlers
app.whenReady().then(async () => {
  console.log('🚀 PrivAI Desktop starting...');
  
  try {
    // Setup IPC handlers
    setupIpcHandlers();
    
    // Start backend
    await startBackend();
    
    // Create main window
    createMainWindow();
    
    // Setup auto-updater (only in production)
    if (!process.env.NODE_ENV || process.env.NODE_ENV === 'production') {
      setupAutoUpdater();
    }
    
    console.log('✅ PrivAI Desktop started successfully');
    
  } catch (error) {
    console.error('❌ Failed to start PrivAI Desktop:', error);
    app.quit();
  }
});

// Handle window activation (macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createMainWindow();
  }
});

// Handle app quit
app.on('before-quit', () => {
  console.log('🛑 PrivAI Desktop shutting down...');
  stopBackend();
});

// Handle app quit
app.on('will-quit', (event) => {
  console.log('👋 Goodbye from PrivAI Desktop');
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  showErrorDialog('Application Error', error.message);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

console.log('📱 PrivAI Desktop Main Process Loaded');
