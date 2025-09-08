"""
Process management tools
"""

import psutil
from typing import Dict, Any, List

from .base import BaseTool

class ListProcessesTool(BaseTool):
    """Tool for listing running processes"""
    
    def get_required_permission(self) -> str:
        return "can_list_processes"
    
    def execute(self, limit: int = 20) -> Dict[str, Any]:
        """List running processes with CPU and memory usage"""
        try:
            processes = []
            
            # Get all processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    proc_info['cpu_percent'] = proc.cpu_percent()
                    proc_info['memory_percent'] = proc.memory_percent()
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort by CPU usage (descending)
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            # Limit results
            processes = processes[:limit]
            
            # Format for display
            formatted_processes = []
            for proc in processes:
                formatted_processes.append({
                    "pid": proc.get('pid', 'N/A'),
                    "name": proc.get('name', 'N/A'),
                    "cpu_percent": f"{proc.get('cpu_percent', 0):.1f}%",
                    "memory_percent": f"{proc.get('memory_percent', 0):.1f}%",
                    "status": proc.get('status', 'N/A')
                })
            
            # Get system stats
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            result_data = {
                "system_stats": {
                    "cpu_usage": f"{cpu_usage:.1f}%",
                    "memory_usage": f"{memory.percent:.1f}%",
                    "memory_available": f"{memory.available / (1024**3):.1f} GB"
                },
                "processes": formatted_processes,
                "total_processes": len(processes)
            }
            
            self.log_execution({"limit": limit}, {"success": f"Listed {len(processes)} processes"})
            
            return {
                "success": f"Listed top {len(processes)} processes by CPU usage",
                "data": result_data
            }
            
        except Exception as e:
            error_result = {"error": str(e)}
            self.log_execution({"limit": limit}, error_result)
            return error_result