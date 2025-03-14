from typing import Dict, List, Optional, Any, Tuple
import uuid
import os
import json
from datetime import datetime

from .models.preference import UserPreference, ModelingPreference, AnalysisPreference, VisualizationPreference, WorkflowPreference

class UserPreferenceStore:
    """
    Manages storage and retrieval of user preferences.
    This is part of the second tier of the three-tier memory architecture.
    """
    
    def __init__(self, storage_path: str, user_id: str):
        """
        Initialize the user preference store.
        
        Args:
            storage_path: Path to the preference storage directory
            user_id: Identifier for the user
        """
        self.storage_path = storage_path
        self.user_id = user_id
        self.preferences: Dict[str, UserPreference] = {}
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing preferences
        self._load_preferences()
    
    def _load_preferences(self) -> None:
        """Load preferences from storage."""
        preference_file = os.path.join(self.storage_path, f"{self.user_id}_preferences.json")
        
        if os.path.exists(preference_file):
            try:
                with open(preference_file, 'r') as f:
                    preferences_data = json.load(f)
                
                for pref_data in preferences_data:
                    pref_type = pref_data.get("preference_type")
                    
                    if pref_type == "modeling":
                        preference = ModelingPreference(**pref_data)
                    elif pref_type == "analysis":
                        preference = AnalysisPreference(**pref_data)
                    elif pref_type == "visualization":
                        preference = VisualizationPreference(**pref_data)
                    elif pref_type == "workflow":
                        preference = WorkflowPreference(**pref_data)
                    else:
                        # Generic preference
                        preference = UserPreference(**pref_data)
                    
                    self.preferences[preference.id] = preference
            except Exception as e:
                print(f"Error loading preferences: {e}")
    
    def _save_preferences(self) -> None:
        """Save preferences to storage."""
        preference_file = os.path.join(self.storage_path, f"{self.user_id}_preferences.json")
        
        try:
            preferences_data = [pref.to_dict() for pref in self.preferences.values()]
            
            with open(preference_file, 'w') as f:
                json.dump(preferences_data, f, default=str)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def add_preference(self, preference: UserPreference) -> str:
        """
        Add a preference.
        
        Args:
            preference: The preference to add
            
        Returns:
            Preference ID
        """
        # Ensure user_id matches
        if preference.user_id != self.user_id:
            preference.user_id = self.user_id
        
        self.preferences[preference.id] = preference
        self._save_preferences()
        
        return preference.id
    
    def get_preference(self, preference_id: str) -> Optional[UserPreference]:
        """
        Get a preference by ID.
        
        Args:
            preference_id: The preference ID
            
        Returns:
            Preference if found, None otherwise
        """
        return self.preferences.get(preference_id)
    
    def update_preference(self, preference: UserPreference) -> bool:
        """
        Update a preference.
        
        Args:
            preference: The updated preference
            
        Returns:
            True if preference was updated, False otherwise
        """
        if preference.id not in self.preferences:
            return False
        
        # Ensure user_id matches
        if preference.user_id != self.user_id:
            preference.user_id = self.user_id
        
        self.preferences[preference.id] = preference
        self._save_preferences()
        
        return True
    
    def delete_preference(self, preference_id: str) -> bool:
        """
        Delete a preference.
        
        Args:
            preference_id: The preference ID
            
        Returns:
            True if preference was deleted, False otherwise
        """
        if preference_id not in self.preferences:
            return False
        
        del self.preferences[preference_id]
        self._save_preferences()
        
        return True
    
    def get_preferences_by_type(self, preference_type: str) -> List[UserPreference]:
        """
        Get preferences by type.
        
        Args:
            preference_type: The preference type
            
        Returns:
            List of preferences of the specified type
        """
        return [
            pref for pref in self.preferences.values()
            if pref.preference_type == preference_type
        ]
    
    def get_preferences_by_domain(self, domain: str) -> List[UserPreference]:
        """
        Get preferences by domain.
        
        Args:
            domain: The domain
            
        Returns:
            List of preferences for the specified domain
        """
        return [
            pref for pref in self.preferences.values()
            if pref.domain == domain
        ]
    
    def get_contextual_preferences(
        self,
        domain: Optional[str] = None,
        preference_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[UserPreference]:
        """
        Get preferences based on context.
        
        Args:
            domain: Optional domain filter
            preference_type: Optional preference type filter
            context: Optional additional context for filtering
            
        Returns:
            List of relevant preferences
        """
        # Start with all preferences
        filtered_preferences = list(self.preferences.values())
        
        # Filter by domain if specified
        if domain:
            filtered_preferences = [
                pref for pref in filtered_preferences
                if pref.domain == domain or pref.domain == "general"
            ]
        
        # Filter by preference type if specified
        if preference_type:
            filtered_preferences = [
                pref for pref in filtered_preferences
                if pref.preference_type == preference_type
            ]
        
        # Apply additional context-based filtering
        if context:
            # This would be extended with more sophisticated filtering
            # based on the specific context and preference types
            pass
        
        return filtered_preferences
    
    def create_modeling_preference(
        self,
        approach: str,
        parameters: Dict[str, Any],
        description: str,
        domain: str = "general"
    ) -> str:
        """
        Create a modeling preference.
        
        Args:
            approach: Modeling approach
            parameters: Modeling parameters
            description: Preference description
            domain: Optional domain
            
        Returns:
            Preference ID
        """
        preference = ModelingPreference(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            timestamp=datetime.now(),
            domain=domain,
            approach=approach,
            parameters=parameters,
            description=description
        )
        
        return self.add_preference(preference)
    
    def create_analysis_preference(
        self,
        method: str,
        metrics: List[str],
        parameters: Dict[str, Any],
        description: str,
        domain: str = "general"
    ) -> str:
        """
        Create an analysis preference.
        
        Args:
            method: Analysis method
            metrics: Analysis metrics
            parameters: Analysis parameters
            description: Preference description
            domain: Optional domain
            
        Returns:
            Preference ID
        """
        preference = AnalysisPreference(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            timestamp=datetime.now(),
            domain=domain,
            method=method,
            metrics=metrics,
            parameters=parameters,
            description=description
        )
        
        return self.add_preference(preference)
