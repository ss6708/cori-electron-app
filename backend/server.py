from flask import Flask, jsonify, request, send_file
import os
import platform
import io
from flask_cors import CORS
from dotenv import load_dotenv
from ai_services import OpenAIHandler
from models import Message

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize OpenAI handler
openai_handler = OpenAIHandler()

# Global variables to store spreadsheet application instances
excel_app = None
libreoffice_calc = None

def open_spreadsheet():
    """
    Open Excel on Windows or LibreOffice Calc on Linux.
    Returns a dict with success message or error.
    """
    global excel_app, libreoffice_calc
    
    try:
        system = platform.system()
        
        if system == "Windows":
            # Windows: Use Excel
            import win32com.client
            excel_app = win32com.client.Dispatch("Excel.Application")
            excel_app.Visible = True
            return {"message": "Excel opened successfully"}
            
        elif system == "Linux":
            # Linux: Use LibreOffice Calc
            # Check if LibreOffice is installed
            if os.system("which libreoffice > /dev/null") != 0:
                return {"error": "LibreOffice not found. Please install libreoffice-calc and python3-uno."}
            
            # Start LibreOffice Calc in listening mode (for UNO bridge)
            import subprocess
            import time
            
            # Kill any existing soffice processes
            os.system("pkill soffice || true")
            
            # Start LibreOffice in headless mode with a UNO bridge
            subprocess.Popen([
                "libreoffice", "--calc", "--accept=socket,host=localhost,port=2002;urp;StarOffice.ServiceManager"
            ])
            
            # Wait for LibreOffice to start
            time.sleep(2)
            
            # Connect to LibreOffice via UNO bridge
            import uno
            localContext = uno.getComponentContext()
            resolver = localContext.ServiceManager.createInstanceWithContext(
                "com.sun.star.bridge.UnoUrlResolver", localContext)
            
            # Connect to the running LibreOffice instance
            context = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
            desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
            
            # Create a new Calc document
            libreoffice_calc = desktop.loadComponentFromURL("private:factory/scalc", "_blank", 0, ())
            
            return {"message": "LibreOffice Calc opened successfully"}
        else:
            return {"error": f"Unsupported operating system: {system}"}
            
    except Exception as e:
        return {"error": str(e)}

@app.route('/open-excel', methods=['GET'])
def launch_spreadsheet():
    result = open_spreadsheet()
    return jsonify(result)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests with OpenAI."""
    try:
        # Get request data
        data = request.json
        
        if not data or 'messages' not in data:
            return jsonify({"error": "Invalid request. 'messages' field is required."}), 400
        
        # Convert incoming messages to Message objects
        messages = [Message.from_dict(msg) for msg in data['messages']]
        
        # Get response from OpenAI
        response = openai_handler.get_completion(messages)
        
        # Return the response
        return jsonify(response.to_dict())
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def capture_spreadsheet_screenshot():
    """
    Capture a screenshot of the spreadsheet window (Excel on Windows, LibreOffice Calc on Linux).
    Returns a tuple of (image_bytes, error_message).
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            # Windows: Capture Excel window
            if not excel_app:
                return None, "Excel application not running"
                
            # Windows screenshot code
            import win32gui
            import win32ui
            import win32con
            from PIL import Image
            
            # Find Excel window handle
            hwnd = win32gui.FindWindow(None, excel_app.Caption)
            if not hwnd:
                return None, "Excel window not found"
            
            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # Create device context
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            # Create bitmap
            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(save_bitmap)
            
            # Copy screen to bitmap
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)
            
            # Convert bitmap to image
            bmpinfo = save_bitmap.GetInfo()
            bmpstr = save_bitmap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # Clean up
            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
            
        elif system == "Linux":
            # Linux: Capture LibreOffice Calc window
            if not libreoffice_calc:
                return None, "LibreOffice Calc not running"
                
            # Use pyscreenshot for Linux
            import pyscreenshot
            
            # Get the active window title using xdotool
            import subprocess
            
            try:
                # Get active window ID
                window_id = subprocess.check_output("xdotool getactivewindow", shell=True).decode().strip()
                # Get window name
                window_name = subprocess.check_output(f"xdotool getwindowname {window_id}", shell=True).decode().strip()
                
                # Check if it's a LibreOffice window
                if "LibreOffice" not in window_name and "Calc" not in window_name:
                    return None, "LibreOffice Calc window not in focus"
                    
                # Get window geometry
                geometry = subprocess.check_output(f"xdotool getwindowgeometry {window_id}", shell=True).decode()
                
                # Parse position and size
                import re
                position_match = re.search(r"Position: (\d+),(\d+)", geometry)
                size_match = re.search(r"Geometry: (\d+)x(\d+)", geometry)
                
                if position_match and size_match:
                    x, y = int(position_match.group(1)), int(position_match.group(2))
                    width, height = int(size_match.group(1)), int(size_match.group(2))
                    
                    # Capture the specific window area
                    img = pyscreenshot.grab(bbox=(x, y, x + width, y + height))
                else:
                    # Fallback to full screen if window geometry can't be determined
                    img = pyscreenshot.grab()
            except subprocess.CalledProcessError:
                # Fallback if xdotool is not available
                img = pyscreenshot.grab()
        else:
            return None, f"Unsupported operating system: {system}"
        
        # Save image to bytes (common for both platforms)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr, None
            
    except Exception as e:
        return None, str(e)

@app.route('/excel-screenshot', methods=['GET'])
def get_spreadsheet_screenshot():
    """
    Endpoint to get a screenshot of the spreadsheet window.
    Returns a PNG image or an error message.
    """
    img_bytes, error = capture_spreadsheet_screenshot()
    if error:
        return jsonify({"error": error}), 500
    
    return send_file(img_bytes, mimetype='image/png')

if __name__ == '__main__':
    # Use 0.0.0.0 to allow connections from any IP address
    # This fixes socket permission issues on Windows
    app.run(host='0.0.0.0', port=5000, debug=True)
