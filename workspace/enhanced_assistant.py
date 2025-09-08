"""
Enhanced Local AI Assistant with Natural Language Processing
Complete system with session management and comprehensive tools
"""

import json
import os
import subprocess
import platform
from pathlib import Path
import datetime
from typing import Optional, Dict, Any, List

from core.enhanced_parser import EnhancedNaturalLanguageParser
from core.system_scanner import ComprehensiveSystemScanner
from core.config_simple import Config

class EnhancedAssistantTools:
    """Enhanced tools with natural language support and system scanning"""
    
    def __init__(self, config, user_role):
        self.config = config
        self.user_role = user_role
        self.parser = EnhancedNaturalLanguageParser()
        self.scanner = ComprehensiveSystemScanner()
    
    def process_message(self, message: str) -> str:
        """Process natural language message and return response"""
        try:
            # Parse the command
            command = self.parser.parse_command(message)
            
            if not command:
                return "I didn't understand that. Can you try rephrasing? / मुझे समझ नहीं आया। कृपया दोबारा कहें।"
            
            tool_name = command["tool"]
            args = command.get("args", {})
            
            # Execute the appropriate tool
            if tool_name == "casual_response":
                return self._handle_casual_response(args.get("text", ""))
            elif tool_name == "system_scan":
                return self._handle_system_scan()
            elif tool_name == "find_files":
                return self._handle_find_files(args.get("query", ""))
            elif tool_name == "system_info":
                return self._handle_system_info()
            elif tool_name == "list_processes":
                return self._handle_list_processes()
            elif tool_name == "open_app":
                return self._handle_open_app(args.get("app_name", ""))
            elif tool_name == "help":
                return self._handle_help()
            else:
                return f"Tool '{tool_name}' is not implemented yet."
                
        except Exception as e:
            return f"Error processing message: {str(e)}"
    
    def _handle_casual_response(self, text: str) -> str:
        """Handle casual conversation"""
        response = self.parser.get_casual_response(text)
        return response
    
    def _handle_system_scan(self) -> str:
        """Handle system scan request"""
        if not self._check_permission("can_scan_system"):
            return "Permission denied: Cannot perform system scan / अनुमति नहीं है: System scan नहीं कर सकते"
        
        try:
            scan_results = self.scanner.full_system_scan()
            
            if 'error' in scan_results:
                return f"System scan failed: {scan_results['error']}"
            
            # Format the results nicely
            summary = self._format_scan_summary(scan_results)
            return summary
            
        except Exception as e:
            return f"System scan error: {str(e)}"
    
    def _handle_find_files(self, query: str) -> str:
        """Handle file search request"""
        if not self._check_permission("can_search_files"):
            return "Permission denied: Cannot search files / अनुमति नहीं है: Files search नहीं कर सकते"
        
        try:
            results = self.scanner.smart_file_search(query)
            
            if not results:
                return f"No files found matching '{query}' / '{query}' के लिए कोई files नहीं मिली"
            
            response = f"Found {len(results)} files matching '{query}' / '{query}' के लिए {len(results)} files मिली:\n\n"
            for i, file_path in enumerate(results[:10], 1):
                response += f"{i}. {file_path}\n"
            
            if len(results) > 10:
                response += f"\n... and {len(results) - 10} more files / और {len(results) - 10} files हैं"
            
            return response
            
        except Exception as e:
            return f"File search error: {str(e)}"
    
    def _handle_system_info(self) -> str:
        """Handle system information request"""
        if not self._check_permission("can_view_system_info"):
            return "Permission denied: Cannot view system info / अनुमति नहीं है: System info नहीं देख सकते"
        
        try:
            scan_results = self.scanner.full_system_scan()
            
            if 'error' in scan_results:
                return f"Cannot get system info: {scan_results['error']}"
            
            basic_info = scan_results.get('basic_info', {})
            hardware = scan_results.get('hardware', {})
            
            response = "🖥️ System Information / सिस्टम जानकारी:\n\n"
            response += f"Platform: {basic_info.get('platform', 'Unknown')}\n"
            response += f"Hostname: {basic_info.get('hostname', 'Unknown')}\n"
            response += f"Uptime: {basic_info.get('uptime', 'Unknown')}\n\n"
            
            if 'cpu' in hardware:
                cpu = hardware['cpu']
                response += f"CPU Cores: {cpu.get('total_cores', 'Unknown')}\n"
                response += f"CPU Usage: {cpu.get('cpu_usage', 'Unknown')}%\n"
            
            if 'memory' in hardware:
                memory = hardware['memory']
                response += f"Memory: {memory.get('used', 'Unknown')}GB / {memory.get('total', 'Unknown')}GB ({memory.get('percent', 'Unknown')}%)\n"
            
            return response
            
        except Exception as e:
            return f"System info error: {str(e)}"
    
    def _handle_list_processes(self) -> str:
        """Handle process listing request"""
        if not self._check_permission("can_list_processes"):
            return "Permission denied: Cannot list processes / अनुमति नहीं है: Processes list नहीं कर सकते"
        
        try:
            scan_results = self.scanner.full_system_scan()
            
            if 'error' in scan_results:
                return f"Cannot get process info: {scan_results['error']}"
            
            process_info = scan_results.get('processes', {})
            top_processes = process_info.get('top_processes', [])
            
            response = f"🔄 Running Processes / चल रही प्रक्रियाएं:\n\n"
            response += f"Total processes: {process_info.get('total_processes', 'Unknown')}\n\n"
            response += "Top processes by CPU usage:\n"
            
            for i, proc in enumerate(top_processes[:10], 1):
                name = proc.get('name', 'Unknown')
                pid = proc.get('pid', 'Unknown')
                cpu = proc.get('cpu_percent', 0)
                memory = proc.get('memory_mb', 0)
                response += f"{i}. {name} (PID: {pid}) - CPU: {cpu}%, Memory: {memory}MB\n"
            
            return response
            
        except Exception as e:
            return f"Process list error: {str(e)}"
    
    def _handle_open_app(self, app_name: str) -> str:
        """Handle app opening request"""
        if not self._check_permission("can_open_apps"):
            return "Permission denied: Cannot open applications / अनुमति नहीं है: Applications नहीं खोल सकते"
        
        if not app_name:
            return "Please specify which application to open / कृपया बताएं कि कौन सा application खोलना है"
        
        try:
            # Common application mappings
            app_mappings = {
                # Windows applications
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'paint': 'mspaint.exe',
                'cmd': 'cmd.exe',
                'command prompt': 'cmd.exe',
                'powershell': 'powershell.exe',
                'explorer': 'explorer.exe',
                'file explorer': 'explorer.exe',
                'task manager': 'taskmgr.exe',
                'control panel': 'control.exe',
                'registry editor': 'regedit.exe',
                'system info': 'msinfo32.exe',
                'device manager': 'devmgmt.msc',
                'services': 'services.msc',
                'event viewer': 'eventvwr.msc',
                
                # Cross-platform applications
                'chrome': 'chrome' if platform.system() != 'Windows' else 'chrome.exe',
                'firefox': 'firefox' if platform.system() != 'Windows' else 'firefox.exe',
                'edge': 'msedge.exe' if platform.system() == 'Windows' else 'microsoft-edge',
                'code': 'code',
                'vscode': 'code',
                'visual studio code': 'code',
                
                # Linux applications
                'gedit': 'gedit',
                'terminal': 'gnome-terminal' if platform.system() == 'Linux' else 'cmd.exe',
                'file manager': 'nautilus' if platform.system() == 'Linux' else 'explorer.exe',
                'system monitor': 'gnome-system-monitor' if platform.system() == 'Linux' else 'taskmgr.exe',
            }
            
            # Normalize app name
            app_name_lower = app_name.lower().strip()
            
            # Find the executable
            executable = None
            if app_name_lower in app_mappings:
                executable = app_mappings[app_name_lower]
            else:
                # Try direct execution
                executable = app_name
            
            # Attempt to launch the application
            if platform.system() == 'Windows':
                # Windows
                try:
                    subprocess.Popen(executable, shell=True)
                    return f"✅ Successfully opened '{app_name}' / '{app_name}' सफलतापूर्वक खोला गया"
                except Exception as e:
                    # Try with start command
                    try:
                        subprocess.Popen(f'start {executable}', shell=True)
                        return f"✅ Successfully opened '{app_name}' / '{app_name}' सफलतापूर्वक खोला गया"
                    except:
                        return f"❌ Failed to open '{app_name}': {str(e)} / '{app_name}' खोलने में असफल"
            else:
                # Linux/Mac
                try:
                    subprocess.Popen([executable])
                    return f"✅ Successfully opened '{app_name}' / '{app_name}' सफलतापूर्वक खोला गया"
                except Exception as e:
                    return f"❌ Failed to open '{app_name}': {str(e)} / '{app_name}' खोलने में असफल"
                    
        except Exception as e:
            return f"Error opening application: {str(e)} / Application खोलने में त्रुटि"
    
    def _handle_help(self) -> str:
        """Handle help request"""
        return """
🤖 Local AI Assistant Help / सहायता

I understand natural language! Try these commands:

🗣️ Casual Conversation:
• "kya hal h" or "hello" - Just say hi!
• "kaise ho" - Ask how I'm doing

🔍 System Operations:
• "system scan karo" - Full system analysis
• "system ka status batao" - System information
• "running processes dikhao" - Show running processes

📁 File Operations:
• "config files dhundo" - Find configuration files
• "log files dikhao" - Show log files
• "mujhe python files chahiye" - Find Python files

🚀 Application Control:
• "notepad kholo" - Open Notepad
• "calculator open karo" - Open Calculator
• "chrome start karo" - Open Chrome browser
• "file explorer kholo" - Open File Explorer

💡 Smart Features:
• No need for exact paths - I'll find files intelligently
• Supports both English and Hindi
• Natural conversation style

🔐 Security:
• All operations require proper permissions
• Human approval needed for sensitive tasks
• Role-based access control

Just talk to me naturally! / बस मुझसे सामान्य तरीके से बात करें!
        """
    
    def _check_permission(self, permission: str) -> bool:
        """Check if user has permission"""
        role_permissions = {
            'viewer': ['can_view_system_info', 'can_search_files'],
            'operator': ['can_view_system_info', 'can_search_files', 'can_list_processes', 'can_scan_system', 'can_open_apps'],
            'admin': ['can_view_system_info', 'can_search_files', 'can_list_processes', 'can_scan_system', 'can_open_apps', 'can_execute_commands']
        }
        
        user_permissions = role_permissions.get(self.user_role, [])
        return permission in user_permissions
    
    def _format_scan_summary(self, scan_results: Dict[str, Any]) -> str:
        """Format system scan results into a readable summary"""
        try:
            summary = "🔍 System Scan Results / सिस्टम स्कैन परिणाम:\n\n"
            
            # Basic info
            basic_info = scan_results.get('basic_info', {})
            summary += f"🖥️ Platform: {basic_info.get('platform', 'Unknown')}\n"
            summary += f"🏠 Hostname: {basic_info.get('hostname', 'Unknown')}\n"
            summary += f"⏰ Uptime: {basic_info.get('uptime', 'Unknown')}\n\n"
            
            # Hardware summary
            hardware = scan_results.get('hardware', {})
            if 'cpu' in hardware:
                cpu = hardware['cpu']
                summary += f"🔧 CPU: {cpu.get('total_cores', 'Unknown')} cores, {cpu.get('cpu_usage', 'Unknown')}% usage\n"
            
            if 'memory' in hardware:
                memory = hardware['memory']
                summary += f"💾 Memory: {memory.get('used', 'Unknown')}GB / {memory.get('total', 'Unknown')}GB ({memory.get('percent', 'Unknown')}%)\n"
            
            # Process summary
            processes = scan_results.get('processes', {})
            summary += f"🔄 Processes: {processes.get('total_processes', 'Unknown')} running\n"
            
            # Disk summary
            disk_usage = scan_results.get('disk_usage', {})
            if 'partitions' in disk_usage:
                partitions = disk_usage['partitions']
                summary += f"💽 Disk partitions: {len(partitions)} found\n"
                
                for device, info in list(partitions.items())[:3]:  # Show first 3
                    summary += f"   {device}: {info.get('used', 'Unknown')}GB / {info.get('total', 'Unknown')}GB ({info.get('percent', 'Unknown')}%)\n"
            
            # Security summary
            security = scan_results.get('security', {})
            if security:
                summary += f"\n🔐 Security Status:\n"
                summary += f"   Firewall: {security.get('firewall_status', 'Unknown')}\n"
                summary += f"   Antivirus: {security.get('antivirus_status', 'Unknown')}\n"
            
            summary += f"\n📊 Scan completed at: {scan_results.get('timestamp', 'Unknown')}"
            
            return summary
            
        except Exception as e:
            return f"Error formatting scan results: {str(e)}"