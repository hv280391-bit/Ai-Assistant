#!/usr/bin/env python3
"""
Multilingual Local AI Assistant - Main Entry Point
A secure Python-based local AI chatbot assistant supporting multiple languages including Hindi
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config_simple import Config
from auth.manager_simple import AuthManager
from assistant_multilingual import MultilingualAssistant

def main():
    """Start the Multilingual Local AI Assistant"""
    
    # Display banner
    print("=" * 60)
    print("🤖 Local AI Assistant / स्थानीय AI सहायक")
    print("Secure system automation under human control")
    print("मानव नियंत्रण के तहत सुरक्षित सिस्टम स्वचालन")
    print("=" * 60)
    
    try:
        # Load or create configuration
        config = Config("config.json")
        
        # Run setup wizard if needed
        if not config.is_configured():
            print("\nRunning first-time setup... / पहली बार सेटअप चल रहा है...")
            setup_wizard(config)
        
        # Initialize authentication
        auth_manager = AuthManager(config)
        
        # Authenticate user
        if not auth_manager.authenticate():
            print("Authentication failed. Exiting. / Authentication असफल। बाहर निकल रहे हैं।")
            return
        
        # Initialize and start assistant
        assistant = MultilingualAssistant(config, auth_manager)
        assistant.start_chat()
        
    except KeyboardInterrupt:
        print("\nAssistant stopped by user. / Assistant को user ने बंद किया।")
    except Exception as e:
        print(f"Error / त्रुटि: {e}")
        return 1

def setup_wizard(config):
    """Simple setup wizard"""
    print("\n=== First Time Setup / पहली बार सेटअप ===")
    print("This will create your user account and configure the assistant.")
    print("यह आपका user account बनाएगा और assistant को configure करेगा।")
    
    # Basic setup - mark as configured
    config.mark_configured()
    print("Setup completed! You can now create your user account.")
    print("सेटअप पूरा हुआ! अब आप अपना user account बना सकते हैं।")

if __name__ == "__main__":
    main()