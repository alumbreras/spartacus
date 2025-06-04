import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // System information
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  
  // Backend management
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  restartBackend: () => ipcRenderer.invoke('restart-backend'),
  
  // External links
  openExternal: (url: string) => ipcRenderer.invoke('open-external', url),
  
  // Development tools
  toggleDevTools: () => ipcRenderer.invoke('toggle-dev-tools'),
  
  // Platform info
  platform: process.platform,
  
  // App version
  getVersion: () => ipcRenderer.invoke('get-version'),
});

// Type definitions for the exposed API
export interface ElectronAPI {
  getSystemInfo: () => Promise<{
    platform: string;
    arch: string;
    version: string;
    electron: string;
    node: string;
    chrome: string;
  }>;
  getBackendStatus: () => Promise<{
    running: boolean;
    port: number;
  }>;
  restartBackend: () => Promise<boolean>;
  openExternal: (url: string) => Promise<void>;
  toggleDevTools: () => Promise<void>;
  platform: string;
  getVersion: () => Promise<string>;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
} 