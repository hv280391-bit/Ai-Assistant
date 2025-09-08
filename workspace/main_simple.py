#!/usr/bin/env python3
"""
Local AI Assistant - Simplified Main Entry Point
A secure Python-based local AI chatbot assistant using only standard library.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config_simple import Config
from auth.manager_simple import AuthManager
from assistant_simple import LocalAssistant

def main():
    """Start the Local AI Assistant"""
    
    # Display banner
    print("=" * 50)
    print("🤖 Local AI Assistant")
    print("Secure system automation under human control")
    print("=" * 50)
    
    try:
        # Load or create configuration
        config = Config("config.json")
        
        # Run setup wizard if needed
        if not config.is_configured():
            print("\nRunning first-time setup...")
            setup_wizard(config)
        
        # Initialize authentication
        auth_manager = AuthManager(config)
        
        # Authenticate user
        if not auth_manager.authenticate():
            print("Authentication failed. Exiting.")
            return
        
        # Initialize and start assistant
        assistant = LocalAssistant(config, auth_manager)
        assistant.start_chat()
        
    except KeyboardInterrupt:
        print("\nAssistant stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
        return 1

def setup_wizard(config):
    """Simple setup wizard"""
    print("\n=== First Time Setup ===")
    print("This will create your user account and configure the assistant.")
    
    # Basic setup - mark as configured
    config.mark_configured()
    print("Setup completed! You can now create your user account.")

if __name__ == "__main__":
    main()