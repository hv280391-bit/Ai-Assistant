"""
Base tool interface for Local AI Assistant
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from core.config import Config
from auth.manager import AuthManager
from audit.logger import AuditLogger

class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self, config: Config, auth_manager: AuthManager, audit_logger: AuditLogger):
        self.config = config
        self.auth_manager = auth_manager
        self.audit_logger = audit_logger
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given arguments"""
        pass
    
    @abstractmethod
    def get_required_permission(self) -> str:
        """Get the required permission for this tool"""
        pass
    
    def log_execution(self, args: Dict[str, Any], result: Dict[str, Any]):
        """Log tool execution"""
        self.audit_logger.log_event("tool_execution", {
            "tool": self.__class__.__name__,
            "user": self.auth_manager.current_user,
            "args": args,
            "result_type": "success" if "success" in result else "error"
        })
    
    def check_permission(self) -> bool:
        """Check if current user has permission to use this tool"""
        required_permission = self.get_required_permission()
        return self.auth_manager.has_permission(required_permission)