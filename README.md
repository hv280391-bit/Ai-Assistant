# Local AI Assistant

A comprehensive, security-first Python AI assistant that runs locally with dual interfaces (CLI and Web UI). Supports natural multilingual conversations in English, Hindi, Urdu, and Punjabi colloquialisms.

## 🌟 Features

### 🔐 Security-First Design
- **Role-Based Access Control (RBAC)**: viewer, operator, admin roles
- **Comprehensive Audit Logging**: All actions logged with tamper detection
- **Path Allowlist**: Secure file access controls
- **Explicit Confirmations**: "I AUTHORIZE" required for sensitive operations
- **Session Management**: Time-limited sessions with reauthentication

### 🌍 Multilingual Support
- **Natural Language Processing**: Understands colloquial Hindi/Urdu/Punjabi
- **Examples**: "kya hal hai", "file dhundo", "notepad kholo"
- **Romanized Support**: Works with English-written Indian languages

### 🖥️ Dual Interface
- **CLI Mode**: Terminal-based chat for power users
- **Web UI**: Modern single-page application with themes
- **Both Modes**: Can run simultaneously

### 🛠️ Core Capabilities
- **File Operations**: Search, read, browse with security validation
- **Process Management**: List, monitor system processes
- **Application Launching**: Secure app execution with whitelist
- **Web Operations**: Safe webpage content extraction
- **System Integration**: Windows/macOS/Linux compatible

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (no additional dependencies required for basic functionality)
- Optional: `pip install flask psutil keyring` for enhanced features

### Installation & Setup

1. **Clone/Download the assistant:**
   ```bash
   # If you have the files, navigate to the directory
   cd local-ai-assistant
   ```

2. **Run the assistant:**
   ```bash
   # CLI only
   python run_assistant.py --mode cli

   # Web UI only  
   python run_assistant.py --mode web --port 8080

   # Both interfaces (recommended)
   python run_assistant.py --mode both --port 8080
   ```

3. **Access the Web UI:**
   - Open http://localhost:8080 in your browser
   - Login with default credentials (see below)

### Default User Accounts

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `admin` | `admin123` | admin | Full system access, elevation requests |
| `operator` | `operator123` | operator | File ops, app launching, web access |
| `viewer` | `viewer123` | viewer | Read-only file and process access |

## 💬 Usage Examples

### English Commands
```
find files with budget
open /home/user/document.txt
show running processes
launch notepad
read webpage https://example.com
```

### Hindi/Urdu/Punjabi (Romanized)
```
kya hal hai                    # How are things?
file dhundo budget ke naam se  # Find files with budget name
notepad kholo                  # Open notepad
kya chal raha hai system mein  # What's running in system?
```

### Mixed Language
```
hey, kya kaam hai?            # Hey, what work is there?
bhai file search karo         # Brother, search files
chrome kholo yaar             # Open chrome, friend
```

## 🔧 Configuration

### Path Allowlist (`config/allowlist.json`)
```json
{
  "allowed_paths": [
    "~/Documents",
    "~/Desktop", 
    "~/Downloads",
    "C:\\Users\\%USERNAME%\\Documents"
  ]
}
```

### Application Whitelist
Edit `tools/app_tools.py` to modify whitelisted applications:
- Windows: notepad, calculator, chrome, firefox, code
- Linux/macOS: gedit, nano, vim, firefox, chrome, code

## 🏗️ Architecture

```
assistant/
├── run_assistant.py          # Main entry point
├── core/
│   ├── main.py              # Core assistant logic
│   ├── session.py           # Authentication & sessions
│   └── nl_processor.py      # Multilingual NLP
├── tools/
│   ├── file_tools.py        # Secure file operations
│   ├── process_tools.py     # Process management
│   ├── app_tools.py         # Application launching
│   └── web_tools.py         # Web content extraction
├── auth/
│   ├── auth_store.py        # User credential storage
│   └── rbac.py              # Role-based permissions
├── audit/
│   ├── audit_store.py       # Comprehensive logging
│   └── verify_chain.py      # Audit verification
├── web_ui/
│   ├── index.html           # Web interface
│   └── app.js               # Frontend logic
└── config/
    └── allowlist.json       # Security configuration
```

## 🔒 Security Features

### Authentication
- Secure password hashing (PBKDF2 with salt)
- Session timeout and reauthentication
- Failed login attempt tracking

### Authorization
- Role-based permissions for all operations
- Sensitivity levels: low, medium, high
- Explicit confirmation for sensitive actions

### Audit Trail
- All actions logged with timestamps
- Hash chain for tamper detection
- Verification utility included

### File Security
- Path validation against allowlist
- File type detection and safe handling
- Size limits and chunked reading

## 🛡️ Safety Measures

### Confirmation Requirements
High sensitivity operations require typing "I AUTHORIZE":
- System elevation requests
- Privileged application launches
- Sensitive file access

### OS Integration
- Windows: Uses `runas` for elevation
- Linux/macOS: Provides `sudo` instructions
- Never captures credentials automatically

### Fail-Safe Behavior
- Refuses dangerous operations
- Graceful degradation without dependencies
- Clear error messages and alternatives

## 🔧 Advanced Usage

### CLI Arguments
```bash
python run_assistant.py --help

Options:
  --mode {cli,web,both}    Run mode (default: both)
  --port PORT             Web server port (default: 8080)  
  --debug                 Enable debug logging
```

### Audit Verification
```bash
python audit/verify_chain.py
```

### User Management (Admin Only)
```python
from auth.auth_store import AuthStore
auth = AuthStore()

# Create new user
auth.create_user('newuser', 'password123', 'operator')

# List all users  
users = auth.list_users()
```

## 🌐 Web UI Features

### Themes
- Light, Dark, Blue, Green, Purple themes
- Persistent theme selection
- Responsive design

### Chat Interface
- Real-time messaging
- Tool suggestions
- Confirmation dialogs
- File browser integration

### Sidebar Tools
- Quick tool access
- File browser
- Audit log viewer (admin only)

## 🔍 Troubleshooting

### Common Issues

**Permission Denied Errors:**
- Check path allowlist configuration
- Verify user role permissions
- Ensure files exist and are readable

**App Launch Failures:**
- Verify application is installed
- Check whitelist configuration
- Confirm role has app launch permissions

**Web UI Not Loading:**
- Check port availability
- Try different port: `--port 8081`
- Install Flask for full functionality: `pip install flask`

**Authentication Issues:**
- Use default credentials initially
- Check database file permissions
- Reset with: `rm auth/users.db`

### Debug Mode
```bash
python run_assistant.py --debug
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Add comprehensive tests
4. Ensure security review
5. Submit pull request

### Security Guidelines
- All file operations must validate paths
- New tools require permission checks
- Sensitive operations need confirmations
- Audit all user interactions

## 📄 License

This project is provided as-is for educational and research purposes. Please review and adapt security measures for production use.

## 🆘 Support

For issues and questions:
1. Check troubleshooting section
2. Review audit logs for errors
3. Run with `--debug` flag
4. Verify configuration files

---

**⚠️ Security Notice**: This assistant requires explicit user authorization for sensitive operations. Never run with elevated privileges unless specifically needed for authorized operations.
