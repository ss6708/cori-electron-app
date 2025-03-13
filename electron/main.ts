import { app, BrowserWindow } from 'electron';
import { exec, spawn, ChildProcess } from 'child_process';
import * as fs from 'fs';
import path from 'path';

let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcess | null = null;

// Get absolute path of the backend server script
const backendPath = path.resolve(__dirname, '../../backend/server.py');

// Function to start Python backend with environment variables from .env
function startBackend(): void {
  try {
    // Read .env file to get environment variables
    const envPath = path.resolve(__dirname, '../../.env');
    let envVars: Record<string, string> = {};
    
    if (fs.existsSync(envPath)) {
      console.log('Found .env file, loading environment variables');
      const envContent = fs.readFileSync(envPath, 'utf8');
      
      // Parse .env file content
      envContent.split('\n').forEach(line => {
        const match = line.match(/^\s*([\w.-]+)\s*=\s*(.*)?\s*$/);
        if (match) {
          const key = match[1];
          let value = match[2] || '';
          
          // Remove quotes if present
          if (value.length > 0 && value.charAt(0) === '"' && value.charAt(value.length - 1) === '"') {
            value = value.replace(/^"|"$/g, '');
          }
          
          envVars[key] = value;
        }
      });
    } else {
      console.warn('.env file not found at', envPath);
    }
    
    // Merge with current environment
    const env = { ...process.env, ...envVars };
    
    // Start Python backend with the merged environment
    backendProcess = spawn('python', [backendPath], { 
      env,
      stdio: 'pipe'
    });
    
    backendProcess.stdout?.on('data', (data: Buffer) => {
      console.log(`Backend stdout: ${data.toString()}`);
    });
    
    backendProcess.stderr?.on('data', (data: Buffer) => {
      console.error(`Backend stderr: ${data.toString()}`);
    });
    
    backendProcess.on('close', (code: number | null) => {
      console.log(`Backend process exited with code ${code}`);
    });
    
    console.log('Backend started with PID:', backendProcess.pid);
  } catch (error) {
    console.error('Error starting backend:', error);
  }
}

// Start backend when app is ready
app.on('ready', () => {
  // Start the backend first
  startBackend();
  
  // Then create the main window
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
    },
    title: "Cori"
  });

  const startUrl = 'http://localhost:3000';
  mainWindow.loadURL(startUrl);

  mainWindow.on('closed', () => {
    mainWindow = null;
    
    // Kill backend on app close
    if (backendProcess) {
      backendProcess.kill();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    app.emit('ready');
  }
});
