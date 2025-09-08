"""
Multilingual Local AI Assistant
Enhanced version supporting Hindi and other languages
"""

import json
import os
import subprocess
import glob
from pathlib import Path
import datetime
from typing import Optional, Dict, Any, List

from core.multilingual_parser import MultilingualParser

class MultilingualTools:
    """Enhanced tools with multilingual support"""
    
    def __init__(self, config, auth_manager):
        self.config = config
        self.auth_manager = auth_manager
    
    def search_files(self, query: str, base: str = None) -> str:
        """Search for files with multilingual response"""
        if not self.auth_manager.has_permission("can_search_files"):
            return "Permission denied: Cannot search files / अनुमति नहीं है: Files search नहीं कर सकते"
        
        if base is None:
            base = str(Path.home())
        
        # Handle special system files query
        if query in ["*.conf *.cfg *.ini *.json *.xml"]:
            return self._search_system_files()
        
        # Expand home directory
        if base.startswith('~'):
            base = str(Path.home() / base[2:]) if len(base) > 1 else str(Path.home())
        
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
            return f"Access denied: Path '{base}' is not allowlisted / पहुंच अस्वीकृत: Path '{base}' allowlisted नहीं है"
        
        try:
            results = []
            
            # Handle multiple patterns
            patterns = query.split() if ' ' in query else [query]
            
            for pattern in patterns:
                if not pattern.startswith('*'):
                    pattern = f"*{pattern}*"
                
                search_pattern = str(base_path / "**" / pattern)
                for file_path in glob.glob(search_pattern, recursive=True):
                    if len(results) >= 20:  # Limit results
                        break
                    if os.path.isfile(file_path):
                        results.append(file_path)
            
            if results:
                hindi_response = f"मिली {len(results)} files:\n"
                english_response = f"Found {len(results)} files:\n"
                file_list = "\n".join(results[:10])
                
                return f"{hindi_response}{english_response}{file_list}"
            else:
                return f"कोई files नहीं मिली / No files found matching '{query}' in '{base}'"
                
        except Exception as e:
            return f"Error searching files / Files search करने में error: {e}"
    
    def _search_system_files(self) -> str:
        """Search for important system files"""
        important_paths = [
            "/etc/passwd", "/etc/hosts", "/etc/fstab", "/etc/crontab",
            "~/.bashrc", "~/.profile", "~/.ssh/config",
            "/var/log/syslog", "/var/log/auth.log"
        ]
        
        found_files = []
        for path in important_paths:
            expanded_path = Path(path).expanduser()
            if expanded_path.exists():
                found_files.append(str(expanded_path))
        
        if found_files:
            return f"System की important files मिली / Found important system files:\n" + "\n".join(found_files)
        else:
            return "कोई important system files accessible नहीं हैं / No accessible important system files found"
    
    def read_file(self, path: str) -> str:
        """Read file contents with multilingual response"""
        if not self.auth_manager.has_permission("can_read_files"):
            return "Permission denied: Cannot read files / अनुमति नहीं है: Files read नहीं कर सकते"
        
        # Expand home directory
        if path.startswith('~'):
            path = str(Path.home() / path[2:]) if len(path) > 1 else str(Path.home())
        
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
            return f"Access denied: Path '{path}' is not allowlisted / पहुंच अस्वीकृत: Path '{path}' allowlisted नहीं है"
        
        try:
            if not file_path.exists():
                return f"File not found / File नहीं मिली: {path}"
            
            if file_path.stat().st_size > self.config.data["max_file_size_mb"] * 1024 * 1024:
                return f"File too large / File बहुत बड़ी है (max {self.config.data['max_file_size_mb']}MB)"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if len(content) > 5000:  # Truncate long content
                    content = content[:5000] + "\n... (truncated / काटा गया)"
                
                return f"Content of {path} / {path} का content:\n{content}"
                
        except Exception as e:
            return f"Error reading file / File read करने में error: {e}"
    
    def list_processes(self) -> str:
        """List running processes with multilingual response"""
        if not self.auth_manager.has_permission("can_list_processes"):
            return "Permission denied: Cannot list processes / अनुमति नहीं है: Processes list नहीं कर सकते"
        
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=10)
                lines = result.stdout.split('\n')[:20]  # First 20 lines
                return "Running processes / चल रही processes:\n" + "\n".join(lines)
            else:  # Unix-like
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
                lines = result.stdout.split('\n')[:20]  # First 20 lines
                return "Running processes / चल रही processes:\n" + "\n".join(lines)
        except Exception as e:
            return f"Error listing processes / Processes list करने में error: {e}"
    
    def open_app(self, name: str) -> str:
        """Open application with multilingual response"""
        if not self.auth_manager.has_permission("can_open_apps"):
            return "Permission denied: Cannot open applications / अनुमति नहीं है: Applications open नहीं कर सकते"
        
        if name not in self.config.whitelisted_apps:
            return f"Application '{name}' is not whitelisted / Application '{name}' whitelisted नहीं है"
        
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen([name], shell=True)
            else:  # Unix-like
                subprocess.Popen([name])
            return f"Launched {name} / {name} को launch किया गया"
        except Exception as e:
            return f"Error launching {name} / {name} launch करने में error: {e}"

class MultilingualAssistant:
    """Main multilingual assistant class"""
    
    def __init__(self, config, auth_manager):
        self.config = config
        self.auth_manager = auth_manager
        self.parser = MultilingualParser()
        self.tools = MultilingualTools(config, auth_manager)
        
    def start_chat(self):
        """Start the main chat loop"""
        print("\n🤖 Local AI Assistant is ready! / Local AI Assistant तैयार है!")
        print("Type 'help' for commands, 'quit' to exit / Commands के लिए 'help' type करें, exit के लिए 'quit'\n")
        
        while True:
            try:
                # Get user input
                user_input = input(f"{self.auth_manager.current_user}> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'bye', 'band karo', 'bandh karo']:
                    print("Goodbye! / अलविदा!")
                    break
                    
                if user_input.lower() in ['help', 'madad']:
                    self._show_help()
                    continue
                
                # Process the command
                self._process_command(user_input)
                
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit properly. / Properly exit करने के लिए 'quit' use करें।")
            except Exception as e:
                print(f"Error / Error: {e}")
    
    def _process_command(self, user_input: str):
        """Process a user command in multiple languages"""
        # Parse the command
        tool_call = self.parser.parse_command(user_input)
        
        if not tool_call:
            print("I don't understand that command. / मुझे यह command समझ नहीं आई। Type 'help' for available commands.")
            return
        
        # Request confirmation for sensitive operations
        if tool_call["tool"] in ["open_app"] and self.auth_manager.current_role != "admin":
            response = input(f"Execute {tool_call['tool']}? (y/n) / {tool_call['tool']} execute करें? (y/n): ").lower()
            if response not in ['y', 'yes', 'haan', 'ha']:
                print("Operation cancelled. / Operation cancel किया गया।")
                return
        
        # Execute the tool
        try:
            tool_name = tool_call["tool"]
            args = tool_call["args"]
            
            if hasattr(self.tools, tool_name):
                result = getattr(self.tools, tool_name)(**args)
                print(result)
            else:
                print(f"Unknown tool / अज्ञात tool: {tool_name}")
                
        except Exception as e:
            print(f"Error executing {tool_call['tool']} / {tool_call['tool']} execute करने में error: {e}")
    
    def _show_help(self):
        """Show help information in multiple languages"""
        help_text = self.parser.get_help_text('hindi')
        print(help_text)
        
        # Also show English help
        print("\n" + "="*50)
        english_help = self.parser.get_help_text('english')
        print(english_help)