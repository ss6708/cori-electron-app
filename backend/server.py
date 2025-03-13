from flask import Flask, jsonify
from flask_cors import CORS
import win32com.client
import win32gui
import win32process
import pythoncom
import time
import sys
import platform

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def open_excel():
    # Check if running on Windows
    if platform.system() != 'Windows':
        print("Not running on Windows, using mock Excel window handle")
        # Return a mock window handle for non-Windows environments
        mock_hwnd = 12345  # Mock window handle
        return {"message": "Mock Excel opened successfully (non-Windows environment)", "hwnd": mock_hwnd, "is_mock": True}
    
    # Windows-specific implementation
    try:
        print("Attempting to open Excel on Windows...")
        # Initialize COM
        pythoncom.CoInitialize()
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = True
        # Wait for Excel to fully initialize
        time.sleep(1)
        # Get Excel main window handle
        hwnd = win32gui.FindWindow("XLMAIN", None)
        if hwnd:
            print(f"Excel opened successfully with window handle: {hwnd}")
            return {"message": "Excel opened successfully", "hwnd": hwnd, "is_mock": False}
        else:
            print("Failed to get Excel window handle")
            return {"error": "Failed to get Excel window handle"}
    except Exception as e:
        print(f"Error opening Excel: {str(e)}")
        return {"error": f"Error opening Excel: {str(e)}"}

@app.route('/open-excel', methods=['GET'])
def launch_excel():
    result = open_excel()
    return jsonify(result)

@app.route('/get-excel-hwnd', methods=['GET'])
def get_excel_hwnd():
    # Check if running on Windows
    if platform.system() != 'Windows':
        print("Not running on Windows, using mock Excel window handle")
        mock_hwnd = 12345  # Mock window handle
        return jsonify({"hwnd": mock_hwnd, "is_mock": True})
        
    try:
        # Initialize COM
        pythoncom.CoInitialize()
        hwnd = win32gui.FindWindow("XLMAIN", None)
        if hwnd:
            return jsonify({"hwnd": hwnd, "is_mock": False})
        return jsonify({"error": "Excel window not found"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
