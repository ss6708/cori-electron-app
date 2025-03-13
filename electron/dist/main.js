"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const child_process_1 = require("child_process");
const path_1 = __importDefault(require("path"));
const main_1 = require("@electron/remote/main");
const os_1 = __importDefault(require("os"));
// Win32 API constants
const GWL_STYLE = -16;
const WS_POPUP = 0x80000000;
const WS_CHILD = 0x40000000;
const SW_SHOW = 5;
const HWND_TOP = 0;
const SWP_NOMOVE = 0x0002;
const SWP_NOSIZE = 0x0001;
const SWP_SHOWWINDOW = 0x0040;
let mainWindow = null;
let excelWindow = null;
// Get absolute path of the backend server script
const backendPath = path_1.default.resolve(__dirname, '../../backend/server.py');
// Start Python backend
const backendProcess = (0, child_process_1.exec)(`python ${backendPath}`, (error, stdout, stderr) => {
    if (error) {
        console.error(`Error starting backend: ${error.message}`);
    }
    if (stderr) {
        console.error(`Backend stderr: ${stderr}`);
    }
    console.log(`Backend stdout: ${stdout}`);
});
// open main window when 'ready' event fires
electron_1.app.on('ready', () => {
    // Initialize remote module
    (0, main_1.initialize)();
    mainWindow = new electron_1.BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path_1.default.join(__dirname, 'preload.js'),
        },
        title: "Cori"
    });
    // Enable remote module for the window
    (0, main_1.enable)(mainWindow.webContents);
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
electron_1.ipcMain.handle('embed-excel-window', async (event, targetElementId) => {
    try {
        console.log('IPC handler called with targetElementId:', targetElementId);
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
                // Ensure hwnd is a number
                const hwnd = parseInt(String(data.hwnd), 10);
                console.log(`Window handle received: ${hwnd} (Mock: ${data.is_mock === true})`);
                // Create a BrowserWindow for the Excel window
                excelWindow = new electron_1.BrowserWindow({
                    width: 800,
                    height: 600,
                    parent: mainWindow,
                    show: false,
                });
                // Set the Excel window as a child of the main window
                excelWindow.setParentWindow(mainWindow);
                // Check if we're on Windows and not using a mock handle
                if (os_1.default.platform() === 'win32' && !data.is_mock) {
                    try {
                        // Use win32 APIs to set parent window (Windows only)
                        const win32 = require('win32-api');
                        const User32 = win32.User32;
                        const user32 = User32.load();
                        // Set Excel window as child of Electron window
                        // Convert Uint8Array to number using Buffer
                        const nativeHandle = excelWindow.getNativeWindowHandle();
                        const handleBuffer = Buffer.from(nativeHandle);
                        const handleValue = handleBuffer.readInt32LE(0);
                        console.log('Native handle converted:', handleValue);
                        // Get current window style
                        const currentStyle = user32.GetWindowLongPtrA(hwnd, GWL_STYLE);
                        console.log('Current window style:', currentStyle);
                        // Modify window style (remove WS_POPUP, add WS_CHILD)
                        const newStyle = (currentStyle & ~WS_POPUP) | WS_CHILD;
                        console.log('New window style:', newStyle);
                        // Set new window style
                        const styleResult = user32.SetWindowLongPtrA(hwnd, GWL_STYLE, newStyle);
                        console.log('SetWindowLongPtr result:', styleResult);
                        const result = user32.SetParent(hwnd, handleValue);
                        console.log('SetParent result:', result);
                        // Show window
                        const showResult = user32.ShowWindow(hwnd, SW_SHOW);
                        console.log('ShowWindow result:', showResult);
                        // Set window position and z-order
                        const posResult = user32.SetWindowPos(hwnd, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW);
                        console.log('SetWindowPos result:', posResult);
                        return { success: true, message: "Excel window embedded successfully" };
                    }
                    catch (attachError) {
                        console.error('Error attaching Excel window:', attachError);
                        return { success: false, message: `Error attaching Excel window: ${attachError instanceof Error ? attachError.message : String(attachError)}` };
                    }
                }
                else {
                    // For non-Windows or mock handles, just show a message
                    console.log('Using mock Excel window or non-Windows platform');
                    return {
                        success: true,
                        message: "Mock Excel window created (Excel embedding only fully supported on Windows)",
                        is_mock: true
                    };
                }
            }
            else {
                return { success: false, message: "Failed to get Excel window handle" };
            }
        }
        catch (innerError) {
            console.error('Error communicating with Python backend:', innerError);
            return { success: false, message: "Error communicating with Python backend: " + (innerError instanceof Error ? innerError.message : String(innerError)) };
        }
    }
    catch (error) {
        console.error('Error embedding Excel window:', error);
        return { success: false, message: "Error embedding Excel window: " + (error instanceof Error ? error.message : String(error)) };
    }
});
electron_1.app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        electron_1.app.quit();
    }
});
electron_1.app.on('activate', () => {
    if (mainWindow === null) {
        electron_1.app.emit('ready');
    }
});
