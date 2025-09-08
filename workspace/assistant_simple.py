"""
Simplified main assistant logic using only standard library
"""

import json
import re
from typing import Optional, Dict, Any, List
import os
import subprocess
import glob
from pathlib import Path
import datetime

class CommandParser:
    """Simple command parser"""
    
    def parse_command(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse natural language command"""
        text = text.strip().lower()
        
        # File search
        if re.search(r'find|search|locate', text):
            match = re.search(r'find\s+(.+?)\s+(?:in|under)\s+(.+)', text)
            if match:
                return {"tool": "search_files", "args": {"query": match.group(1).strip(), "base": match.group(2).strip()}}
            match = re.search(r'(?:find|search|locate)\s+(.+)', text)
            if match:
                return {"tool": "search_files", "args": {"query": match.group(1).strip()}}
        
        # File read
        if re.search(r'read|open|show|cat', text):
            match = re.search(r'(?:read|open|show|cat)\s+(.+)', text)
            if match:
                return {"tool": "read_file", "args": {"path": match.group(1).strip()}}
        
        # List processes
        if re.search(r'list\s+processes|show.*processes|ps|what.*running', text):
            return {"tool": "list_processes", "args": {}}
        
        # Open app
        if re.search(r'open|launch|start|run', text) and not re.search(r'read|show', text):
            match = re.search(r'(?:open|launch|start|run)\s+(.+)', text)
            if match:
                return {"tool": "open_app", "args": {"name": match.group(1).strip()}}
        
        return None

class SimpleTools:
    """Simple tools using only standard library"""
    
    def __init__(self, config, auth_manager):
        self.config = config
        self.auth_manager = auth_manager
    
    def search_files(self, query: str, base: str = None) -> str:
        """Search for files"""
        if not self.auth_manager.has_permission("can_search_files"):
            return "Permission denied: Cannot search files"
        
        if base is None:
            base = str(Path.home())
        
        # Validate path is allowlisted
        base_path = Path(base).resolve()
        allowed = False
        for allowed_path in self.config.allowlisted_paths:
            try:
                base_path.relative_to(Path(allowed_path).resolve())
                allowed = True
                break
            except ValueError:
                continue
        
        if not allowed:
            return f"Access denied: Path '{base}' is not allowlisted"
        
        try:
            results = []
            pattern = f"**/*{query}*"
            
            for file_path in glob.glob(str(base_path / pattern), recursive=True):
                if len(results) >= 20:  # Limit results
                    break
                results.append(file_path)
            
            if results:
                return f"Found {len(results)} files:\n" + "\n".join(results[:10])
            else:
                return f"No files found matching '{query}' in '{base}'"
                
        except Exception as e:
            return f"Error searching files: {e}"
    
    def read_file(self, path: str) -> str:
        """Read file contents"""
        if not self.auth_manager.has_permission("can_read_files"):
            return "Permission denied: Cannot read files"
        
        file_path = Path(path).resolve()
        
        # Validate path is allowlisted
        allowed = False
        for allowed_path in self.config.allowlisted_paths:
            try:
                file_path.relative_to(Path(allowed_path).resolve())
                allowed = True
                break
            except ValueError:
                continue
        
        if not allowed:
            return f"Access denied: Path '{path}' is not allowlisted"
        
        try:
            if not file_path.exists():
                return f"File not found: {path}"
            
            if file_path.stat().st_size > self.config.data["max_file_size_mb"] * 1024 * 1024:
                return f"File too large (max {self.config.data['max_file_size_mb']}MB)"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if len(content) > 5000:  # Truncate long content
                    content = content[:5000] + "\n... (truncated)"
                return f"Content of {path}:\n{content}"
                
        except Exception as e:
            return f"Error reading file: {e}"
    
    def list_processes(self) -> str:
        """List running processes"""
        if not self.auth_manager.has_permission("can_list_processes"):
            return "Permission denied: Cannot list processes"
        
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=10)
                lines = result.stdout.split('\n')[:20]  # First 20 lines
                return "Running processes:\n" + "\n".join(lines)
            else:  # Unix-like
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
                lines = result.stdout.split('\n')[:20]  # First 20 lines
                return "Running processes:\n" + "\n".join(lines)
        except Exception as e:
            return f"Error listing processes: {e}"
    
    def open_app(self, name: str) -> str:
        """Open application"""
        if not self.auth_manager.has_permission("can_open_apps"):
            return "Permission denied: Cannot open applications"
        
        if name not in self.config.whitelisted_apps:
            return f"Application '{name}' is not whitelisted"
        
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen([name], shell=True)
            else:  # Unix-like
                subprocess.Popen([name])
            return f"Launched {name}"
        except Exception as e:
            return f"Error launching {name}: {e}"

class LocalAssistant:
    """Main assistant class"""
    
    def __init__(self, config, auth_manager):
        self.config = config
        self.auth_manager = auth_manager
        self.parser = CommandParser()
        self.tools = SimpleTools(config, auth_manager)
        
    def start_chat(self):
        """Start the main chat loop"""
        print("\n🤖 Local AI Assistant is ready!")
        print("Type 'help' for commands, 'quit' to exit\n")
        
        while True:
            try:
                # Get user input
                user_input = input(f"{self.auth_manager.current_user}> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye!")
                    break
                    
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                # Process the command
                self._process_command(user_input)
                
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit properly.")
            except Exception as e:
                print(f"Error: {e}")
    
    def _process_command(self, user_input: str):
        """Process a user command"""
        # Parse the command
        tool_call = self.parser.parse_command(user_input)
        
        if not tool_call:
            print("I don't understand that command. Type 'help' for available commands.")
            return
        
        # Request confirmation for sensitive operations
        if tool_call["tool"] in ["open_app"] and self.auth_manager.current_role != "admin":
            response = input(f"Execute {tool_call['tool']}? (y/n): ").lower()
            if response not in ['y', 'yes']:
                print("Operation cancelled.")
                return
        
        # Execute the tool
        try:
            tool_name = tool_call["tool"]
            args = tool_call["args"]
            
            if hasattr(self.tools, tool_name):
                result = getattr(self.tools, tool_name)(**args)
                print(result)
            else:
                print(f"Unknown tool: {tool_name}")
                
        except Exception as e:
            print(f"Error executing {tool_call['tool']}: {e}")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
=== Local AI Assistant Commands ===

File Operations:
• find <filename> in <directory>  - Search for files
• read <filepath>                 - Read file contents

System Operations:
• list processes                  - Show running processes
• open <app_name>                 - Launch application

General:
• help                           - Show this help
• quit                           - Exit assistant

Examples:
• find config.txt in /home/user
• read /home/user/documents/file.txt
• list processes
• open notepad
        """
        print(help_text)