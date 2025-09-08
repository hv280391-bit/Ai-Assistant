"""
Application launcher tool
"""

import subprocess
import os
import shutil
from typing import Dict, Any

from .base import BaseTool

class OpenAppTool(BaseTool):
    """Tool for launching whitelisted applications"""
    
    def get_required_permission(self) -> str:
        return "can_open_apps"
    
    def execute(self, name: str) -> Dict[str, Any]:
        """Launch a whitelisted application"""
        try:
            # Check if app is whitelisted
            if name not in self.config.whitelisted_apps:
                return {"error": f"Application '{name}' is not whitelisted"}
            
            # Try to find and launch the application
            app_path = self._find_application(name)
            if not app_path:
                return {"error": f"Application '{name}' not found on system"}
            
            # Launch the application
            if os.name == 'nt':  # Windows
                subprocess.Popen([app_path], shell=True)
            else:  # Unix-like systems
                subprocess.Popen([app_path])
            
            self.log_execution({"name": name}, {"success": f"Launched {name}"})
            
            return {
                "success": f"Successfully launched {name}",
                "data": {"app_name": name, "app_path": app_path}
            }
            
        except Exception as e:
            error_result = {"error": str(e)}
            self.log_execution({"name": name}, error_result)
            return error_result
    
    def _find_application(self, name: str) -> str:
        """Find application executable path"""
        # First try to find in PATH
        app_path = shutil.which(name)
        if app_path:
            return app_path
        
        # Platform-specific search
        if os.name == 'nt':  # Windows
            return self._find_windows_app(name)
        else:  # Unix-like systems
            return self._find_unix_app(name)
    
    def _find_windows_app(self, name: str) -> str:
        """Find Windows application"""
        # Common Windows application paths
        search_paths = [
            os.path.expandvars(r"%ProgramFiles%"),
            os.path.expandvars(r"%ProgramFiles(x86)%"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
            os.path.expandvars(r"%APPDATA%")
        ]
        
        # Add .exe if not present
        if not name.endswith('.exe'):
            name += '.exe'
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                for root, dirs, files in os.walk(search_path):
                    if name.lower() in [f.lower() for f in files]:
                        return os.path.join(root, name)
        
        return None
    
    def _find_unix_app(self, name: str) -> str:
        """Find Unix application"""
        # Common Unix application paths
        search_paths = [
            "/usr/bin",
            "/usr/local/bin",
            "/opt",
            "/Applications"  # macOS
        ]
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                app_path = os.path.join(search_path, name)
                if os.path.exists(app_path) and os.access(app_path, os.X_OK):
                    return app_path
                
                # For macOS .app bundles
                if search_path == "/Applications":
                    app_bundle = os.path.join(search_path, f"{name}.app")
                    if os.path.exists(app_bundle):
                        return f"open -a '{name}'"
        
        return None