"""
Enhanced Natural Language Parser for Local AI Assistant
Supports casual conversation and complex command parsing in multiple languages
"""

import re
from typing import Dict, Any, Optional, List

class EnhancedNaturalLanguageParser:
    """Advanced natural language parser with multi-language support"""
    
    def __init__(self):
        self.casual_patterns = self._setup_casual_patterns()
        self.command_patterns = self._setup_command_patterns()
        self.app_patterns = self._setup_app_patterns()
    
    def _setup_casual_patterns(self) -> Dict[str, List[str]]:
        """Setup patterns for casual conversation"""
        return {
            'greetings': [
                r'\b(hello|hi|hey|kya hal h|kya haal hai|namaste|namaskar)\b',
                r'\b(good morning|good afternoon|good evening|subah|shaam)\b',
                r'\b(sup|wassup|what\'s up)\b'
            ],
            'how_are_you': [
                r'\b(how are you|kaise ho|kaisi ho|kya haal|how\'s it going)\b',
                r'\b(what\'s up|kya chal raha|kya kar rahe|all good)\b'
            ],
            'thanks': [
                r'\b(thank you|thanks|dhanyawad|shukriya|thx)\b',
                r'\b(appreciate|grateful|meherbani)\b'
            ],
            'goodbye': [
                r'\b(bye|goodbye|see you|alvida|chalta hun|ja raha)\b',
                r'\b(take care|khyal rakhna|milte hain)\b'
            ]
        }
    
    def _setup_command_patterns(self) -> Dict[str, List[str]]:
        """Setup patterns for system commands"""
        return {
            'system_scan': [
                r'\b(system scan|scan system|system check|check system)\b',
                r'\b(system scan karo|scan karo|system dekho|check karo)\b',
                r'\b(full scan|complete scan|pura scan)\b'
            ],
            'system_info': [
                r'\b(system info|system information|system status|system ka status)\b',
                r'\b(system details|computer info|pc info|laptop info)\b',
                r'\b(hardware info|system specs|configuration)\b'
            ],
            'find_files': [
                r'\b(find files?|search files?|locate files?|files? dhundo)\b',
                r'\b(files? chahiye|files? dikhao|files? batao)\b',
                r'\b(where (?:are|is) .+ files?|kahan hai .+ files?)\b'
            ],
            'list_processes': [
                r'\b(list processes|show processes|running processes|processes dikhao)\b',
                r'\b(what\'s running|kya chal raha|active processes)\b',
                r'\b(task manager|process list|running programs)\b'
            ],
            'open_app': [
                r'\b(open|start|launch|run|kholo|chalu karo|start karo)\b.+\b(app|application|program|software)\b',
                r'\b(open|start|launch|kholo|chalu karo)\s+(\w+)',
                r'\b(\w+)\s+(kholo|open karo|start karo|chalu karo)\b'
            ]
        }
    
    def _setup_app_patterns(self) -> Dict[str, List[str]]:
        """Setup patterns for application names"""
        return {
            'notepad': [r'\b(notepad|text editor|editor)\b'],
            'calculator': [r'\b(calculator|calc|गणक)\b'],
            'chrome': [r'\b(chrome|google chrome|browser)\b'],
            'firefox': [r'\b(firefox|mozilla)\b'],
            'edge': [r'\b(edge|microsoft edge)\b'],
            'explorer': [r'\b(explorer|file explorer|files|folder)\b'],
            'cmd': [r'\b(cmd|command prompt|terminal|console)\b'],
            'powershell': [r'\b(powershell|power shell|ps)\b'],
            'paint': [r'\b(paint|mspaint|drawing)\b'],
            'task manager': [r'\b(task manager|taskmgr|processes)\b'],
            'control panel': [r'\b(control panel|settings|control)\b'],
            'code': [r'\b(code|vscode|visual studio code|vs code)\b']
        }
    
    def parse_command(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse natural language text into structured commands"""
        text = text.lower().strip()
        
        # Check for casual conversation first
        if self._is_casual_conversation(text):
            return {
                "tool": "casual_response",
                "args": {"text": text}
            }
        
        # Check for system commands
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    if command_type == 'find_files':
                        # Extract file type or query
                        query = self._extract_file_query(text)
                        return {
                            "tool": "find_files",
                            "args": {"query": query}
                        }
                    elif command_type == 'open_app':
                        # Extract app name
                        app_name = self._extract_app_name(text)
                        return {
                            "tool": "open_app",
                            "args": {"app_name": app_name}
                        }
                    else:
                        return {
                            "tool": command_type,
                            "args": {}
                        }
        
        # Check for help requests
        if any(word in text for word in ['help', 'madad', 'sahayata', 'commands', 'what can you do']):
            return {
                "tool": "help",
                "args": {}
            }
        
        return None
    
    def _is_casual_conversation(self, text: str) -> bool:
        """Check if text is casual conversation"""
        for category, patterns in self.casual_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
        return False
    
    def _extract_file_query(self, text: str) -> str:
        """Extract file search query from text"""
        # Common file type patterns
        file_patterns = {
            r'\b(config|configuration)\b': 'config',
            r'\b(log|logs)\b': 'log',
            r'\b(python|py)\b': 'python',
            r'\b(javascript|js)\b': 'javascript',
            r'\b(html|web)\b': 'html',
            r'\b(css|style)\b': 'css',
            r'\b(json|data)\b': 'json',
            r'\b(txt|text)\b': 'txt',
            r'\b(pdf|document)\b': 'pdf',
            r'\b(image|img|photo|picture)\b': 'image',
            r'\b(video|movie|mp4)\b': 'video',
            r'\b(audio|music|mp3)\b': 'audio'
        }
        
        for pattern, query in file_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return query
        
        # Extract quoted strings or specific terms
        quoted = re.search(r'"([^"]+)"', text)
        if quoted:
            return quoted.group(1)
        
        # Default to generic file search
        return "files"
    
    def _extract_app_name(self, text: str) -> str:
        """Extract application name from text"""
        # Check for specific app patterns
        for app_name, patterns in self.app_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return app_name
        
        # Try to extract app name from common command structures
        patterns = [
            r'\b(?:open|start|launch|kholo|chalu karo)\s+([a-zA-Z]+)',
            r'\b([a-zA-Z]+)\s+(?:kholo|open karo|start karo|chalu karo)\b',
            r'\b(?:open|start|launch)\s+([a-zA-Z\s]+?)(?:\s+(?:app|application|program))?$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                app_name = match.group(1).strip()
                if app_name and len(app_name) > 1:
                    return app_name
        
        return "unknown"
    
    def get_casual_response(self, text: str) -> str:
        """Generate appropriate casual response"""
        text = text.lower()
        
        # Greetings
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in self.casual_patterns['greetings']):
            responses = [
                "Hello! How can I help you today? / नमस्ते! आज मैं आपकी कैसे मदद कर सकता हूं?",
                "Hi there! Ready to assist you! / हैलो! आपकी सहायता के लिए तैयार हूं!",
                "Namaste! What would you like me to do? / नमस्ते! आप क्या करवाना चाहते हैं?"
            ]
            return responses[hash(text) % len(responses)]
        
        # How are you
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in self.casual_patterns['how_are_you']):
            responses = [
                "I'm doing great, thanks for asking! How can I help? / मैं बहुत अच्छा हूं, पूछने के लिए धन्यवाद! कैसे मदद करूं?",
                "All systems running smoothly! What do you need? / सभी सिस्टम ठीक चल रहे हैं! आपको क्या चाहिए?",
                "Sab badhiya hai! Ready to help you! / सब बढ़िया है! आपकी मदद के लिए तैयार हूं!"
            ]
            return responses[hash(text) % len(responses)]
        
        # Thanks
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in self.casual_patterns['thanks']):
            responses = [
                "You're welcome! Happy to help! / आपका स्वागत है! खुशी से मदद की!",
                "No problem at all! / कोई समस्या नहीं!",
                "Glad I could help! / खुशी है कि मदद कर सका!"
            ]
            return responses[hash(text) % len(responses)]
        
        # Goodbye
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in self.casual_patterns['goodbye']):
            responses = [
                "Goodbye! Take care! / अलविदा! ख्याल रखना!",
                "See you later! / फिर मिलेंगे!",
                "Bye! Feel free to come back anytime! / बाय! कभी भी वापस आ सकते हैं!"
            ]
            return responses[hash(text) % len(responses)]
        
        # Default casual response
        return "I understand you're being casual! How can I assist you today? / समझ गया! आज कैसे मदद करूं?"