"""
Service for managing user data persistence
"""
import json
import os
from typing import Dict, Any

class DataService:
    """Handles saving and loading user resume data"""
    
    def __init__(self, data_file='data/user_data.json'):
        self.data_file = data_file
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def save_user_data(self, data: Dict[str, Any]) -> bool:
        """
        Save user resume data to file
        
        Args:
            data: Dictionary containing user resume information
            
        Returns:
            bool: True if successful
        """
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            raise Exception(f"Error saving data: {str(e)}")
    
    def load_user_data(self) -> Dict[str, Any]:
        """
        Load saved user resume data
        
        Returns:
            Dictionary containing user resume information
        """
        try:
            if not os.path.exists(self.data_file):
                return self._get_empty_template()
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def _get_empty_template(self) -> Dict[str, Any]:
        """Return empty data template"""
        return {
            'personal_info': {
                'name': '',
                'title': '',
                'address': '',
                'email': '',
                'linkedin': '',
                'phone': ''
            },
            'professional_summary': '',
            'skills': [],
            'work_experience': [],
            'projects': [],
            'certifications': [],
            'education': []
        }

