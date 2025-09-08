"""
Simple configuration management for Local AI Assistant
"""

import json
import os
from pathlib import Path
import datetime

class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.data = self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return default config
        return {
            "users": {},
            "configured": False,
            "settings": {
                "max_sessions": 10,
                "session_timeout": 3600
            }
        }
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get_user(self, username):
        """Get user data by username"""
        return self.data.get("users", {}).get(username)
    
    def add_user(self, username, password_hash, role, email=None):
        """Add a new user - FIXED to handle 5 arguments properly"""
        if "users" not in self.data:
            self.data["users"] = {}
        
        self.data["users"][username] = {
            "password_hash": password_hash,
            "role": role,
            "email": email or "",
            "created_at": datetime.datetime.now().isoformat()
        }
        self._save_config()
    
    def update_user(self, username, **kwargs):
        """Update user data"""
        if username in self.data.get("users", {}):
            self.data["users"][username].update(kwargs)
            self._save_config()
    
    def delete_user(self, username):
        """Delete a user"""
        if username in self.data.get("users", {}):
            del self.data["users"][username]
            self._save_config()
    
    def list_users(self):
        """List all users"""
        return list(self.data.get("users", {}).keys())
    
    def is_configured(self):
        """Check if system is configured"""
        return self.data.get("configured", False)
    
    def mark_configured(self):
        """Mark system as configured"""
        self.data["configured"] = True
        self._save_config()
    
    def get_setting(self, key, default=None):
        """Get a setting value"""
        return self.data.get("settings", {}).get(key, default)
    
    def set_setting(self, key, value):
        """Set a setting value"""
        if "settings" not in self.data:
            self.data["settings"] = {}
        self.data["settings"][key] = value
        self._save_config()