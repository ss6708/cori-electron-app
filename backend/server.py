from flask import Flask, jsonify
import win32com.client

app = Flask(__name__)

def open_excel():
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = True
        return {"message": "Excel opened successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/open-excel', methods=['GET'])
def launch_excel():
    result = open_excel()
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
