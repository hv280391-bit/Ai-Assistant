# Local AI Assistant (Standalone Version)

A secure Python-based local AI chatbot assistant that performs system tasks under explicit human control. This version uses **ZERO external dependencies** - only Python standard library.

## Features

- 🔒 **Security First**: Role-based access control, explicit consent
- 🛠️ **Core Tools**: File operations, process management, app launching
- 📝 **Simple Logging**: Basic audit trail
- 🔑 **Local Auth**: File-based user authentication
- 🎯 **Controlled Access**: Allowlisted paths and whitelisted applications

## Installation

**No pip install required!** This version uses only Python standard library.

```bash
# Just run it directly
python main_simple.py
```

## Usage

```bash
python main_simple.py
```

### First Run Setup

1. Create user account with role (viewer/operator/admin)
2. Configure allowlisted paths and whitelisted applications
3. Start chatting with the assistant

### Example Interactions

```
User: find config.txt in /home/user
Assistant: [Searches files and returns results]

User: read /home/user/documents/notes.txt  
Assistant: [Shows file contents]

User: list processes
Assistant: [Shows running processes]

User: open notepad
Assistant: [Launches notepad if whitelisted]
```

## Security Model

- **Allowlisted Paths**: File access restricted to home directory + project folder by default
- **Whitelisted Apps**: Only pre-approved applications can be launched
- **Explicit Consent**: Sensitive operations require confirmation
- **Role-Based Access**: 3-tier permission system (viewer/operator/admin)

## Project Structure

```
├── main_simple.py           # Entry point (no dependencies)
├── core/
│   └── config_simple.py     # Configuration management
├── auth/
│   └── manager_simple.py    # Authentication
├── assistant_simple.py      # Main assistant logic
└── README_simple.md         # This file
```

## Available Commands

- `find <filename> in <directory>` - Search for files
- `read <filepath>` - Read file contents  
- `list processes` - Show running processes
- `open <app_name>` - Launch whitelisted application
- `help` - Show available commands
- `quit` - Exit assistant

## Roles & Permissions

- **Viewer**: Read files, search files, list processes
- **Operator**: All viewer permissions + launch apps
- **Admin**: All operator permissions + system administration

This standalone version provides core functionality without external dependencies, perfect for environments with restricted internet access or package installation limitations.