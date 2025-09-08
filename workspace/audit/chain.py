"""
HMAC chain verification for audit logs
"""

import json
import hmac
import hashlib
from pathlib import Path
from typing import List, Dict, Any

class AuditChain:
    """Verifies audit log integrity using HMAC chain"""
    
    def __init__(self, log_path: str, secret_key: bytes):
        self.log_path = Path(log_path)
        self.secret_key = secret_key
    
    def verify_chain(self) -> bool:
        """Verify the entire audit chain"""
        if not self.log_path.exists():
            return True  # Empty log is valid
        
        entries = self._load_entries()
        if not entries:
            return True
        
        # Verify each entry
        for i, entry in enumerate(entries):
            # Verify hash
            if not self._verify_entry_hash(entry):
                print(f"Hash verification failed for entry {i}")
                return False
            
            # Verify chain (except for genesis)
            if i > 0:
                expected_prev_hash = entries[i-1]["hash"]
                if entry["previous_hash"] != expected_prev_hash:
                    print(f"Chain verification failed at entry {i}")
                    return False
        
        return True
    
    def _load_entries(self) -> List[Dict[str, Any]]:
        """Load all log entries"""
        entries = []
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        
        return entries
    
    def _verify_entry_hash(self, entry: Dict[str, Any]) -> bool:
        """Verify hash of a single entry"""
        stored_hash = entry.get("hash", "")
        
        # Calculate expected hash
        entry_copy = entry.copy()
        entry_copy.pop("hash", None)
        
        canonical_string = json.dumps(entry_copy, sort_keys=True, separators=(',', ':'))
        expected_hash = hmac.new(
            self.secret_key,
            canonical_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return stored_hash == expected_hash
    
    def get_tampered_entries(self) -> List[int]:
        """Get list of tampered entry indices"""
        tampered = []
        entries = self._load_entries()
        
        for i, entry in enumerate(entries):
            if not self._verify_entry_hash(entry):
                tampered.append(i)
            
            if i > 0:
                expected_prev_hash = entries[i-1]["hash"]
                if entry["previous_hash"] != expected_prev_hash:
                    tampered.append(i)
        
        return tampered