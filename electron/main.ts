import { app, BrowserWindow, ipcMain } from 'electron';
import { exec } from 'child_process';
import path from 'path';
import { initialize } from '@electron/remote/main';

let mainWindow: BrowserWindow | null = null;
let excelWindow: BrowserWindow | null = null;

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
  // Initialize remote module
  initialize();
  
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    title: "Cori"
  });

  const startUrl = 'http://localhost:3000';
  mainWindow.loadURL(startUrl);

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (excelWindow) {
      excelWindow.close();
      excelWindow = null;
    }
    backendProcess.kill(); // Kill backend on app close
  });
});

// IPC handler for embedding Excel window
ipcMain.handle('embed-excel-window', async (event, targetElementId) => {
  try {
    // Wait for backend to be ready
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Call backend API to open Excel and get window handle
    try {
      console.log('Calling Python backend to open Excel...');
      const fetch = require('node-fetch');
      const response = await fetch('http://localhost:5000/open-excel');
      const data = await response.json();
      console.log('Response from Python backend:', data);
      
      if (data.error) {
        console.error('Error from Python backend:', data.error);
        return { success: false, message: data.error };
      }
      
      if (data.hwnd) {
        const hwnd = data.hwnd;
        
        // Create a BrowserWindow for the Excel window
        excelWindow = new BrowserWindow({
          width: 800,
          height: 600,
          parent: mainWindow!,
          show: false,
        });
        
        // Set the Excel window as a child of the main window
        excelWindow.setParentWindow(mainWindow!);
        
        // Attach the Excel window to the main window
        const { NativeWindow } = require('@electron/remote');
        const nativeWin = new NativeWindow({ handle: hwnd });
        nativeWin.setParent(excelWindow);
        
        return { success: true, message: "Excel window embedded successfully" };
      } else {
        return { success: false, message: "Failed to get Excel window handle" };
      }
    } catch (innerError) {
      console.error('Error communicating with Python backend:', innerError);
      return { success: false, message: "Error communicating with Python backend: " + (innerError instanceof Error ? innerError.message : String(innerError)) };
    }
  } catch (error) {
    console.error('Error embedding Excel window:', error);
    return { success: false, message: "Error embedding Excel window: " + (error instanceof Error ? error.message : String(error)) };
  }
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
