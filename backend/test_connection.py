"""
Test script to verify the backend connection.
"""
import requests
import json
import sys

def test_backend_connection():
    """
    Test connectivity to the Flask backend server.
    Sends a test message to the backend and verifies the response.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        response = requests.post(
            'http://localhost:5000/chat',
            json={'messages': [{'role': 'user', 'content': 'test', 'timestamp': '2023-01-01T00:00:00.000Z', 'displayed': True}]}
        )
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        return False

if __name__ == "__main__":
    print("Testing connection to backend server...")
    print("Sending test message to http://localhost:5000/chat")
    success = test_backend_connection()
    
    if success:
        print("✅ Connection test successful!")
        sys.exit(0)
    else:
        print("❌ Connection test failed!")
        sys.exit(1)
