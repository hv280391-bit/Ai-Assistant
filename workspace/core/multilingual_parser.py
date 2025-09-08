"""
Multilingual command parser for Local AI Assistant
Supports English, Hindi, and other languages
"""

import re
from typing import Optional, Dict, Any

class MultilingualParser:
    """Enhanced parser supporting multiple languages"""
    
    def __init__(self):
        # Language patterns for different commands
        self.patterns = {
            # File search patterns
            'search_files': {
                'english': [
                    r'(?:find|search|locate|show)\s+(.+?)\s+(?:in|under|from)\s+(.+)',
                    r'(?:find|search|locate|show)\s+(.+)',
                    r'list\s+(?:all\s+)?files?\s+(?:in|from)\s+(.+)',
                ],
                'hindi': [
                    r'(?:dhundo|khojo|dikhao|batao)\s+(.+?)\s+(?:mein|me|se)\s+(.+)',
                    r'(?:dhundo|khojo|dikhao|batao)\s+(.+)',
                    r'(?:sabhi|sari)\s+files?\s+(?:dikhao|batao)\s+(.+)',
                    r'(.+)\s+(?:ki|ke)\s+(?:sabhi|sari)\s+files?\s+(?:dikhao|batao)',
                    r'system\s+(?:ki|ke)\s+(?:sabhi|sari)\s+(?:imp|important|zaroori)\s+files?\s+(?:dikhao|batao)',
                ]
            },
            
            # File read patterns  
            'read_file': {
                'english': [
                    r'(?:read|open|show|cat|display)\s+(.+)',
                    r'what(?:\'s|\s+is)\s+(?:in|inside)\s+(.+)',
                ],
                'hindi': [
                    r'(?:padho|kholo|dikhao|batao)\s+(.+)',
                    r'(.+)\s+(?:ko|ka)\s+(?:content|data|padho|dikhao)',
                    r'(.+)\s+(?:file|mein)\s+(?:kya|kya hai)',
                ]
            },
            
            # Process list patterns
            'list_processes': {
                'english': [
                    r'(?:list|show|display)\s+(?:all\s+)?(?:running\s+)?processes',
                    r'what(?:\'s|\s+is)\s+running',
                    r'show\s+(?:me\s+)?(?:all\s+)?(?:running\s+)?(?:programs|apps)',
                ],
                'hindi': [
                    r'(?:sabhi|sari)\s+(?:running|chal rahi|chalti)\s+(?:processes|programs)\s+(?:dikhao|batao)',
                    r'(?:kya|kaun si)\s+(?:processes|programs)\s+(?:chal rahi|running)\s+(?:hai|hain)',
                    r'system\s+(?:mein|me)\s+(?:kya|kaun)\s+(?:chal raha|running)\s+(?:hai|he)',
                    r'(?:running|chalti)\s+(?:processes|programs)\s+(?:list|dikhao|batao)',
                ]
            },
            
            # App launch patterns
            'open_app': {
                'english': [
                    r'(?:open|launch|start|run)\s+(.+)',
                    r'(?:can\s+you\s+)?(?:please\s+)?(?:open|launch|start)\s+(.+)',
                ],
                'hindi': [
                    r'(?:kholo|chalu karo|start karo|run karo)\s+(.+)',
                    r'(.+)\s+(?:ko|kholo|chalu karo)',
                    r'(?:kya\s+)?(.+)\s+(?:khol sakte ho|chalu kar sakte ho)',
                ]
            }
        }
        
        # Common Hindi-English word mappings
        self.translations = {
            'bhai': '',  # Remove casual address
            'yaar': '',
            'dost': '',
            'system': 'system',
            'sabhi': 'all',
            'sari': 'all', 
            'imp': 'important',
            'important': 'important',
            'zaroori': 'important',
            'files': 'files',
            'file': 'file',
            'dikhao': 'show',
            'batao': 'show',
            'dhundo': 'find',
            'khojo': 'find',
            'padho': 'read',
            'kholo': 'open',
            'chalu': 'start',
            'karo': '',
            'processes': 'processes',
            'programs': 'programs',
            'chal': 'running',
            'running': 'running',
            'rahi': 'running',
            'hai': 'is',
            'hain': 'are',
            'mein': 'in',
            'me': 'in',
            'ki': 'of',
            'ke': 'of',
            'ka': 'of',
            'ko': '',
            'se': 'from'
        }
    
    def parse_command(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse command in multiple languages"""
        text = text.strip().lower()
        
        # Remove casual addresses
        text = self._clean_text(text)
        
        # Try to parse in different languages
        result = self._try_parse_hindi(text)
        if result:
            return result
            
        result = self._try_parse_english(text)
        if result:
            return result
            
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove casual addresses and common filler words
        for word in ['bhai', 'yaar', 'dost', 'please', 'kya']:
            text = re.sub(r'\b' + word + r'\b', '', text)
        
        # Clean extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _try_parse_hindi(self, text: str) -> Optional[Dict[str, Any]]:
        """Try to parse Hindi commands"""
        
        # File search in Hindi
        for pattern in self.patterns['search_files']['hindi']:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    return {"tool": "search_files", "args": {"query": match.group(1).strip(), "base": self._translate_path(match.group(2).strip())}}
                else:
                    query = match.group(1).strip()
                    # Special handling for system files
                    if 'system' in text and ('imp' in text or 'important' in text or 'zaroori' in text):
                        return {"tool": "search_files", "args": {"query": "*.conf *.cfg *.ini *.json *.xml", "base": "/etc"}}
                    return {"tool": "search_files", "args": {"query": query}}
        
        # File read in Hindi
        for pattern in self.patterns['read_file']['hindi']:
            match = re.search(pattern, text)
            if match:
                return {"tool": "read_file", "args": {"path": match.group(1).strip()}}
        
        # Process list in Hindi
        for pattern in self.patterns['list_processes']['hindi']:
            if re.search(pattern, text):
                return {"tool": "list_processes", "args": {}}
        
        # App launch in Hindi
        for pattern in self.patterns['open_app']['hindi']:
            match = re.search(pattern, text)
            if match:
                app_name = self._translate_app_name(match.group(1).strip())
                return {"tool": "open_app", "args": {"name": app_name}}
        
        return None
    
    def _try_parse_english(self, text: str) -> Optional[Dict[str, Any]]:
        """Try to parse English commands"""
        
        # File search in English
        for pattern in self.patterns['search_files']['english']:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    return {"tool": "search_files", "args": {"query": match.group(1).strip(), "base": match.group(2).strip()}}
                else:
                    return {"tool": "search_files", "args": {"query": match.group(1).strip()}}
        
        # File read in English
        for pattern in self.patterns['read_file']['english']:
            match = re.search(pattern, text)
            if match:
                return {"tool": "read_file", "args": {"path": match.group(1).strip()}}
        
        # Process list in English
        for pattern in self.patterns['list_processes']['english']:
            if re.search(pattern, text):
                return {"tool": "list_processes", "args": {}}
        
        # App launch in English
        for pattern in self.patterns['open_app']['english']:
            match = re.search(pattern, text)
            if match:
                return {"tool": "open_app", "args": {"name": match.group(1).strip()}}
        
        return None
    
    def _translate_path(self, path: str) -> str:
        """Translate Hindi path references to actual paths"""
        path_mappings = {
            'ghar': '~',
            'home': '~',
            'desktop': '~/Desktop',
            'documents': '~/Documents',
            'downloads': '~/Downloads',
            'system': '/etc',
            'root': '/',
        }
        
        for hindi, english in path_mappings.items():
            if hindi in path:
                return english
        
        return path
    
    def _translate_app_name(self, app: str) -> str:
        """Translate Hindi app names to English"""
        app_mappings = {
            'notepad': 'notepad',
            'calculator': 'calc',
            'browser': 'firefox',
            'chrome': 'chrome',
            'firefox': 'firefox',
            'calc': 'calc',
            'text editor': 'notepad',
        }
        
        return app_mappings.get(app, app)
    
    def get_help_text(self, language='english') -> str:
        """Get help text in specified language"""
        if language == 'hindi':
            return """
=== Local AI Assistant Commands (Hindi) ===

File Operations:
• "system ki sabhi imp files dikhao" - Important files dikhayega
• "config.txt dhundo home folder mein" - Files search karega
• "readme file padho" - File content dikhayega

System Operations:
• "sabhi running processes dikhao" - Running processes list karega
• "system mein kya chal raha hai" - Active processes dikhayega

App Operations:
• "notepad kholo" - Notepad launch karega
• "calculator chalu karo" - Calculator start karega

General:
• "help" - Ye help dikhayega
• "quit" - Assistant band kar dega

Examples:
• "bhai system ki sabhi zaroori files dikhao"
• "documents folder mein python files dhundo"
• "config file ko padho"
• "chrome browser kholo"
            """
        else:
            return """
=== Local AI Assistant Commands (English) ===

File Operations:
• "find config.txt in home folder" - Search for files
• "read readme file" - Read file contents
• "show all important files in system" - List system files

System Operations:
• "list all running processes" - Show running processes
• "what's running on my system" - Show active processes

App Operations:
• "open notepad" - Launch notepad
• "start calculator" - Launch calculator

General:
• "help" - Show this help
• "quit" - Exit assistant
            """