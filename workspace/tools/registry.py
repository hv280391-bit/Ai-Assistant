"""
Tool registry for managing and executing tools
"""

from typing import Dict, Any
from core.config import Config
from auth.manager import AuthManager
from audit.logger import AuditLogger
from core.parser import ToolCall

from .files import SearchFilesTool, ReadTextFileTool
from .processes import ListProcessesTool
from .apps import OpenAppTool
from .web import ReadWebpageTool
from .scheduler import ScheduleReminderTool
from .elevation import RequestElevationTool

class ToolRegistry:
    """Registry for managing and executing tools"""
    
    def __init__(self, config: Config, auth_manager: AuthManager, audit_logger: AuditLogger):
        self.config = config
        self.auth_manager = auth_manager
        self.audit_logger = audit_logger
        
        # Initialize tools
        self.tools = {
            "search_files": SearchFilesTool(config, auth_manager, audit_logger),
            "read_text_file": ReadTextFileTool(config, auth_manager, audit_logger),
            "list_processes": ListProcessesTool(config, auth_manager, audit_logger),
            "open_app": OpenAppTool(config, auth_manager, audit_logger),
            "read_webpage": ReadWebpageTool(config, auth_manager, audit_logger),
            "schedule_reminder": ScheduleReminderTool(config, auth_manager, audit_logger),
            "request_elevation": RequestElevationTool(config, auth_manager, audit_logger)
        }
    
    def execute_tool(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute a tool call"""
        tool_name = tool_call.tool
        
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        tool = self.tools[tool_name]
        
        # Check permissions
        if not tool.check_permission():
            return {"error": f"Permission denied for tool: {tool_name}"}
        
        # Execute tool
        try:
            result = tool.execute(**tool_call.args)
            return result
        except TypeError as e:
            return {"error": f"Invalid arguments for {tool_name}: {str(e)}"}
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def get_available_tools(self) -> Dict[str, str]:
        """Get list of available tools for current user"""
        available = {}
        
        for tool_name, tool in self.tools.items():
            if tool.check_permission():
                available[tool_name] = tool.__class__.__doc__ or "No description"
        
        return available