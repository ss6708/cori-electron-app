# Excel Screenshot Streaming Feature - Troubleshooting Guide

This guide provides solutions for common issues when setting up and using the Excel/LibreOffice screenshot streaming feature in the Cori application.

## Prerequisites

### Windows
- Microsoft Excel installed
- Python 3.8+ with pip
- Required Python packages (install with `pip install -r backend/requirements.txt`)

### Linux
- LibreOffice Calc installed
- Python 3.8+ with pip
- xdotool for window management
- Python UNO bridge
- Required Python packages

## Setup Instructions

### Windows Setup

1. Install required Python packages:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Ensure Excel is properly installed and can be launched manually.

3. Start the backend server:
   ```bash
   cd backend
   python server_enhanced.py
   ```

4. Start the frontend development server:
   ```bash
   npm run dev
   # or
   pnpm run dev
   ```

### Linux Setup

1. Run the Linux setup script to install dependencies:
   ```bash
   cd backend
   chmod +x setup_linux.sh
   ./setup_linux.sh
   ```

2. Install required Python packages:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```bash
   cd backend
   python server_enhanced.py
   ```

4. Start the frontend development server:
   ```bash
   npm run dev
   # or
   pnpm run dev
   ```

## Common Issues and Solutions

### Backend Server Won't Start

#### Issue: Import Errors
```
ModuleNotFoundError: No module named 'backend'
```

**Solution:**
1. Modify import paths in server_enhanced.py to use relative imports:
   ```python
   # Change from:
   from backend.ai_services.openai_handler import OpenAIHandler
   
   # To:
   from ai_services.openai_handler import OpenAIHandler
   ```

2. Or run the server with the correct Python path:
   ```bash
   cd /path/to/cori-electron-app
   PYTHONPATH=$PYTHONPATH:/path/to/cori-electron-app python backend/server_enhanced.py
   ```

#### Issue: Port Already in Use
```
OSError: [Errno 98] Address already in use
```

**Solution:**
1. Find and kill the process using the port:
   ```bash
   # Find process
   lsof -i :5000
   
   # Kill process
   kill -9 <PID>
   ```

2. Or change the port in server_enhanced.py:
   ```python
   app.run(host='0.0.0.0', port=5001, debug=True)
   ```

### Excel/LibreOffice Won't Launch

#### Windows Issue: COM Error
```
Error: (-2147221008, 'CoInitialize has not been called')
```

**Solution:**
1. Ensure you're running as the same user who installed Excel
2. Try reinstalling pywin32:
   ```bash
   pip uninstall pywin32
   pip install pywin32
   ```

#### Linux Issue: LibreOffice Not Found
```
Error: LibreOffice not found. Please install libreoffice-calc and python3-uno.
```

**Solution:**
1. Install LibreOffice and UNO bridge:
   ```bash
   sudo apt-get install libreoffice-calc python3-uno
   ```

2. Ensure LibreOffice is in your PATH:
   ```bash
   which libreoffice
   ```

### Screenshot Capture Issues

#### Windows Issue: Excel Window Not Found
```
Error: Excel window not found
```

**Solution:**
1. Make sure Excel is running and visible
2. Try clicking on the Excel window to bring it to focus
3. Check if Excel is running with a different window title

#### Linux Issue: xdotool Not Available
```
Error: Command 'xdotool' not found
```

**Solution:**
1. Install xdotool:
   ```bash
   sudo apt-get install xdotool
   ```

2. Make sure X11 is running (not Wayland):
   ```bash
   echo $XDG_SESSION_TYPE
   ```

### Frontend Issues

#### Issue: Screenshot Not Updating
**Solution:**
1. Check browser console for errors
2. Verify backend server is running
3. Check network tab to see if requests to `/excel-screenshot` are succeeding
4. Try increasing the interval in useExcelScreenshot hook:
   ```typescript
   const { screenshotUrl } = useExcelScreenshot({
     enabled: isSpreadsheetRunning,
     interval: 2000  // Increase to 2 seconds
   });
   ```

#### Issue: CORS Errors
```
Access to fetch at 'http://localhost:5000/excel-screenshot' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
1. Ensure CORS is properly configured in the backend:
   ```python
   from flask_cors import CORS
   app = Flask(__name__)
   CORS(app)  # Enable CORS for all routes
   ```

## Advanced Troubleshooting

### Debugging Screenshot Capture

For detailed debugging of screenshot capture, add logging to the capture function:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

def capture_spreadsheet_screenshot():
    logging.debug(f"Capturing screenshot on {platform.system()}")
    # ... existing code ...
    logging.debug(f"Screenshot captured successfully")
```

### Testing Screenshot Endpoint Directly

Test the screenshot endpoint directly using curl:

```bash
curl -v http://localhost:5000/excel-screenshot -o screenshot.png
```

### Checking Event System Integration

To verify event system integration, add temporary logging to event handlers:

```python
@event_bus.on("spreadsheet")
def handle_spreadsheet_event(event):
    print(f"Spreadsheet event received: {event.data}")
```

## Contact Support

If you continue to experience issues after trying these solutions, please:

1. Create an issue on GitHub with:
   - Your operating system details
   - Python version (`python --version`)
   - Excel/LibreOffice version
   - Complete error message
   - Steps to reproduce

2. Or contact the development team directly at support@example.com
