from flask import Flask, jsonify, request
import os
import platform
from flask_cors import CORS
from ai_services import OpenAIHandler
from models import Message

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize OpenAI handler
openai_handler = OpenAIHandler()

def open_excel():
    """
    Open Excel application if on Windows, otherwise return a mock response.
    This is a placeholder function that will be properly implemented on Windows.
    """
    try:
        if platform.system() == "Windows":
            # Import win32com only on Windows
            import win32com.client
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = True
            return {"message": "Excel opened successfully"}
        else:
            # Mock response for non-Windows platforms
            return {"message": "Excel would be opened (mock response - not on Windows)"}
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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
