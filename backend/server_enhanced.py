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

# Import core classes
from backend.ai_services.openai_handler import OpenAIHandler
from backend.models.message import Message
from backend.core.event_system import event_bus, Event as CoreEvent
from backend.core.state_management import AgentStateController, AgentState

# Import RAG++ components
from backend.memory.adapters.server_integration import RAGServerIntegration

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
    """Launch Excel application."""
    result = open_excel()
    return jsonify(result)

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
    app.run(host='127.0.0.1', port=5000, debug=True)
