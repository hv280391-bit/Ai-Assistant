"""
Security utilities and validation
"""

import os
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from core.config import Config
from core.parser import ToolCall

class SecurityManager:
    """Manages security validation for tool calls"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def validate_tool_call(self, tool_call: ToolCall) -> bool:
        """Validate tool call for security compliance"""
        
        # Validate based on tool type
        if tool_call.tool == "search_files":
            return self._validate_file_access(tool_call.args.get("base"))
        
        elif tool_call.tool == "read_text_file":
            return self._validate_file_access(tool_call.args.get("path"))
        
        elif tool_call.tool == "open_app":
            return self._validate_app_access(tool_call.args.get("name"))
        
        elif tool_call.tool == "read_webpage":
            return self._validate_url_access(tool_call.args.get("url"))
        
        elif tool_call.tool == "request_elevation":
            return self._validate_elevation_command(tool_call.args.get("cmd"))
        
        # Other tools are generally safe
        return True
    
    def _validate_file_access(self, path: str) -> bool:
        """Validate file/directory access against allowlist"""
        if not path:
            return True  # Will use default allowlisted paths
        
        try:
            resolved_path = str(Path(path).resolve())
            
            # Check against allowlisted paths
            for allowed_path in self.config.allowlisted_paths:
                if resolved_path.startswith(os.path.abspath(allowed_path)):
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _validate_app_access(self, app_name: str) -> bool:
        """Validate application against whitelist"""
        if not app_name:
            return False
        
        return app_name in self.config.whitelisted_apps
    
    def _validate_url_access(self, url: str) -> bool:
        """Validate URL for web access"""
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            
            # Only allow HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Block localhost and private IPs for security
            hostname = parsed.hostname
            if hostname:
                if hostname in ['localhost', '127.0.0.1', '::1']:
                    return False
                
                # Block private IP ranges
                if hostname.startswith(('10.', '172.', '192.168.')):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_elevation_command(self, cmd: str) -> bool:
        """Validate elevated command for basic safety"""
        if not cmd:
            return False
        
        # Block obviously dangerous commands
        dangerous_patterns = [
            'rm -rf /',
            'del /f /s /q c:',
            'format c:',
            'dd if=/dev/zero',
            'chmod 777 /',
            'chown root:root /',
            '> /dev/sda',
            'mkfs.',
            'fdisk',
            'parted'
        ]
        
        cmd_lower = cmd.lower()
        for pattern in dangerous_patterns:
            if pattern in cmd_lower:
                return False
        
        return True
    
    def is_safe_path(self, path: str) -> bool:
        """Check if path is safe for access"""
        try:
            resolved_path = Path(path).resolve()
            
            # Check for path traversal attempts
            if '..' in str(resolved_path):
                return False
            
            # Check against allowlisted paths
            for allowed_path in self.config.allowlisted_paths:
                if str(resolved_path).startswith(os.path.abspath(allowed_path)):
                    return True
            
            return False
            
        except Exception:
            return False