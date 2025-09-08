"""
Comprehensive System Scanner for Local AI Assistant
Advanced system analysis and administrative tools
"""

import os
import platform
import psutil
import subprocess
import json
from pathlib import Path
import datetime
from typing import Dict, List, Any

class ComprehensiveSystemScanner:
    """Advanced system scanner with comprehensive analysis capabilities"""
    
    def __init__(self):
        self.system_info = {}
        self.scan_results = {}
    
    def full_system_scan(self) -> Dict[str, Any]:
        """Perform comprehensive system scan"""
        try:
            results = {
                'timestamp': datetime.datetime.now().isoformat(),
                'basic_info': self._get_basic_system_info(),
                'hardware': self._get_hardware_info(),
                'processes': self._get_process_info(),
                'network': self._get_network_info(),
                'disk_usage': self._get_disk_usage(),
                'security': self._get_security_status(),
                'services': self._get_system_services(),
            }
            
            self.scan_results = results
            return results
            
        except Exception as e:
            return {'error': f'System scan failed: {str(e)}'}
    
    def _get_basic_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        try:
            return {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'hostname': platform.node(),
                'python_version': platform.python_version(),
                'uptime': self._get_uptime(),
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information"""
        try:
            # CPU Info
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'total_cores': psutil.cpu_count(logical=True),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'cpu_usage': psutil.cpu_percent(interval=1),
                'cpu_per_core': psutil.cpu_percent(percpu=True, interval=1)
            }
            
            # Memory Info
            memory = psutil.virtual_memory()
            memory_info = {
                'total': self._bytes_to_gb(memory.total),
                'available': self._bytes_to_gb(memory.available),
                'percent': memory.percent,
                'used': self._bytes_to_gb(memory.used),
                'free': self._bytes_to_gb(memory.free)
            }
            
            # Swap Info
            swap = psutil.swap_memory()
            swap_info = {
                'total': self._bytes_to_gb(swap.total),
                'used': self._bytes_to_gb(swap.used),
                'free': self._bytes_to_gb(swap.free),
                'percent': swap.percent
            }
            
            return {
                'cpu': cpu_info,
                'memory': memory_info,
                'swap': swap_info,
                'boot_time': datetime.datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_process_info(self) -> Dict[str, Any]:
        """Get running processes information"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    proc_info['memory_mb'] = round(proc.memory_info().rss / 1024 / 1024, 2)
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            return {
                'total_processes': len(processes),
                'top_processes': processes[:10],  # Top 10 by CPU
                'process_count_by_status': self._count_processes_by_status()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            # Network interfaces
            interfaces = {}
            for interface, addrs in psutil.net_if_addrs().items():
                interfaces[interface] = []
                for addr in addrs:
                    interfaces[interface].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
            
            # Network statistics
            net_io = psutil.net_io_counters()
            net_stats = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
            
            return {
                'interfaces': interfaces,
                'statistics': net_stats,
                'connections': len(psutil.net_connections())
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            disk_usage = {}
            
            # Get all disk partitions
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'filesystem': partition.fstype,
                        'total': self._bytes_to_gb(usage.total),
                        'used': self._bytes_to_gb(usage.used),
                        'free': self._bytes_to_gb(usage.free),
                        'percent': round((usage.used / usage.total) * 100, 2)
                    }
                except PermissionError:
                    continue
            
            # Disk I/O statistics
            disk_io = psutil.disk_io_counters()
            io_stats = {
                'read_count': disk_io.read_count,
                'write_count': disk_io.write_count,
                'read_bytes': disk_io.read_bytes,
                'write_bytes': disk_io.write_bytes
            } if disk_io else {}
            
            return {
                'partitions': disk_usage,
                'io_statistics': io_stats
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_security_status(self) -> Dict[str, Any]:
        """Get basic security status"""
        try:
            security_info = {
                'user_accounts': self._get_user_accounts(),
                'firewall_status': self._check_firewall_status(),
                'antivirus_status': self._check_antivirus_status(),
                'system_updates': self._check_system_updates()
            }
            
            return security_info
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_system_services(self) -> Dict[str, Any]:
        """Get system services information"""
        try:
            if platform.system() == 'Windows':
                return self._get_windows_services()
            else:
                return self._get_unix_services()
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_windows_services(self) -> Dict[str, Any]:
        """Get Windows services"""
        try:
            result = subprocess.run(['sc', 'query'], capture_output=True, text=True, timeout=10)
            services = []
            
            if result.returncode == 0:
                # Parse sc query output
                lines = result.stdout.split('\n')
                current_service = {}
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('SERVICE_NAME:'):
                        if current_service:
                            services.append(current_service)
                        current_service = {'name': line.split(':', 1)[1].strip()}
                    elif line.startswith('STATE:') and current_service:
                        current_service['state'] = line.split(':', 1)[1].strip()
                
                if current_service:
                    services.append(current_service)
            
            return {
                'total_services': len(services),
                'services': services[:20]  # Limit to first 20
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_unix_services(self) -> Dict[str, Any]:
        """Get Unix/Linux services"""
        try:
            # Try systemctl first
            try:
                result = subprocess.run(['systemctl', 'list-units', '--type=service'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')[1:]  # Skip header
                    services = []
                    
                    for line in lines:
                        if line.strip() and not line.startswith('●'):
                            parts = line.split()
                            if len(parts) >= 4:
                                services.append({
                                    'name': parts[0],
                                    'load': parts[1],
                                    'active': parts[2],
                                    'sub': parts[3]
                                })
                    
                    return {
                        'total_services': len(services),
                        'services': services[:20]
                    }
            except FileNotFoundError:
                pass
            
            # Fallback to ps
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')[1:]  # Skip header
                return {
                    'total_processes': len(lines),
                    'note': 'Service list not available, showing process count'
                }
            
            return {'error': 'Unable to retrieve service information'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.datetime.now().timestamp() - boot_time
            
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return f"{days} days, {hours} hours, {minutes} minutes"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _bytes_to_gb(self, bytes_value: int) -> float:
        """Convert bytes to GB"""
        return round(bytes_value / (1024**3), 2)
    
    def _count_processes_by_status(self) -> Dict[str, int]:
        """Count processes by status"""
        try:
            status_count = {}
            for proc in psutil.process_iter(['status']):
                try:
                    status = proc.info['status']
                    status_count[status] = status_count.get(status, 0) + 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return status_count
        except Exception:
            return {}
    
    def _get_user_accounts(self) -> List[str]:
        """Get user accounts"""
        try:
            users = [user.name for user in psutil.users()]
            return list(set(users))  # Remove duplicates
        except Exception:
            return []
    
    def _check_firewall_status(self) -> str:
        """Check firewall status"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return "Firewall information available" if "ON" in result.stdout else "Firewall may be disabled"
            else:
                # Check for common Linux firewalls
                for fw in ['ufw', 'iptables', 'firewalld']:
                    try:
                        subprocess.run(['which', fw], capture_output=True, timeout=2)
                        return f"{fw} detected"
                    except:
                        continue
            
            return "Firewall status unknown"
            
        except Exception:
            return "Unable to check firewall status"
    
    def _check_antivirus_status(self) -> str:
        """Check antivirus status"""
        try:
            if platform.system() == 'Windows':
                # Check Windows Defender
                result = subprocess.run(['powershell', 'Get-MpComputerStatus'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return "Windows Defender information available"
            
            return "Antivirus status check not implemented for this system"
            
        except Exception:
            return "Unable to check antivirus status"
    
    def _check_system_updates(self) -> str:
        """Check system updates"""
        try:
            if platform.system() == 'Windows':
                return "Windows Update check requires elevated privileges"
            else:
                # Check for package managers
                for pm in ['apt', 'yum', 'dnf', 'pacman']:
                    try:
                        subprocess.run(['which', pm], capture_output=True, timeout=2, check=True)
                        return f"Package manager {pm} detected - updates can be checked"
                    except:
                        continue
            
            return "No supported package manager found"
            
        except Exception:
            return "Unable to check system updates"
    
    def smart_file_search(self, query: str, base_path: str = None) -> List[str]:
        """Smart file search without requiring exact paths"""
        try:
            if base_path is None:
                base_path = str(Path.home())
            
            results = []
            search_paths = [base_path]
            
            # Add common system paths based on query
            if 'config' in query.lower():
                if platform.system() == 'Windows':
                    search_paths.extend([
                        os.path.expandvars('%APPDATA%'),
                        os.path.expandvars('%PROGRAMDATA%'),
                        'C:\\Windows\\System32\\config'
                    ])
                else:
                    search_paths.extend(['/etc', '~/.config', '~/.local/config'])
            
            if 'log' in query.lower():
                if platform.system() == 'Windows':
                    search_paths.extend([
                        'C:\\Windows\\Logs',
                        os.path.expandvars('%TEMP%')
                    ])
                else:
                    search_paths.extend(['/var/log', '~/.local/share/logs'])
            
            # Search for files
            for search_path in search_paths:
                try:
                    path_obj = Path(search_path).expanduser()
                    if path_obj.exists():
                        # Use different patterns based on query
                        patterns = self._generate_search_patterns(query)
                        
                        for pattern in patterns:
                            for file_path in path_obj.rglob(pattern):
                                if file_path.is_file() and len(results) < 20:
                                    results.append(str(file_path))
                except (PermissionError, OSError):
                    continue
            
            return results[:20]  # Limit results
            
        except Exception as e:
            return [f"Search error: {str(e)}"]
    
    def _generate_search_patterns(self, query: str) -> List[str]:
        """Generate search patterns based on query"""
        patterns = []
        query_lower = query.lower()
        
        # Direct pattern
        patterns.append(f"*{query}*")
        
        # Common file extensions based on query
        if 'config' in query_lower:
            patterns.extend(['*.conf', '*.cfg', '*.ini', '*.json', '*.xml', '*.yaml', '*.yml'])
        
        if 'log' in query_lower:
            patterns.extend(['*.log', '*.txt'])
        
        if 'script' in query_lower:
            patterns.extend(['*.py', '*.sh', '*.bat', '*.ps1'])
        
        if 'document' in query_lower:
            patterns.extend(['*.doc', '*.docx', '*.pdf', '*.txt'])
        
        return patterns