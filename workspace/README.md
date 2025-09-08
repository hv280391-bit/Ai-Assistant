# Local AI Assistant

A secure Python-based local AI chatbot assistant that performs system tasks under explicit human control.

## Features

- 🔒 **Security First**: Role-based access control, audit logging, explicit consent
- 🛠️ **Modular Tools**: File operations, process management, app launching, web reading
- 📝 **Audit Trail**: HMAC-chained logging for tamper detection
- 🔑 **Secure Auth**: OS keyring integration, credential prompts
- 🎯 **Controlled Access**: Allowlisted paths and whitelisted applications

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

### First Run Setup

1. Create user account with role (viewer/operator/admin)
2. Configure allowlisted paths and whitelisted applications
3. Start chatting with the assistant

### Example Interactions

```
User: find finance.xlsx under my Documents
Assistant: [Searches files and returns results]

User: read /Users/hemant/Documents/finance.xlsx  
Assistant: [Requests confirmation for medium sensitivity operation]

User: install nginx
Assistant: [Requires "I AUTHORIZE" + OS credential prompt for high sensitivity]
```

## Security Model

- **Allowlisted Paths**: File access restricted to home directory + project folder by default
- **Whitelisted Apps**: Only pre-approved applications can be launched
- **Explicit Consent**: Sensitive operations require typed confirmation
- **OS Integration**: Uses native credential prompts (sudo/UAC/polkit)
- **Audit Logging**: All operations logged with HMAC chaining

## Project Structure

```
├── main.py              # Entry point
├── core/
│   ├── assistant.py     # Main assistant logic
│   ├── config.py        # Configuration management
│   └── parser.py        # Command parsing
├── auth/
│   ├── manager.py       # Authentication & authorization
│   └── roles.py         # Role definitions
├── audit/
│   ├── logger.py        # Audit logging with HMAC
│   └── chain.py         # HMAC chain verification
├── tools/
│   ├── base.py          # Base tool interface
│   ├── files.py         # File operations
│   ├── processes.py     # Process management
│   ├── apps.py          # Application launcher
│   ├── web.py           # Web reading
│   ├── scheduler.py     # Reminder scheduling
│   └── elevation.py     # Privileged operations
└── utils/
    ├── security.py      # Security utilities
    └── prompts.py       # User interaction prompts
```