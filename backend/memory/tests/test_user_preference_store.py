"""
Tests for the user preference store.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory.user_preference_store import UserPreferenceStore
from memory.models.preference import Preference
from memory.long_term_memory import LongTermMemory

class TestUserPreferenceStore(unittest.TestCase):
    """Test cases for the UserPreferenceStore class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for the preference store
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the long-term memory
        self.mock_ltm = MagicMock(spec=LongTermMemory)
        
        # Initialize the preference store
        self.preference_store = UserPreferenceStore(
            long_term_memory=self.mock_ltm,
            preference_dir=self.temp_dir
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test initialization of the preference store."""
        # Check that the preference directory was created
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_add_preference(self):
        """Test adding a preference to the store."""
        # Create a preference
        preference = Preference(
            id="test_id",
            user_id="test_user",
            domain="lbo",
            key="debt_to_ebitda",
            value="5.5x",
            description="Preferred debt-to-EBITDA ratio for LBOs",
            timestamp="2023-01-01T00:00:00Z"
        )
        
        # Add the preference
        doc_id = self.preference_store.add_preference(preference)
        
        # Check that the document was added to long-term memory
        self.mock_ltm.add_document.assert_called_once()
        call_args = self.mock_ltm.add_document.call_args[1]
        self.assertEqual(call_args["collection_name"], "preferences")
        self.assertEqual(call_args["text"], "Preferred debt-to-EBITDA ratio for LBOs: 5.5x")
        self.assertEqual(call_args["metadata"]["user_id"], "test_user")
        self.assertEqual(call_args["metadata"]["domain"], "lbo")
        self.assertEqual(call_args["metadata"]["key"], "debt_to_ebitda")
        self.assertEqual(call_args["metadata"]["value"], "5.5x")
        self.assertEqual(call_args["metadata"]["type"], "preference")
        
        # Check that the document ID was returned
        self.assertEqual(doc_id, "test_id")
        
        # Check that the preference file was created
        preference_file = os.path.join(self.temp_dir, "test_user", "lbo", "debt_to_ebitda.json")
        self.assertTrue(os.path.exists(preference_file))
        
        # Check the content of the preference file
        with open(preference_file, "r") as f:
            pref_data = json.load(f)
            self.assertEqual(pref_data["id"], "test_id")
            self.assertEqual(pref_data["user_id"], "test_user")
            self.assertEqual(pref_data["domain"], "lbo")
            self.assertEqual(pref_data["key"], "debt_to_ebitda")
            self.assertEqual(pref_data["value"], "5.5x")
            self.assertEqual(pref_data["description"], "Preferred debt-to-EBITDA ratio for LBOs")
            self.assertEqual(pref_data["timestamp"], "2023-01-01T00:00:00Z")
    
    def test_get_preference(self):
        """Test getting a preference from the store."""
        # Create a preference
        preference = Preference(
            id="test_id",
            user_id="test_user",
            domain="lbo",
            key="debt_to_ebitda",
            value="5.5x",
            description="Preferred debt-to-EBITDA ratio for LBOs",
            timestamp="2023-01-01T00:00:00Z"
        )
        
        # Add the preference
        self.preference_store.add_preference(preference)
        
        # Set up mock response
        self.mock_ltm.get_document.return_value = {
            "id": "test_id",
            "text": "Preferred debt-to-EBITDA ratio for LBOs: 5.5x",
            "metadata": {
                "user_id": "test_user",
                "domain": "lbo",
                "key": "debt_to_ebitda",
                "value": "5.5x",
                "description": "Preferred debt-to-EBITDA ratio for LBOs",
                "timestamp": "2023-01-01T00:00:00Z",
                "type": "preference"
            }
        }
        
        # Get the preference
        retrieved_preference = self.preference_store.get_preference("test_id")
        
        # Check that the document was retrieved from long-term memory
        self.mock_ltm.get_document.assert_called_once_with(
            doc_id="test_id",
            collection_name="preferences"
        )
        
        # Check that the preference was returned
        self.assertEqual(retrieved_preference.id, "test_id")
        self.assertEqual(retrieved_preference.user_id, "test_user")
        self.assertEqual(retrieved_preference.domain, "lbo")
        self.assertEqual(retrieved_preference.key, "debt_to_ebitda")
        self.assertEqual(retrieved_preference.value, "5.5x")
        self.assertEqual(retrieved_preference.description, "Preferred debt-to-EBITDA ratio for LBOs")
        self.assertEqual(retrieved_preference.timestamp, "2023-01-01T00:00:00Z")
    
    def test_get_user_preferences(self):
        """Test getting all preferences for a user."""
        # Set up mock response
        self.mock_ltm.search_by_metadata.return_value = [
            {
                "id": "test_id1",
                "text": "Preferred debt-to-EBITDA ratio for LBOs: 5.5x",
                "metadata": {
                    "user_id": "test_user",
                    "domain": "lbo",
                    "key": "debt_to_ebitda",
                    "value": "5.5x",
                    "description": "Preferred debt-to-EBITDA ratio for LBOs",
                    "timestamp": "2023-01-01T00:00:00Z",
                    "type": "preference"
                }
            },
            {
                "id": "test_id2",
                "text": "Preferred exit multiple for LBOs: 12x",
                "metadata": {
                    "user_id": "test_user",
                    "domain": "lbo",
                    "key": "exit_multiple",
                    "value": "12x",
                    "description": "Preferred exit multiple for LBOs",
                    "timestamp": "2023-01-01T00:00:01Z",
                    "type": "preference"
                }
            }
        ]
        
        # Get user preferences
        preferences = self.preference_store.get_user_preferences("test_user")
        
        # Check that the search was performed
        self.mock_ltm.search_by_metadata.assert_called_once_with(
            collection_name="preferences",
            filters={"user_id": "test_user", "type": "preference"}
        )
        
        # Check that the preferences were returned
        self.assertEqual(len(preferences), 2)
        self.assertEqual(preferences[0].id, "test_id1")
        self.assertEqual(preferences[0].key, "debt_to_ebitda")
        self.assertEqual(preferences[1].id, "test_id2")
        self.assertEqual(preferences[1].key, "exit_multiple")
    
    def test_get_domain_preferences(self):
        """Test getting preferences for a user in a specific domain."""
        # Set up mock response
        self.mock_ltm.search_by_metadata.return_value = [
            {
                "id": "test_id1",
                "text": "Preferred debt-to-EBITDA ratio for LBOs: 5.5x",
                "metadata": {
                    "user_id": "test_user",
                    "domain": "lbo",
                    "key": "debt_to_ebitda",
                    "value": "5.5x",
                    "description": "Preferred debt-to-EBITDA ratio for LBOs",
                    "timestamp": "2023-01-01T00:00:00Z",
                    "type": "preference"
                }
            }
        ]
        
        # Get domain preferences
        preferences = self.preference_store.get_domain_preferences("test_user", "lbo")
        
        # Check that the search was performed
        self.mock_ltm.search_by_metadata.assert_called_once_with(
            collection_name="preferences",
            filters={"user_id": "test_user", "domain": "lbo", "type": "preference"}
        )
        
        # Check that the preferences were returned
        self.assertEqual(len(preferences), 1)
        self.assertEqual(preferences[0].id, "test_id1")
        self.assertEqual(preferences[0].domain, "lbo")
        self.assertEqual(preferences[0].key, "debt_to_ebitda")
    
    def test_update_preference(self):
        """Test updating a preference in the store."""
        # Create a preference
        preference = Preference(
            id="test_id",
            user_id="test_user",
            domain="lbo",
            key="debt_to_ebitda",
            value="5.5x",
            description="Preferred debt-to-EBITDA ratio for LBOs",
            timestamp="2023-01-01T00:00:00Z"
        )
        
        # Add the preference
        self.preference_store.add_preference(preference)
        
        # Update the preference
        updated_preference = Preference(
            id="test_id",
            user_id="test_user",
            domain="lbo",
            key="debt_to_ebitda",
            value="6.0x",
            description="Updated preferred debt-to-EBITDA ratio for LBOs",
            timestamp="2023-01-01T00:00:01Z"
        )
        
        self.preference_store.update_preference(updated_preference)
        
        # Check that the document was updated in long-term memory
        self.mock_ltm.update_document.assert_called_once()
        call_args = self.mock_ltm.update_document.call_args[1]
        self.assertEqual(call_args["doc_id"], "test_id")
        self.assertEqual(call_args["collection_name"], "preferences")
        self.assertEqual(call_args["text"], "Updated preferred debt-to-EBITDA ratio for LBOs: 6.0x")
        self.assertEqual(call_args["metadata"]["user_id"], "test_user")
        self.assertEqual(call_args["metadata"]["domain"], "lbo")
        self.assertEqual(call_args["metadata"]["key"], "debt_to_ebitda")
        self.assertEqual(call_args["metadata"]["value"], "6.0x")
        self.assertEqual(call_args["metadata"]["type"], "preference")
        
        # Check that the preference file was updated
        preference_file = os.path.join(self.temp_dir, "test_user", "lbo", "debt_to_ebitda.json")
        self.assertTrue(os.path.exists(preference_file))
        
        # Check the content of the preference file
        with open(preference_file, "r") as f:
            pref_data = json.load(f)
            self.assertEqual(pref_data["id"], "test_id")
            self.assertEqual(pref_data["value"], "6.0x")
            self.assertEqual(pref_data["description"], "Updated preferred debt-to-EBITDA ratio for LBOs")
            self.assertEqual(pref_data["timestamp"], "2023-01-01T00:00:01Z")
    
    def test_delete_preference(self):
        """Test deleting a preference from the store."""
        # Create a preference
        preference = Preference(
            id="test_id",
            user_id="test_user",
            domain="lbo",
            key="debt_to_ebitda",
            value="5.5x",
            description="Preferred debt-to-EBITDA ratio for LBOs",
            timestamp="2023-01-01T00:00:00Z"
        )
        
        # Add the preference
        self.preference_store.add_preference(preference)
        
        # Set up mock response
        self.mock_ltm.get_document.return_value = {
            "id": "test_id",
            "text": "Preferred debt-to-EBITDA ratio for LBOs: 5.5x",
            "metadata": {
                "user_id": "test_user",
                "domain": "lbo",
                "key": "debt_to_ebitda",
                "value": "5.5x",
                "description": "Preferred debt-to-EBITDA ratio for LBOs",
                "timestamp": "2023-01-01T00:00:00Z",
                "type": "preference"
            }
        }
        
        # Delete the preference
        self.preference_store.delete_preference("test_id")
        
        # Check that the document was deleted from long-term memory
        self.mock_ltm.delete_document.assert_called_once_with(
            doc_id="test_id",
            collection_name="preferences"
        )
        
        # Check that the preference file was deleted
        preference_file = os.path.join(self.temp_dir, "test_user", "lbo", "debt_to_ebitda.json")
        self.assertFalse(os.path.exists(preference_file))
    
    def test_get_preference_by_key(self):
        """Test getting a preference by key."""
        # Set up mock response
        self.mock_ltm.search_by_metadata.return_value = [
            {
                "id": "test_id",
                "text": "Preferred debt-to-EBITDA ratio for LBOs: 5.5x",
                "metadata": {
                    "user_id": "test_user",
                    "domain": "lbo",
                    "key": "debt_to_ebitda",
                    "value": "5.5x",
                    "description": "Preferred debt-to-EBITDA ratio for LBOs",
                    "timestamp": "2023-01-01T00:00:00Z",
                    "type": "preference"
                }
            }
        ]
        
        # Get preference by key
        preference = self.preference_store.get_preference_by_key("test_user", "lbo", "debt_to_ebitda")
        
        # Check that the search was performed
        self.mock_ltm.search_by_metadata.assert_called_once_with(
            collection_name="preferences",
            filters={
                "user_id": "test_user",
                "domain": "lbo",
                "key": "debt_to_ebitda",
                "type": "preference"
            }
        )
        
        # Check that the preference was returned
        self.assertIsNotNone(preference)
        self.assertEqual(preference.id, "test_id")
        self.assertEqual(preference.user_id, "test_user")
        self.assertEqual(preference.domain, "lbo")
        self.assertEqual(preference.key, "debt_to_ebitda")
        self.assertEqual(preference.value, "5.5x")
    
    def test_get_preference_by_key_not_found(self):
        """Test getting a preference by key when it doesn't exist."""
        # Set up mock response
        self.mock_ltm.search_by_metadata.return_value = []
        
        # Get preference by key
        preference = self.preference_store.get_preference_by_key("test_user", "lbo", "nonexistent_key")
        
        # Check that the search was performed
        self.mock_ltm.search_by_metadata.assert_called_once()
        
        # Check that None was returned
        self.assertIsNone(preference)

if __name__ == "__main__":
    unittest.main()
