"""
Enhanced server implementation for Cori backend.
Integrates RAG++ memory system with core infrastructure.
"""

from flask import Flask, jsonify, request
import os
import platform
import threading
import logging
from datetime import datetime
from flask_cors import CORS
from dotenv import load_dotenv
import uuid
from pathlib import Path

# Import core classes
from ai_services.openai_handler import OpenAIHandler
from models.message import Message
from core.event_system import event_bus, Event as CoreEvent
from core.state_management import AgentStateController, AgentState

# Import RAG++ components
from memory.adapters.server_integration import RAGServerIntegration

# Import additional libraries for cross-platform screenshot capture
import io
from flask import send_file
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize core components
openai_handler = OpenAIHandler()
state_controller = AgentStateController()

# Initialize RAG++ integration
rag_integration = RAGServerIntegration(
    state_controller=state_controller,
    storage_dir=os.environ.get("MEMORY_STORAGE_DIR", "memory"),
    rag_enabled=os.environ.get("RAG_ENABLED", "true").lower() == "true"
)

# Initialize RAG++ components
rag_integration.initialize()

# Get RAG-enhanced OpenAI handler
rag_handler = rag_integration.get_rag_handler()

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
            import pythoncom
            
            # Initialize COM for the current thread
            pythoncom.CoInitialize()
            
            # Create Excel application instance
            excel_app = win32com.client.Dispatch("Excel.Application")
            excel_app.Visible = True
            
            # Open an existing workbook if path is specified, otherwise create a new one
            try:
                dir_path = Path("C:\\Users\\shrey\\OneDrive\\Desktop\\Excel\\inputs")
                ws_path = "Sample model.xlsm"
                workbook = excel_app.Workbooks.Open(os.path.join(dir_path, ws_path))
            except Exception as e:
                # Fallback to creating a new workbook if opening fails
                logger.warning(f"Failed to open specified workbook: {e}. Creating a new workbook instead.")
                workbook = excel_app.Workbooks.Add()
            
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
            
            try:
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
            except ImportError:
                return {"error": "python3-uno module not installed. Please install python3-uno."}
        else:
            return {"error": f"Unsupported operating system: {system}"}
            
    except Exception as e:
        return {"error": f"Error opening spreadsheet: {str(e)}"}

@app.route('/open-excel', methods=['GET'])
def launch_spreadsheet():
    """Launch Excel or LibreOffice Calc based on platform."""
    result = open_spreadsheet()
    
    # Create an event for the spreadsheet launch
    event_data = {
        "type": "spreadsheet_launched",
        "platform": platform.system(),
        "success": "error" not in result,
        "message": result.get("message", result.get("error", ""))
    }
    event_bus.emit(CoreEvent("spreadsheet", event_data))
    
    return jsonify(result)

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
        # Emit error event
        event_data = {
            "type": "spreadsheet_screenshot_error",
            "error": error
        }
        event_bus.emit(CoreEvent("spreadsheet", event_data))
        return jsonify({"error": error}), 500
    
    # Emit success event
    event_data = {
        "type": "spreadsheet_screenshot_captured",
        "timestamp": datetime.now().isoformat()
    }
    event_bus.emit(CoreEvent("spreadsheet", event_data))
    
    return send_file(img_bytes, mimetype='image/png')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat requests with RAG-enhanced OpenAI.
    Falls back to core OpenAI handler if RAG is disabled.
    """
    try:
        # Get request data
        data = request.json
        
        if not data or 'messages' not in data:
            return jsonify({"error": "Invalid request. 'messages' field is required."}), 400
        
        # Get session ID
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Convert incoming messages to Message objects
        messages = [Message.from_dict(msg) for msg in data['messages']]
        
        # Get last user message
        last_user_message = next(
            (msg for msg in reversed(messages) if msg.role == "user"),
            None
        )
        
        if not last_user_message:
            return jsonify({"error": "No user message found"}), 400
        
        # Publish user message event
        event_bus.publish(CoreEvent(
            event_type="user_message",
            data={
                "session_id": session_id,
                "message": last_user_message.content
            }
        ))
        
        # Transition to ANALYZING state
        state_controller.transition_to(
            AgentState.ANALYZING,
            reason="Analyzing user query",
            metadata={
                "session_id": session_id,
                "query": last_user_message.content
            }
        )
        
        # Check if RAG is enabled
        use_rag = rag_integration.is_rag_enabled()
        
        # Get response from appropriate handler
        if use_rag:
            # Transition to PLANNING state
            state_controller.transition_to(
                AgentState.PLANNING,
                reason="Planning response with domain knowledge",
                metadata={
                    "session_id": session_id,
                    "query": last_user_message.content
                }
            )
            
            # Transition to EXECUTING state
            state_controller.transition_to(
                AgentState.EXECUTING,
                reason="Generating response with RAG context",
                metadata={
                    "session_id": session_id
                }
            )
            
            # Get response from RAG-enhanced handler
            response = rag_handler.get_completion(
                messages=messages,
                session_id=session_id
            )
        else:
            # Get response from core handler
            response = openai_handler.get_completion(messages)
        
        # Transition to REVIEWING state
        state_controller.transition_to(
            AgentState.REVIEWING,
            reason="Response generated, ready for review",
            metadata={
                "session_id": session_id,
                "response_length": len(response.content)
            }
        )
        
        # Transition to IDLE state
        state_controller.transition_to(
            AgentState.IDLE,
            reason="Chat interaction completed",
            metadata={
                "session_id": session_id
            }
        )
        
        # Return the response
        return jsonify(response.to_dict())
    
    except Exception as e:
        # Handle errors gracefully
        error_message = f"Error in chat endpoint: {str(e)}"
        logger.error(error_message)
        
        # Transition to ERROR state
        state_controller.transition_to(
            AgentState.ERROR,
            reason=error_message,
            metadata={"error": str(e)}
        )
        
        return jsonify({"error": str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    """
    Handle user feedback for learning.
    """
    try:
        # Get request data
        data = request.json
        
        if not data or 'session_id' not in data or 'feedback' not in data:
            return jsonify({"error": "Invalid request. 'session_id' and 'feedback' fields are required."}), 400
        
        # Get feedback data
        session_id = data.get('session_id')
        feedback_text = data.get('feedback')
        rating = data.get('rating')
        
        # Process feedback
        success = rag_integration.process_feedback(
            session_id=session_id,
            feedback=feedback_text,
            rating=rating
        )
        
        if success:
            return jsonify({"message": "Feedback processed successfully"})
        else:
            return jsonify({"error": "Error processing feedback"}), 500
    
    except Exception as e:
        # Handle errors gracefully
        error_message = f"Error in feedback endpoint: {str(e)}"
        logger.error(error_message)
        
        return jsonify({"error": str(e)}), 500

@app.route('/sessions', methods=['GET'])
def list_sessions():
    """
    List all available sessions.
    """
    try:
        # Get session adapter
        session_adapter = rag_integration.get_session_adapter()
        
        # List sessions
        sessions = session_adapter.list_sessions()
        
        return jsonify(sessions)
    
    except Exception as e:
        # Handle errors gracefully
        error_message = f"Error listing sessions: {str(e)}"
        logger.error(error_message)
        
        return jsonify({"error": str(e)}), 500

@app.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """
    Get a session by ID.
    """
    try:
        # Get session adapter
        session_adapter = rag_integration.get_session_adapter()
        
        # Load session
        session_data = session_adapter.load_session(session_id)
        
        if not session_data:
            return jsonify({"error": f"Session not found: {session_id}"}), 404
        
        return jsonify(session_data)
    
    except Exception as e:
        # Handle errors gracefully
        error_message = f"Error getting session: {str(e)}"
        logger.error(error_message)
        
        return jsonify({"error": str(e)}), 500

@app.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    Delete a session by ID.
    """
    try:
        # Get session adapter
        session_adapter = rag_integration.get_session_adapter()
        
        # Delete session
        success = session_adapter.delete_session(session_id)
        
        if success:
            return jsonify({"message": f"Session deleted: {session_id}"})
        else:
            return jsonify({"error": f"Error deleting session: {session_id}"}), 500
    
    except Exception as e:
        # Handle errors gracefully
        error_message = f"Error deleting session: {str(e)}"
        logger.error(error_message)
        
        return jsonify({"error": str(e)}), 500

