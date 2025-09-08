#!/usr/bin/env python3
"""
Complete Enhanced Web-based Local AI Assistant
Professional system with proper session handling, authentication, and natural language processing
"""

import http.server
import socketserver
import json
import secrets
import hashlib
import datetime
import threading
import webbrowser
import time
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config_simple import Config
from enhanced_assistant import EnhancedAssistantTools

# Global session manager
class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = 3600  # 1 hour
    
    def create_session(self, username, role):
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            'username': username,
            'role': role,
            'created_at': datetime.datetime.now(),
            'last_activity': datetime.datetime.now()
        }
        return session_id
    
    def validate_session(self, session_id):
        if not session_id or session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        now = datetime.datetime.now()
        
        if (now - session['last_activity']).seconds > self.session_timeout:
            del self.sessions[session_id]
            return None
        
        session['last_activity'] = now
        return session
    
    def destroy_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

session_manager = SessionManager()

class CompleteWebUIHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.config = Config("config.json")
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_main_page()
        elif self.path == '/auth':
            self.serve_auth_page()
        elif self.path == '/chat':
            self.serve_chat_page()
        elif self.path == '/api/logout':
            self.handle_logout()
        elif self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404)
    
    def get_session_id(self):
        cookie_header = self.headers.get('Cookie')
        if not cookie_header:
            return None
        
        for cookie in cookie_header.split(';'):
            if cookie.strip().startswith('session_id='):
                return cookie.strip().split('=')[1]
        return None
    
    def set_session_cookie(self, session_id):
        self.send_header('Set-Cookie', f'session_id={session_id}; Path=/; HttpOnly; SameSite=Strict; Max-Age=3600')
    
    def serve_main_page(self):
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Local AI Assistant</title>
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
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 600px;
            width: 90%;
        }
        .logo { font-size: 4rem; margin-bottom: 1rem; }
        h1 { color: #333; margin-bottom: 0.5rem; font-size: 2.2rem; font-weight: 700; }
        .subtitle { color: #666; margin-bottom: 2.5rem; font-size: 1rem; line-height: 1.6; }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 35px;
            border-radius: 30px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin: 0.5rem;
            font-weight: 600;
        }
        .btn:hover { transform: translateY(-3px); }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🤖</div>
        <h1>Enhanced Local AI Assistant<br><span style="font-size: 1.4rem; color: #e74c3c;">स्थानीय AI सहायक</span></h1>
        <p class="subtitle">
            Secure system automation under human control<br>
            <span style="color: #e74c3c;">मानव नियंत्रण के तहत सुरक्षित सिस्टम स्वचालन</span>
        </p>
        <a href="/auth" class="btn">Get Started / शुरू करें</a>
    </div>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_auth_page(self):
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Authentication - Enhanced Local AI Assistant</title>
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
        .auth-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.2);
            max-width: 450px;
            width: 90%;
        }
        .auth-header { text-align: center; margin-bottom: 2rem; }
        .auth-logo { font-size: 2.5rem; margin-bottom: 1rem; }
        .auth-title { color: #333; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem; }
        .auth-subtitle { color: #666; font-size: 0.9rem; }
        .auth-tabs {
            display: flex;
            margin-bottom: 2rem;
            background: rgba(248, 249, 250, 0.8);
            border-radius: 12px;
            padding: 4px;
        }
        .auth-tab {
            flex: 1;
            padding: 12px;
            text-align: center;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            color: #666;
        }
        .auth-tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .auth-form { display: none; }
        .auth-form.active { display: block; }
        .form-group { margin-bottom: 1.5rem; }
        .form-label { display: block; margin-bottom: 0.5rem; color: #555; font-weight: 500; font-size: 0.9rem; }
        .form-input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.9);
        }
        .form-input:focus { outline: none; border-color: #667eea; }
        .form-select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 1rem;
            background: rgba(255, 255, 255, 0.9);
        }
        .auth-btn {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .auth-btn:hover { transform: translateY(-2px); }
        .auth-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .message {
            padding: 12px;
            margin: 1rem 0;
            border-radius: 8px;
            text-align: center;
            font-size: 0.9rem;
        }
        .message.error { background: rgba(220, 53, 69, 0.1); color: #dc3545; border: 1px solid rgba(220, 53, 69, 0.2); }
        .message.success { background: rgba(40, 167, 69, 0.1); color: #28a745; border: 1px solid rgba(40, 167, 69, 0.2); }
        .auth-links { text-align: center; margin-top: 1.5rem; }
        .auth-link { color: #667eea; text-decoration: none; font-size: 0.9rem; margin: 0 0.5rem; }
        .auth-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="auth-container">
        <div class="auth-header">
            <div class="auth-logo">🔐</div>
            <h2 class="auth-title">Welcome</h2>
            <p class="auth-subtitle">Secure access to your AI Assistant</p>
        </div>
        
        <div class="auth-tabs">
            <div class="auth-tab active" onclick="switchTab('signin')">Sign In</div>
            <div class="auth-tab" onclick="switchTab('signup')">Sign Up</div>
        </div>
        
        <div id="message"></div>
        
        <form id="signinForm" class="auth-form active">
            <div class="form-group">
                <label class="form-label" for="signinUsername">Username</label>
                <input type="text" id="signinUsername" class="form-input" required>
            </div>
            <div class="form-group">
                <label class="form-label" for="signinPassword">Password</label>
                <input type="password" id="signinPassword" class="form-input" required>
            </div>
            <button type="submit" class="auth-btn">Sign In</button>
        </form>
        
        <form id="signupForm" class="auth-form">
            <div class="form-group">
                <label class="form-label" for="signupUsername">Username</label>
                <input type="text" id="signupUsername" class="form-input" required>
            </div>
            <div class="form-group">
                <label class="form-label" for="signupEmail">Email</label>
                <input type="email" id="signupEmail" class="form-input" required>
            </div>
            <div class="form-group">
                <label class="form-label" for="signupPassword">Password</label>
                <input type="password" id="signupPassword" class="form-input" required>
            </div>
            <div class="form-group">
                <label class="form-label" for="confirmPassword">Confirm Password</label>
                <input type="password" id="confirmPassword" class="form-input" required>
            </div>
            <div class="form-group">
                <label class="form-label" for="userRole">Role</label>
                <select id="userRole" class="form-select">
                    <option value="viewer">Viewer - Read-only access</option>
                    <option value="operator" selected>Operator - Can execute commands</option>
                    <option value="admin">Admin - Full system access</option>
                </select>
            </div>
            <button type="submit" class="auth-btn">Create Account</button>
        </form>
        
        <div class="auth-links">
            <a href="/" class="auth-link">← Back to Home</a>
        </div>
    </div>
    
    <script>
        function switchTab(tab) {
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            document.querySelector(`[onclick="switchTab('${tab}')"]`).classList.add('active');
            
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            document.getElementById(tab + 'Form').classList.add('active');
            
            clearMessage();
        }
        
        function showMessage(text, type) {
            document.getElementById('message').innerHTML = `<div class="message ${type}">${text}</div>`;
        }
        
        function clearMessage() {
            document.getElementById('message').innerHTML = '';
        }
        
        document.getElementById('signinForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('signinUsername').value;
            const password = document.getElementById('signinPassword').value;
            
            if (!username || !password) {
                showMessage('Please enter username and password', 'error');
                return;
            }
            
            const submitBtn = this.querySelector('.auth-btn');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Signing in...';
            
            fetch('/api/signin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage('Login successful! Redirecting...', 'success');
                    setTimeout(() => window.location.href = '/chat', 1000);
                } else {
                    showMessage(data.message, 'error');
                }
            })
            .catch(error => {
                showMessage('Login failed', 'error');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Sign In';
            });
        });
        
        document.getElementById('signupForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('signupUsername').value;
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const role = document.getElementById('userRole').value;
            
            if (!username || !email || !password || !confirmPassword) {
                showMessage('Please fill all fields', 'error');
                return;
            }
            
            if (password !== confirmPassword) {
                showMessage('Passwords do not match', 'error');
                return;
            }
            
            const submitBtn = this.querySelector('.auth-btn');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating account...';
            
            fetch('/api/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password, role })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage('Account created successfully! You can now sign in.', 'success');
                    switchTab('signin');
                    document.getElementById('signinUsername').value = username;
                } else {
                    showMessage(data.message, 'error');
                }
            })
            .catch(error => {
                showMessage('Failed to create account', 'error');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create Account';
            });
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
        session_id = self.get_session_id()
        session = session_manager.validate_session(session_id)
        
        if not session:
            self.send_response(302)
            self.send_header('Location', '/auth')
            self.end_headers()
            return
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat - Enhanced Local AI Assistant</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header h1 {{ font-size: 1.3rem; }}
        .user-info {{ display: flex; align-items: center; gap: 1rem; }}
        .chat-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 900px;
            margin: 0 auto;
            width: 100%;
            padding: 1rem;
        }}
        .messages {{
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background: white;
            border-radius: 15px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .message {{
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 12px;
            max-width: 85%;
            word-wrap: break-word;
            line-height: 1.5;
        }}
        .user-message {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
        }}
        .assistant-message {{
            background: #f8f9fa;
            color: #333;
            border: 1px solid #e9ecef;
        }}
        .input-container {{
            display: flex;
            gap: 1rem;
            background: white;
            padding: 1rem;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .input-container input {{
            flex: 1;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 25px;
            font-size: 1rem;
            outline: none;
        }}
        .input-container input:focus {{ border-color: #667eea; }}
        .send-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            transition: transform 0.2s;
        }}
        .send-btn:hover {{ transform: translateY(-1px); }}
        .send-btn:disabled {{ opacity: 0.6; cursor: not-allowed; }}
        .logout-btn {{
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            text-decoration: none;
            font-size: 0.9rem;
        }}
        .logout-btn:hover {{ background: rgba(255,255,255,0.3); }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Enhanced Local AI Assistant</h1>
        <div class="user-info">
            <span>{session['username']} ({session['role']})</span>
            <a href="/api/logout" class="logout-btn">Logout</a>
        </div>
    </div>
    
    <div class="chat-container">
        <div id="messages" class="messages">
            <div class="message assistant-message">
                <strong>🤖 Assistant:</strong> Hello {session['username']}! I'm your Enhanced Local AI Assistant with advanced natural language understanding.<br><br>
                Try natural commands like:<br>
                • "kya hal h system ka?" (What's the system status?)<br>
                • "mujhe config files dikhao" (Show me config files)<br>
                • "system scan karo" (Do a system scan)<br>
                • "hello" or "kya hal h" for casual chat!
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Type naturally... / प्राकृतिक रूप से टाइप करें..." autofocus>
            <button id="sendBtn" class="send-btn" onclick="sendMessage()">Send</button>
        </div>
    </div>
    
    <script>
        function sendMessage() {{
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            addMessage(message, 'user');
            input.value = '';
            
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';
            
            fetch('/api/chat', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ message }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    addMessage(data.response, 'assistant');
                }} else {{
                    addMessage('Error: ' + data.message, 'assistant');
                }}
            }})
            .catch(error => {{
                addMessage('Error: Failed to process command', 'assistant');
            }})
            .finally(() => {{
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
                input.focus();
            }});
        }}
        
        function addMessage(text, sender) {{
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{sender}}-message`;
            
            if (sender === 'user') {{
                messageDiv.innerHTML = `<strong>👤 You:</strong> ${{escapeHtml(text)}}`;
            }} else {{
                messageDiv.innerHTML = `<strong>🤖 Assistant:</strong> ${{escapeHtml(text).replace(/\\n/g, '<br>')}}`;
            }}
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        document.getElementById('messageInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter' && !document.getElementById('sendBtn').disabled) {{
                sendMessage();
            }}
        }});
    </script>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def handle_api_request(self):
        if self.path == '/api/signin':
            self.handle_signin()
        elif self.path == '/api/signup':
            self.handle_signup()
        elif self.path == '/api/logout':
            self.handle_logout()
        elif self.path == '/api/chat':
            self.handle_chat()
        else:
            self.send_error(404)
    
    def handle_signin(self):
        if self.command != 'POST':
            self.send_error(405)
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        username = data.get('username')
        password = data.get('password')
        
        user_data = self.config.get_user(username)
        if user_data:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash == user_data['password_hash']:
                session_id = session_manager.create_session(username, user_data['role'])
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.set_session_cookie(session_id)
                self.end_headers()
                
                response = {"success": True, "message": "Login successful"}
                self.wfile.write(json.dumps(response).encode())
                return
        
        self.send_json_response({"success": False, "message": "Invalid username or password"})
    
    def handle_signup(self):
        if self.command != 'POST':
            self.send_error(405)
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'operator')
        
        if self.config.get_user(username):
            self.send_json_response({"success": False, "message": "Username already exists"})
            return
        
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.config.add_user(username, password_hash, role, email)
            self.config.mark_configured()
            self.send_json_response({"success": True, "message": "Account created successfully"})
        except Exception as e:
            self.send_json_response({"success": False, "message": str(e)})
    
    def handle_logout(self):
        session_id = self.get_session_id()
        if session_id:
            session_manager.destroy_session(session_id)
        
        self.send_response(302)
        self.send_header('Location', '/')
        self.send_header('Set-Cookie', 'session_id=; Path=/; HttpOnly; Max-Age=0')
        self.end_headers()
    
    def handle_chat(self):
        if self.command != 'POST':
            self.send_error(405)
            return
        
        session_id = self.get_session_id()
        session = session_manager.validate_session(session_id)
        
        if not session:
            self.send_json_response({"success": False, "message": "Session expired"})
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        message = data.get('message', '')
        
        try:
            assistant = EnhancedAssistantTools(self.config, session['role'])
            response = assistant.process_message(message)
            self.send_json_response({"success": True, "response": response})
        except Exception as e:
            self.send_json_response({"success": False, "message": f"Error: {str(e)}"})

def start_server(port=8080):
    """Start the web server"""
    handler = CompleteWebUIHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 Enhanced Local AI Assistant started!")
        print(f"🌐 Open your browser and go to: http://localhost:{port}")
        print(f"🔐 Create your account to get started")
        print(f"🗣️ Supports natural language: English & Hindi")
        print(f"🔍 Advanced system scanning capabilities")
        print(f"⚡ Persistent sessions with security")
        print(f"\n📝 Press Ctrl+C to stop the server")
        
        # Open browser automatically
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open(f"http://localhost:{port}")
            except:
                pass
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()