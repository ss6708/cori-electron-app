"""
Configuration for pytest.
Sets up the Python path to allow imports from the backend directory.
"""

import os
import sys

# Add the parent directory to sys.path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
