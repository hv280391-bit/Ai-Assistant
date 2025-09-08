"""
Privileged operation tool with OS-native credential prompts
"""

import subprocess
import os
import getpass
from typing import Dict, Any

from .base import BaseTool

class RequestElevationTool(BaseTool):
    """Tool for executing privileged commands with OS-native prompts"""
    
    def get_required_permission(self) -> str:
        return "can_elevate"
    
    def execute(self, cmd: str) -> Dict[str, Any]:
        """Execute privileged command with OS-native credential prompt"""
        try:
            # This tool requires explicit authorization
            if not self.auth_manager.require_elevation():
                return {"error": "Elevation not authorized for current user"}
            
            # Execute command with OS-native elevation
            if os.name == 'nt':  # Windows
                result = self._execute_windows_elevated(cmd)
            else:  # Unix-like systems
                result = self._execute_unix_elevated(cmd)
            
            self.log_execution({"cmd": cmd}, {"success": "Elevated command executed"})
            return result
            
        except Exception as e:
            error_result = {"error": str(e)}
            self.log_execution({"cmd": cmd}, error_result)
            return error_result
    
    def _execute_windows_elevated(self, cmd: str) -> Dict[str, Any]:
        """Execute command with Windows UAC prompt"""
        try:
            # Use PowerShell with -Verb RunAs to trigger UAC
            ps_cmd = f'Start-Process cmd -ArgumentList "/c {cmd}" -Verb RunAs -Wait'
            
            result = subprocess.run(
                ['powershell', '-Command', ps_cmd],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    "success": f"Command executed successfully: {cmd}",
                    "data": {
                        "command": cmd,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "return_code": result.returncode
                    }
                }
            else:
                return {
                    "error": f"Command failed with return code {result.returncode}",
                    "data": {
                        "command": cmd,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "return_code": result.returncode
                    }
                }
                
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": f"Windows elevation failed: {str(e)}"}
    
    def _execute_unix_elevated(self, cmd: str) -> Dict[str, Any]:
        """Execute command with sudo prompt"""
        try:
            # Use sudo with the command
            sudo_cmd = ['sudo', '-S'] + cmd.split()
            
            # Execute with sudo
            result = subprocess.run(
                sudo_cmd,
                capture_output=True,
                text=True,
                timeout=60,
                input=None  # Let sudo handle password prompting
            )
            
            if result.returncode == 0:
                return {
                    "success": f"Command executed successfully: {cmd}",
                    "data": {
                        "command": cmd,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "return_code": result.returncode
                    }
                }
            else:
                return {
                    "error": f"Command failed with return code {result.returncode}",
                    "data": {
                        "command": cmd,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "return_code": result.returncode
                    }
                }
                
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": f"Unix elevation failed: {str(e)}"}