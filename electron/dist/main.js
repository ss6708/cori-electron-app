"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const child_process_1 = require("child_process");
const path_1 = __importDefault(require("path"));
let mainWindow = null;
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
    mainWindow = new electron_1.BrowserWindow({
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
