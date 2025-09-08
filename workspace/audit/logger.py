"""
Audit logging with HMAC chaining for tamper detection
"""

import json
import time
import hmac
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

from core.config import Config

class AuditLogger:
    """Audit logger with HMAC chain verification"""
    
    def __init__(self, config: Config):
        self.config = config
        self.log_path = Path(config.audit_log_path)
        self.secret_key = config.audit_secret_key
        self.last_hash: Optional[str] = None
        
        # Initialize log file if it doesn't exist
        if not self.log_path.exists():
            self._initialize_log()
        else:
            self._load_last_hash()
    
    def _initialize_log(self):
        """Initialize audit log with genesis entry"""
        genesis_entry = {
            "timestamp": time.time(),
            "event_type": "log_genesis",
            "data": {"message": "Audit log initialized"},
            "sequence": 0,
            "previous_hash": "0" * 64,
            "hash": ""
        }
        
        # Calculate hash for genesis entry
        genesis_entry["hash"] = self._calculate_hash(genesis_entry)
        self.last_hash = genesis_entry["hash"]
        
        # Write genesis entry
        with open(self.log_path, 'w') as f:
            f.write(json.dumps(genesis_entry) + '\n')
    
    def _load_last_hash(self):
        """Load the last hash from existing log"""
        try:
            with open(self.log_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1].strip())
                    self.last_hash = last_entry["hash"]
                else:
                    self._initialize_log()
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            # If log is corrupted, reinitialize
            self._initialize_log()
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event with HMAC chaining"""
        # Get sequence number
        sequence = self._get_next_sequence()
        
        # Create log entry
        entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data,
            "sequence": sequence,
            "previous_hash": self.last_hash or "0" * 64,
            "hash": ""
        }
        
        # Calculate and set hash
        entry["hash"] = self._calculate_hash(entry)
        self.last_hash = entry["hash"]
        
        # Append to log file
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _calculate_hash(self, entry: Dict[str, Any]) -> str:
        """Calculate HMAC hash for log entry"""
        # Create canonical string representation
        entry_copy = entry.copy()
        entry_copy.pop("hash", None)  # Remove hash field for calculation
        
        canonical_string = json.dumps(entry_copy, sort_keys=True, separators=(',', ':'))
        
        # Calculate HMAC
        return hmac.new(
            self.secret_key,
            canonical_string.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _get_next_sequence(self) -> int:
        """Get next sequence number"""
        try:
            with open(self.log_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1].strip())
                    return last_entry["sequence"] + 1
                return 0
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            return 0