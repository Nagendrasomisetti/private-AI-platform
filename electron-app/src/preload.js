/**
 * PrivAI Desktop Application - Preload Script
 * 
 * This script runs in the renderer process with access to Node.js APIs
 * but in a secure context. It provides a bridge between the main process
 * and the renderer process for secure communication.
 */

const { contextBridge, ipcRenderer } = require('electron');

/**
 * Expose protected methods that allow the renderer process to use
 * the ipcRenderer without exposing the entire object
 */
contextBridge.exposeInMainWorld('electronAPI', {
  /**
   * Backend management
   */
  backend: {
    /**
     * Get backend status
     * @returns {Promise<{running: boolean, url: string, port: number}>}
     */
    getStatus: () => ipcRenderer.invoke('get-backend-status'),
    
    /**
     * Restart backend process
     * @returns {Promise<{success: boolean, error?: string}>}
     */
    restart: () => ipcRenderer.invoke('restart-backend')
  },

  /**
   * Application information
   */
  app: {
    /**
     * Get application information
     * @returns {Promise<{name: string, version: string, platform: string, arch: string}>}
     */
    getInfo: () => ipcRenderer.invoke('get-app-info')
  },

  /**
   * System utilities
   */
  system: {
    /**
     * Open external URL
     * @param {string} url - URL to open
     */
    openExternal: (url) => ipcRenderer.invoke('open-external', url),
    
    /**
     * Show message box
     * @param {Object} options - Message box options
     * @returns {Promise<{response: number, checkboxChecked: boolean}>}
     */
    showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options)
  },

  /**
   * Event listeners for main process events
   */
  events: {
    /**
     * Listen for new session event
     * @param {Function} callback - Callback function
     */
    onNewSession: (callback) => {
      ipcRenderer.on('new-session', callback);
    },
    
    /**
     * Listen for clear data event
     * @param {Function} callback - Callback function
     */
    onClearData: (callback) => {
      ipcRenderer.on('clear-data', callback);
    },
    
    /**
     * Remove all listeners
     */
    removeAllListeners: () => {
      ipcRenderer.removeAllListeners('new-session');
      ipcRenderer.removeAllListeners('clear-data');
    }
  },

  /**
   * Platform detection
   */
  platform: {
    isWindows: process.platform === 'win32',
    isMac: process.platform === 'darwin',
    isLinux: process.platform === 'linux',
    platform: process.platform,
    arch: process.arch
  },

  /**
   * Development utilities
   */
  dev: {
    /**
     * Check if running in development mode
     * @returns {boolean}
     */
    isDev: process.env.NODE_ENV === 'development',
    
    /**
     * Get environment variables
     * @returns {Object}
     */
    getEnv: () => ({
      NODE_ENV: process.env.NODE_ENV,
      ELECTRON_IS_DEV: process.env.ELECTRON_IS_DEV
    })
  }
});

/**
 * Security: Prevent the renderer from accessing Node.js APIs directly
 */
delete window.require;
delete window.exports;
delete window.module;

console.log('🔒 PrivAI Desktop Preload Script Loaded');
