#!/usr/bin/env python3
"""
Startup script for Enhanced Local AI Assistant
"""

import sys
import time
import webbrowser
import threading
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def open_browser_delayed(url, delay=2):
    """Open browser after a delay"""
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except:
        pass

def main():
    try:
        # Import the complete web assistant
        from complete_web_assistant import start_server
        
        port = 8080
        url = f"http://localhost:{port}"
        
        print("🚀 Starting Enhanced Local AI Assistant...")
        print("=" * 60)
        print(f"🌐 Server will be available at: {url}")
        print(f"🔐 Features:")
        print(f"   • Secure authentication with sign up/sign in")
        print(f"   • Persistent sessions (no more 'session expired')")
        print(f"   • Natural language understanding (English & Hindi)")
        print(f"   • Comprehensive system scanner")
        print(f"   • Smart file search without exact paths")
        print(f"   • Role-based access control")
        print(f"   • Professional, clean UI")
        print("=" * 60)
        
        # Open browser automatically after server starts
        browser_thread = threading.Thread(target=open_browser_delayed, args=(url, 3))
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start the server
        start_server(port)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Installing required dependencies...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_enhanced.txt"])
        print("✅ Dependencies installed. Please run the script again.")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    main()