@app.route('/sessions', methods=['POST'])
def create_session():
    """
    Create a new session.
    """
    try:
        # Get request data
        data = request.json or {}
        
        # Get session ID
        session_id = data.get('session_id')
        
        # Get session adapter
        session_adapter = rag_integration.get_session_adapter()
        
        # Create session
        session_id = session_adapter.create_session(session_id)
        
        # Publish session created event
        event_bus.publish(CoreEvent(
            event_type="session_created",
            data={"session_id": session_id}
        ))
        
        return jsonify({"session_id": session_id})
    
    except Exception as e:
        # Handle errors gracefully
        error_message = f"Error creating session: {str(e)}"
        logger.error(error_message)
        
        return jsonify({"error": str(e)}), 500

@app.route('/rag/status', methods=['GET'])
def rag_status():
    """
    Get RAG status.
    """
    try:
        # Get RAG status
        status = {
            "rag_enabled": rag_integration.is_rag_enabled(),
            "components_initialized": rag_integration._initialized
        }
        
        return jsonify(status)
    
    except Exception as e:
        # Handle errors gracefully
        error_message = f"Error getting RAG status: {str(e)}"
        logger.error(error_message)
        
        return jsonify({"error": str(e)}), 500

@app.route('/rag/enable', methods=['POST'])
def enable_rag():
    """
    Enable RAG.
    """
    try:
        # Enable RAG
        rag_integration.set_rag_enabled(True)
        
        return jsonify({"message": "RAG enabled"})
    
    except Exception as e:
        # Handle errors gracefully
        error_message = f"Error enabling RAG: {str(e)}"
        logger.error(error_message)
        
        return jsonify({"error": str(e)}), 500

@app.route('/rag/disable', methods=['POST'])
def disable_rag():
    """
    Disable RAG.
    """
    try:
        # Disable RAG
        rag_integration.set_rag_enabled(False)
        
        return jsonify({"message": "RAG disabled"})
    
    except Exception as e:
        # Handle errors gracefully
        error_message = f"Error disabling RAG: {str(e)}"
        logger.error(error_message)
        
        return jsonify({"error": str(e)}), 500

@app.route('/rag/condense/<session_id>', methods=['POST'])
def condense_memory(session_id):
    """
    Condense memory for a session.
    """
    try:
        # Condense memory
        success = rag_integration.condense_memory(session_id)
        
        if success:
            return jsonify({"message": f"Memory condensed for session: {session_id}"})
        else:
            return jsonify({"error": f"Error condensing memory for session: {session_id}"}), 500
    
    except Exception as e:
        # Handle errors gracefully
        error_message = f"Error condensing memory: {str(e)}"
        logger.error(error_message)
        
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use 0.0.0.0 to allow connections from any IP address
    # This fixes socket permission issues on Windows
    app.run(host='0.0.0.0', port=5000, debug=True)
