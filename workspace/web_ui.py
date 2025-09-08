#!/usr/bin/env python3
"""
Web-based UI for Local AI Assistant
A simple web interface using Python's built-in HTTP server
"""

import http.server
import socketserver
import json
import urllib.parse
import threading
import webbrowser
import time
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config_simple import Config
from auth.manager_simple import AuthManager
from assistant_simple import SimpleTools, CommandParser

class WebUIHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the web UI"""
    
    def __init__(self, *args, **kwargs):
        self.config = Config("config.json")
        self.auth_manager = None
        self.tools = None
        self.parser = CommandParser()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/index.html':
            self.serve_main_page()
        elif self.path == '/login':
            self.serve_login_page()
        elif self.path == '/chat':
            self.serve_chat_page()
        elif self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404)
    
    def serve_main_page(self):
        """Serve the main HTML page"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Local AI Assistant</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            width: 90%;
        }
        .logo { font-size: 3rem; margin-bottom: 1rem; }
        h1 { color: #333; margin-bottom: 0.5rem; }
        .subtitle { color: #666; margin-bottom: 2rem; }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s;
            text-decoration: none;
            display: inline-block;
            margin: 0.5rem;
        }
        .btn:hover { transform: translateY(-2px); }
        .status { margin-top: 1rem; padding: 1rem; background: #f8f9fa; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🤖</div>
        <h1>Local AI Assistant</h1>
        <p class="subtitle">Secure system automation under human control</p>
        
        <div id="status" class="status">
            <p>Checking system status...</p>
        </div>
        
        <a href="/login" class="btn">Start Assistant</a>
        
        <div style="margin-top: 2rem; font-size: 0.9rem; color: #666;">
            <p><strong>Features:</strong></p>
            <p>• File operations with security</p>
            <p>• Process monitoring</p>
            <p>• Application launching</p>
            <p>• Role-based access control</p>
        </div>
    </div>
    
    <script>
        // Check if users exist
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                const status = document.getElementById('status');
                if (data.users_exist) {
                    status.innerHTML = '<p style="color: green;">✓ System ready - Users configured</p>';
                } else {
                    status.innerHTML = '<p style="color: orange;">⚠ First time setup required</p>';
                }
            })
            .catch(error => {
                document.getElementById('status').innerHTML = '<p style="color: red;">✗ System error</p>';
            });
    </script>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_login_page(self):
        """Serve the login page"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Local AI Assistant</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 400px;
            width: 90%;
        }
        .logo { font-size: 2rem; text-align: center; margin-bottom: 1rem; }
        h2 { color: #333; margin-bottom: 1.5rem; text-align: center; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; color: #555; font-weight: 500; }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s;
            width: 100%;
            margin-top: 1rem;
        }
        .btn:hover { transform: translateY(-2px); }
        .message { padding: 1rem; margin: 1rem 0; border-radius: 8px; text-align: center; }
        .error { background: #fee; color: #c33; border: 1px solid #fcc; }
        .success { background: #efe; color: #363; border: 1px solid #cfc; }
        .setup-section { margin-top: 2rem; padding-top: 2rem; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🔐</div>
        <h2>Login to Assistant</h2>
        
        <div id="message"></div>
        
        <div id="loginForm">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" required>
            </div>
            <button class="btn" onclick="login()">Login</button>
        </div>
        
        <div id="setupForm" class="setup-section" style="display: none;">
            <h3 style="text-align: center; color: #333; margin-bottom: 1rem;">Create First User</h3>
            <div class="form-group">
                <label for="newUsername">Username:</label>
                <input type="text" id="newUsername" required>
            </div>
            <div class="form-group">
                <label for="newPassword">Password:</label>
                <input type="password" id="newPassword" required>
            </div>
            <div class="form-group">
                <label for="role">Role:</label>
                <select id="role">
                    <option value="viewer">Viewer - Read-only access</option>
                    <option value="operator" selected>Operator - Can launch apps</option>
                    <option value="admin">Admin - Full access</option>
                </select>
            </div>
            <button class="btn" onclick="createUser()">Create User</button>
        </div>
        
        <div style="text-align: center; margin-top: 1rem;">
            <a href="/" style="color: #667eea; text-decoration: none;">← Back to Home</a>
        </div>
    </div>
    
    <script>
        // Check if setup is needed
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                if (!data.users_exist) {
                    document.getElementById('setupForm').style.display = 'block';
                    document.getElementById('message').innerHTML = 
                        '<div class="message" style="background: #fff3cd; color: #856404; border: 1px solid #ffeaa7;">No users found. Please create the first user account.</div>';
                }
            });
        
        function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            if (!username || !password) {
                showMessage('Please enter username and password', 'error');
                return;
            }
            
            fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/chat';
                } else {
                    showMessage(data.message, 'error');
                }
            })
            .catch(error => {
                showMessage('Login failed', 'error');
            });
        }
        
        function createUser() {
            const username = document.getElementById('newUsername').value;
            const password = document.getElementById('newPassword').value;
            const role = document.getElementById('role').value;
            
            if (!username || !password) {
                showMessage('Please enter username and password', 'error');
                return;
            }
            
            fetch('/api/create-user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password, role })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage('User created successfully! You can now login.', 'success');
                    document.getElementById('setupForm').style.display = 'none';
                    document.getElementById('username').value = username;
                } else {
                    showMessage(data.message, 'error');
                }
            })
            .catch(error => {
                showMessage('Failed to create user', 'error');
            });
        }
        
        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = `<div class="message ${type}">${text}</div>`;
        }
        
        // Enter key support
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                if (document.getElementById('setupForm').style.display !== 'none') {
                    createUser();
                } else {
                    login();
                }
            }
        });
    </script>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_chat_page(self):
        """Serve the chat interface page"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat - Local AI Assistant</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 1.5rem; }
        .user-info { display: flex; align-items: center; gap: 1rem; }
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
            padding: 1rem;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background: white;
            border-radius: 15px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .message {
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 12px;
            max-width: 80%;
            word-wrap: break-word;
        }
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
        }
        .assistant-message {
            background: #f8f9fa;
            color: #333;
            border: 1px solid #e9ecef;
        }
        .input-container {
            display: flex;
            gap: 1rem;
            background: white;
            padding: 1rem;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .input-container input {
            flex: 1;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 25px;
            font-size: 1rem;
            outline: none;
        }
        .input-container input:focus {
            border-color: #667eea;
        }
        .send-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            transition: transform 0.2s;
        }
        .send-btn:hover { transform: translateY(-1px); }
        .send-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .help-text {
            font-size: 0.9rem;
            color: #666;
            text-align: center;
            margin-bottom: 1rem;
        }
        .logout-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            text-decoration: none;
            font-size: 0.9rem;
        }
        .logout-btn:hover { background: rgba(255,255,255,0.3); }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Local AI Assistant</h1>
        <div class="user-info">
            <span id="userInfo">Loading...</span>
            <a href="/login" class="logout-btn">Logout</a>
        </div>
    </div>
    
    <div class="chat-container">
        <div class="help-text">
            Try: "find config.txt in /home/user" • "read file.txt" • "list processes" • "open notepad" • "help"
        </div>
        
        <div id="messages" class="messages">
            <div class="message assistant-message">
                <strong>🤖 Assistant:</strong> Hello! I'm your Local AI Assistant. I can help you with file operations, process management, and launching applications. What would you like to do?
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Type your command here..." autofocus>
            <button id="sendBtn" class="send-btn" onclick="sendMessage()">Send</button>
        </div>
    </div>
    
    <script>
        let currentUser = null;
        
        // Load user info
        fetch('/api/user-info')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentUser = data.user;
                    document.getElementById('userInfo').textContent = `${data.user.username} (${data.user.role})`;
                } else {
                    window.location.href = '/login';
                }
            })
            .catch(error => {
                window.location.href = '/login';
            });
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, 'user');
            input.value = '';
            
            // Disable send button
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';
            
            // Send to API
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.response, 'assistant');
            })
            .catch(error => {
                addMessage('Error: Failed to process command', 'assistant');
            })
            .finally(() => {
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
                input.focus();
            });
        }
        
        function addMessage(text, sender) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            if (sender === 'user') {
                messageDiv.innerHTML = `<strong>👤 You:</strong> ${escapeHtml(text)}`;
            } else {
                messageDiv.innerHTML = `<strong>🤖 Assistant:</strong> ${escapeHtml(text).replace(/\\n/g, '<br>')}`;
            }
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Enter key support
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !document.getElementById('sendBtn').disabled) {
                sendMessage();
            }
        });
    </script>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_api_request(self):
        """Handle API requests"""
        if self.path == '/api/status':
            self.handle_status()
        elif self.path == '/api/login':
            self.handle_login()
        elif self.path == '/api/create-user':
            self.handle_create_user()
        elif self.path == '/api/user-info':
            self.handle_user_info()
        elif self.path == '/api/chat':
            self.handle_chat()
        else:
            self.send_error(404)
    
    def handle_status(self):
        """Handle status check"""
        users_exist = bool(self.config.data["users"])
        response = {"users_exist": users_exist}
        self.send_json_response(response)
    
    def handle_login(self):
        """Handle login request"""
        if self.command != 'POST':
            self.send_error(405)
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        auth_manager = AuthManager(self.config)
        
        # Simulate login process
        user_data = self.config.get_user(data['username'])
        if user_data:
            import hashlib
            password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
            if password_hash == user_data['password_hash']:
                # Store session (simplified)
                global current_session
                current_session = {
                    'username': data['username'],
                    'role': user_data['role']
                }
                self.send_json_response({"success": True})
                return
        
        self.send_json_response({"success": False, "message": "Invalid username or password"})
    
    def handle_create_user(self):
        """Handle user creation"""
        if self.command != 'POST':
            self.send_error(405)
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        try:
            import hashlib
            password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
            self.config.add_user(data['username'], password_hash, data['role'])
            self.config.mark_configured()
            self.send_json_response({"success": True})
        except Exception as e:
            self.send_json_response({"success": False, "message": str(e)})
    
    def handle_user_info(self):
        """Handle user info request"""
        global current_session
        if 'current_session' in globals() and current_session:
            self.send_json_response({
                "success": True,
                "user": current_session
            })
        else:
            self.send_json_response({"success": False})
    
    def handle_chat(self):
        """Handle chat message"""
        if self.command != 'POST':
            self.send_error(405)
            return
        
        global current_session
        if 'current_session' not in globals() or not current_session:
            self.send_json_response({"response": "Please login first"})
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        # Create auth manager with current session
        auth_manager = AuthManager(self.config)
        auth_manager.current_user = current_session['username']
        auth_manager.current_role = current_session['role']
        
        # Process the command
        tools = SimpleTools(self.config, auth_manager)
        parser = CommandParser()
        
        message = data['message'].strip()
        
        if message.lower() == 'help':
            response = """Available commands:
• find <filename> in <directory> - Search for files
• read <filepath> - Read file contents  
• list processes - Show running processes
• open <app_name> - Launch whitelisted application
• help - Show this help"""
        else:
            tool_call = parser.parse_command(message)
            
            if not tool_call:
                response = "I don't understand that command. Type 'help' for available commands."
            else:
                try:
                    tool_name = tool_call["tool"]
                    args = tool_call["args"]
                    
                    if hasattr(tools, tool_name):
                        response = getattr(tools, tool_name)(**args)
                    else:
                        response = f"Unknown tool: {tool_name}"
                        
                except Exception as e:
                    response = f"Error executing {tool_call['tool']}: {e}"
        
        self.send_json_response({"response": response})
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

# Global session storage (simplified)
current_session = None

def start_web_server(port=8080):
    """Start the web server"""
    try:
        with socketserver.TCPServer(("", port), WebUIHandler) as httpd:
            print(f"🌐 Local AI Assistant Web UI started!")
            print(f"📱 Open your browser and go to: http://localhost:{port}")
            print(f"🔗 Or try: http://127.0.0.1:{port}")
            print("Press Ctrl+C to stop the server")
            
            # Auto-open browser
            def open_browser():
                time.sleep(1)
                webbrowser.open(f'http://localhost:{port}')
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Web server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Try a different port:")
            print(f"python web_ui.py {port + 1}")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_web_server(port)