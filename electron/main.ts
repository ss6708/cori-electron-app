import { app, BrowserWindow } from 'electron';
import { exec } from 'child_process';

import path from 'path';


let mainWindow: BrowserWindow | null = null;

// Get absolute path of the backend server script
const backendPath = path.resolve(__dirname, '../../backend/server.py');

// Start Python backend
const backendProcess = exec(`python ${backendPath}`, (error, stdout, stderr) => {
  if (error) {
    console.error(`Error starting backend: ${error.message}`);
  }
  if (stderr) {
    console.error(`Backend stderr: ${stderr}`);
  }
  console.log(`Backend stdout: ${stdout}`);
});

// open main window when 'ready' event fires
app.on('ready', () => {
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
    backendProcess.kill(); // Kill backend on app close
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