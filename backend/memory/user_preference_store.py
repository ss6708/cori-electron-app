"""
User preference store for Cori RAG++ system.
This module provides a store for user preferences.
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .models.preference import Preference
from .long_term_memory import LongTermMemory

class UserPreferenceStore:
    """
    User preference store for storing and retrieving user preferences.
    """
    
    def __init__(
        self,
        long_term_memory: LongTermMemory,
        preference_dir: str = "preferences"
    ):
        """
        Initialize the user preference store.
        
        Args:
            long_term_memory: Long-term memory for storing preferences
            preference_dir: Directory for storing preference files
        """
        self.long_term_memory = long_term_memory
        self.preference_dir = preference_dir
        
        # Create preference directory if it doesn't exist
        os.makedirs(preference_dir, exist_ok=True)
    
    def add_preference(self, preference: Preference) -> str:
        """
        Add a preference to the store.
        
        Args:
            preference: Preference to add
            
        Returns:
            ID of the added preference
        """
        # Create user directory if it doesn't exist
        user_dir = os.path.join(self.preference_dir, preference.user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        # Create domain directory if it doesn't exist
        domain_dir = os.path.join(user_dir, preference.domain)
        os.makedirs(domain_dir, exist_ok=True)
        
        # Create preference file
        preference_file = os.path.join(domain_dir, f"{preference.key}.json")
        
        # Write preference to file
        with open(preference_file, "w") as f:
            json.dump(preference.to_dict(), f, indent=2)
        
        # Add preference to long-term memory
        preference_text = f"{preference.description}: {preference.value}"
        
        self.long_term_memory.add_document(
            collection_name="preferences",
            doc_id=preference.id,
            text=preference_text,
            metadata={
                "user_id": preference.user_id,
                "domain": preference.domain,
                "key": preference.key,
                "value": preference.value,
                "description": preference.description,
                "timestamp": preference.timestamp,
                "type": "preference"
            }
        )
        
        return preference.id
    
    def get_preference(self, preference_id: str) -> Optional[Preference]:
        """
        Get a preference from the store.
        
        Args:
            preference_id: ID of the preference
            
        Returns:
            Preference or None if not found
        """
        # Get preference from long-term memory
        doc = self.long_term_memory.get_document(
            doc_id=preference_id,
            collection_name="preferences"
        )
        
        if not doc:
            return None
        
        # Create preference from document
        preference_data = {
            "id": doc["id"],
            "user_id": doc["metadata"]["user_id"],
            "domain": doc["metadata"]["domain"],
            "key": doc["metadata"]["key"],
            "value": doc["metadata"]["value"],
            "description": doc["metadata"]["description"],
            "timestamp": doc["metadata"]["timestamp"]
        }
        
        return Preference.from_dict(preference_data)
    
    def get_user_preferences(self, user_id: str) -> List[Preference]:
        """
        Get all preferences for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of preferences
        """
        # Get preferences from long-term memory
        docs = self.long_term_memory.search_by_metadata(
            collection_name="preferences",
            filters={"user_id": user_id, "type": "preference"}
        )
        
        # Create preferences from documents
        preferences = []
        for doc in docs:
            preference_data = {
                "id": doc["id"],
                "user_id": doc["metadata"]["user_id"],
                "domain": doc["metadata"]["domain"],
                "key": doc["metadata"]["key"],
                "value": doc["metadata"]["value"],
                "description": doc["metadata"]["description"],
                "timestamp": doc["metadata"]["timestamp"]
            }
            
            preferences.append(Preference.from_dict(preference_data))
        
        return preferences
    
    def get_domain_preferences(self, user_id: str, domain: str) -> List[Preference]:
        """
        Get preferences for a user in a specific domain.
        
        Args:
            user_id: ID of the user
            domain: Domain of the preferences
            
        Returns:
            List of preferences
        """
        # Get preferences from long-term memory
        docs = self.long_term_memory.search_by_metadata(
            collection_name="preferences",
            filters={"user_id": user_id, "domain": domain, "type": "preference"}
        )
        
        # Create preferences from documents
        preferences = []
        for doc in docs:
            preference_data = {
                "id": doc["id"],
                "user_id": doc["metadata"]["user_id"],
                "domain": doc["metadata"]["domain"],
                "key": doc["metadata"]["key"],
                "value": doc["metadata"]["value"],
                "description": doc["metadata"]["description"],
                "timestamp": doc["metadata"]["timestamp"]
            }
            
            preferences.append(Preference.from_dict(preference_data))
        
        return preferences
    
    def get_preference_by_key(self, user_id: str, domain: str, key: str) -> Optional[Preference]:
        """
        Get a preference by key.
        
        Args:
            user_id: ID of the user
            domain: Domain of the preference
            key: Key of the preference
            
        Returns:
            Preference or None if not found
        """
        # Get preference from long-term memory
        docs = self.long_term_memory.search_by_metadata(
            collection_name="preferences",
            filters={
                "user_id": user_id,
                "domain": domain,
                "key": key,
                "type": "preference"
            }
        )
        
        if not docs:
            return None
        
        # Create preference from document
        doc = docs[0]
        preference_data = {
            "id": doc["id"],
            "user_id": doc["metadata"]["user_id"],
            "domain": doc["metadata"]["domain"],
            "key": doc["metadata"]["key"],
            "value": doc["metadata"]["value"],
            "description": doc["metadata"]["description"],
            "timestamp": doc["metadata"]["timestamp"]
        }
        
        return Preference.from_dict(preference_data)
    
    def update_preference(self, preference: Preference) -> None:
        """
        Update a preference in the store.
        
        Args:
            preference: Preference to update
        """
        # Create user directory if it doesn't exist
        user_dir = os.path.join(self.preference_dir, preference.user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        # Create domain directory if it doesn't exist
        domain_dir = os.path.join(user_dir, preference.domain)
        os.makedirs(domain_dir, exist_ok=True)
        
        # Create preference file
        preference_file = os.path.join(domain_dir, f"{preference.key}.json")
        
        # Write preference to file
        with open(preference_file, "w") as f:
            json.dump(preference.to_dict(), f, indent=2)
        
        # Update preference in long-term memory
        preference_text = f"{preference.description}: {preference.value}"
        
        self.long_term_memory.update_document(
            doc_id=preference.id,
            collection_name="preferences",
            text=preference_text,
            metadata={
                "user_id": preference.user_id,
                "domain": preference.domain,
                "key": preference.key,
                "value": preference.value,
                "description": preference.description,
                "timestamp": preference.timestamp,
                "type": "preference"
            }
        )
    
    def delete_preference(self, preference_id: str) -> None:
        """
        Delete a preference from the store.
        
        Args:
            preference_id: ID of the preference
        """
        # Get preference
        preference = self.get_preference(preference_id)
        
        if not preference:
            return
        
        # Delete preference file
        preference_file = os.path.join(
            self.preference_dir,
            preference.user_id,
            preference.domain,
            f"{preference.key}.json"
        )
        
        if os.path.exists(preference_file):
            os.remove(preference_file)
        
        # Delete preference from long-term memory
        self.long_term_memory.delete_document(
            doc_id=preference_id,
            collection_name="preferences"
        )
