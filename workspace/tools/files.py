"""
File operation tools
"""

import os
from pathlib import Path
from typing import Dict, Any, List
import mimetypes

from .base import BaseTool

class SearchFilesTool(BaseTool):
    """Tool for searching files"""
    
    def get_required_permission(self) -> str:
        return "can_search_files"
    
    def execute(self, query: str, base: str = None, max_results: int = None) -> Dict[str, Any]:
        """Search for files matching query"""
        try:
            if max_results is None:
                max_results = self.config.data.get("max_search_results", 100)
            
            # Determine search base
            if base is None:
                search_bases = self.config.allowlisted_paths
            else:
                base_path = Path(base).resolve()
                # Check if base is in allowlisted paths
                if not any(str(base_path).startswith(allowed) for allowed in self.config.allowlisted_paths):
                    return {"error": f"Access denied to path: {base}"}
                search_bases = [str(base_path)]
            
            results = []
            query_lower = query.lower()
            
            for search_base in search_bases:
                if not os.path.exists(search_base):
                    continue
                
                for root, dirs, files in os.walk(search_base):
                    # Skip hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for file in files:
                        if query_lower in file.lower():
                            file_path = os.path.join(root, file)
                            file_stat = os.stat(file_path)
                            results.append({
                                "path": file_path,
                                "name": file,
                                "size": file_stat.st_size,
                                "modified": file_stat.st_mtime
                            })
                            
                            if len(results) >= max_results:
                                break
                    
                    if len(results) >= max_results:
                        break
            
            self.log_execution({"query": query, "base": base}, {"success": f"Found {len(results)} files"})
            
            return {
                "success": f"Found {len(results)} files matching '{query}'",
                "data": results
            }
            
        except Exception as e:
            error_result = {"error": str(e)}
            self.log_execution({"query": query, "base": base}, error_result)
            return error_result

class ReadTextFileTool(BaseTool):
    """Tool for reading text files"""
    
    def get_required_permission(self) -> str:
        return "can_read_files"
    
    def execute(self, path: str, max_bytes: int = None) -> Dict[str, Any]:
        """Read text file contents"""
        try:
            file_path = Path(path).resolve()
            
            # Check if path is in allowlisted directories
            if not any(str(file_path).startswith(allowed) for allowed in self.config.allowlisted_paths):
                return {"error": f"Access denied to path: {path}"}
            
            # Check if file exists
            if not file_path.exists():
                return {"error": f"File not found: {path}"}
            
            # Check file size
            if max_bytes is None:
                max_bytes = self.config.data.get("max_file_size_mb", 10) * 1024 * 1024
            
            file_size = file_path.stat().st_size
            if file_size > max_bytes:
                return {"error": f"File too large: {file_size} bytes (max: {max_bytes})"}
            
            # Check if file is text-based
            mime_type, _ = mimetypes.guess_type(str(file_path))
            text_types = ['text/', 'application/json', 'application/xml', 'application/javascript']
            
            if mime_type and not any(mime_type.startswith(t) for t in text_types):
                return {"error": f"File type not supported: {mime_type}"}
            
            # Read file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            self.log_execution({"path": path}, {"success": f"Read {len(content)} characters"})
            
            return {
                "success": f"Read file: {path}",
                "data": {
                    "path": str(file_path),
                    "size": file_size,
                    "content": content
                }
            }
            
        except Exception as e:
            error_result = {"error": str(e)}
            self.log_execution({"path": path}, error_result)
            return error_result