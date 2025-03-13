from flask import Flask, jsonify
import win32com.client
import win32gui
import win32process
import time

app = Flask(__name__)

def open_excel():
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = True
        # Wait for Excel to fully initialize
        time.sleep(1)
        # Get Excel main window handle
        hwnd = win32gui.FindWindow("XLMAIN", None)
        return {"message": "Excel opened successfully", "hwnd": hwnd}
    except Exception as e:
        return {"error": str(e)}

@app.route('/open-excel', methods=['GET'])
def launch_excel():
    result = open_excel()
    return jsonify(result)

@app.route('/get-excel-hwnd', methods=['GET'])
def get_excel_hwnd():
    try:
        hwnd = win32gui.FindWindow("XLMAIN", None)
        if hwnd:
            return jsonify({"hwnd": hwnd})
        return jsonify({"error": "Excel window not found"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
