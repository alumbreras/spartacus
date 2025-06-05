import { app, BrowserWindow, ipcMain, shell, Menu } from 'electron';
import path from 'path';
import { spawn, ChildProcess } from 'child_process';

// Global references
let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcess | null = null;

// Environment configuration
const isDevelopment = process.env.NODE_ENV === 'development' || process.env.NODE_ENV !== 'production';
const BACKEND_PORT = 8000;
const FRONTEND_PORT = 3000;

class SpartacusApp {
  constructor() {
    this.setupAppEvents();
    this.setupIpcHandlers();
  }

  private setupAppEvents(): void {
    // App ready event
    app.whenReady().then(() => {
      this.createMainWindow();
      this.startBackend();
      this.setupMenu();
      
      app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
          this.createMainWindow();
        }
      });
    });

    // Quit when all windows are closed
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        this.cleanup();
        app.quit();
      }
    });

    // Before quit event
    app.on('before-quit', () => {
      this.cleanup();
    });

    // Security: Prevent navigation to external URLs
    app.on('web-contents-created', (event, contents) => {
      contents.on('will-navigate', (navigationEvent, navigationUrl) => {
        const parsedUrl = new URL(navigationUrl);
        
        if (parsedUrl.origin !== `http://localhost:${FRONTEND_PORT}`) {
          navigationEvent.preventDefault();
        }
      });
    });
  }

  private createMainWindow(): void {
    // Create the browser window
    mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 800,
      minHeight: 600,
      titleBarStyle: 'hiddenInset',
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, '../preload/preload.js'),
      },
      icon: path.join(__dirname, '../../assets/icon.png'),
      show: false,
    });

    // Load the React app
    const startUrl = `http://localhost:${FRONTEND_PORT}`;
    
    console.log(`🌐 Loading URL: ${startUrl}`);
    console.log(`🔧 isDevelopment: ${isDevelopment}`);
    console.log(`🔧 NODE_ENV: ${process.env.NODE_ENV}`);
    
    mainWindow.loadURL(startUrl);

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
      mainWindow?.show();
      
      // Open DevTools in development
      if (isDevelopment) {
        mainWindow?.webContents.openDevTools();
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
  }

  private startBackend(): void {
    const backendPath = path.join(__dirname, '../../../spartacus_backend/start_backend.py');
    const rootPath = path.join(__dirname, '../../../');
    
    console.log('🚀 Starting Spartacus Backend...');
    
    // Start Python backend
    backendProcess = spawn('python', [backendPath, '--host', '127.0.0.1', '--port', BACKEND_PORT.toString()], {
      cwd: rootPath,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, PYTHONPATH: rootPath }
    });

    backendProcess.stdout?.on('data', (data) => {
      console.log(`Backend: ${data}`);
    });

    backendProcess.stderr?.on('data', (data) => {
      console.error(`Backend Error: ${data}`);
    });

    backendProcess.on('close', (code) => {
      console.log(`Backend process exited with code ${code}`);
    });
  }

  private setupMenu(): void {
    const template = [
      {
        label: 'Spartacus',
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
      }
    ];

    const menu = Menu.buildFromTemplate(template as any);
    Menu.setApplicationMenu(menu);
  }

  private setupIpcHandlers(): void {
    // System info
    ipcMain.handle('get-system-info', async () => {
      return {
        platform: process.platform,
        arch: process.arch,
        version: app.getVersion(),
        electron: process.versions.electron,
        node: process.versions.node,
        chrome: process.versions.chrome
      };
    });

    // Backend status
    ipcMain.handle('get-backend-status', async () => {
      return {
        running: backendProcess !== null && !backendProcess.killed,
        port: BACKEND_PORT
      };
    });

    // Restart backend
    ipcMain.handle('restart-backend', async () => {
      this.cleanup();
      this.startBackend();
      return true;
    });

    // Open external link
    ipcMain.handle('open-external', async (event, url: string) => {
      await shell.openExternal(url);
    });

    // Toggle DevTools
    ipcMain.handle('toggle-dev-tools', async () => {
      if (mainWindow) {
        mainWindow.webContents.toggleDevTools();
      }
    });
  }

  private cleanup(): void {
    console.log('🛑 Cleaning up...');
    
    if (backendProcess && !backendProcess.killed) {
      console.log('Stopping backend process...');
      backendProcess.kill('SIGTERM');
      
      // Force kill after 5 seconds
      setTimeout(() => {
        if (backendProcess && !backendProcess.killed) {
          backendProcess.kill('SIGKILL');
        }
      }, 5000);
    }
  }
}

// Create app instance
new SpartacusApp(); 