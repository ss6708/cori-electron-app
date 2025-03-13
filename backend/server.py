from flask import Flask, jsonify, send_file
import win32com.client
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import io
import os
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# Global variable to store Excel application instance
excel_app = None

def open_excel():
    global excel_app
    try:
        excel_app = win32com.client.Dispatch("Excel.Application")
        excel_app.Visible = True
        return {"message": "Excel opened successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/open-excel', methods=['GET'])
def launch_excel():
    result = open_excel()
    return jsonify(result)

def capture_excel_screenshot():
    try:
        if not excel_app:
            return None, "Excel application not running"
        
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
    img_bytes, error = capture_excel_screenshot()
    if error:
        return jsonify({"error": error}), 500
    
    return send_file(img_bytes, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
