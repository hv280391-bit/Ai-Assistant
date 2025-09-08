"""
Web reading tool
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
from urllib.parse import urlparse

from .base import BaseTool

class ReadWebpageTool(BaseTool):
    """Tool for reading webpage content"""
    
    def get_required_permission(self) -> str:
        return "can_read_web"
    
    def execute(self, url: str, max_chars: int = 5000) -> Dict[str, Any]:
        """Read and extract text content from a webpage"""
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {"error": "Invalid URL format"}
            
            # Set headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Fetch the webpage
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Truncate if too long
            if len(text) > max_chars:
                text = text[:max_chars] + "... [truncated]"
            
            # Extract metadata
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"
            
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ''
            
            result_data = {
                "url": url,
                "title": title_text,
                "description": description,
                "content": text,
                "content_length": len(text),
                "status_code": response.status_code
            }
            
            self.log_execution({"url": url}, {"success": f"Read {len(text)} characters"})
            
            return {
                "success": f"Successfully read webpage: {title_text}",
                "data": result_data
            }
            
        except requests.exceptions.RequestException as e:
            error_result = {"error": f"Network error: {str(e)}"}
            self.log_execution({"url": url}, error_result)
            return error_result
        
        except Exception as e:
            error_result = {"error": str(e)}
            self.log_execution({"url": url}, error_result)
            return error_result