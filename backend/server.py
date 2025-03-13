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

# Global variable to store Excel application instance
excel_app = None

def open_excel():
    """
    Open Excel application on Windows.
    """
    global excel_app
    try:
        # Import win32com for Windows
        import win32com.client
        excel_app = win32com.client.Dispatch("Excel.Application")
        excel_app.Visible = True
        return {"message": "Excel opened successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/open-excel', methods=['GET'])
def launch_excel():
    result = open_excel()
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

def capture_excel_screenshot():
    """
    Capture a screenshot of the Excel window on Windows.
    Returns a tuple of (image_bytes, error_message).
    """
    try:
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
        
        # Save image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Clean up
        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)
        
        return img_byte_arr, None
    except Exception as e:
        return None, str(e)

@app.route('/excel-screenshot', methods=['GET'])
def get_excel_screenshot():
    """
    Endpoint to get a screenshot of the Excel window.
    Returns a PNG image or an error message.
    """
    img_bytes, error = capture_excel_screenshot()
    if error:
        return jsonify({"error": error}), 500
    
    return send_file(img_bytes, mimetype='image/png')

if __name__ == '__main__':
    # Use 0.0.0.0 to allow connections from any IP address
    # This fixes socket permission issues on Windows
    app.run(host='0.0.0.0', port=5000, debug=True)
