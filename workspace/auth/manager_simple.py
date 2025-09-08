"""
Simplified authentication manager using only standard library
"""

import hashlib
import getpass
from typing import Optional

class AuthManager:
    """Manages user authentication and authorization"""
    
    def __init__(self, config):
        self.config = config
        self.current_user: Optional[str] = None
        self.current_role: Optional[str] = None
    
    def authenticate(self) -> bool:
        """Authenticate user"""
        # If no users exist, create first user
        if not self.config.data["users"]:
            print("No users found. Creating first user...")
            return self._create_first_user()
        
        # Login existing user
        return self._login_user()
    
    def _create_first_user(self) -> bool:
        """Create the first user account"""
        print("\n=== Create First User Account ===")
        
        username = input("Username: ").strip()
        if not username:
            print("Username cannot be empty")
            return False
        
        password = getpass.getpass("Password: ")
        if not password:
            print("Password cannot be empty")
            return False
        
        # Choose role
        print("\nAvailable roles:")
        print("1. viewer - Read-only access")
        print("2. operator - Can launch apps and perform operations")
        print("3. admin - Full access including system administration")
        
        while True:
            role_choice = input("Choose role (1-3) [default: 2]: ").strip() or "2"
            if role_choice in ["1", "2", "3"]:
                break
            print("Please enter 1, 2, or 3")
        
        role_map = {"1": "viewer", "2": "operator", "3": "admin"}
        role = role_map[role_choice]
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Save user
        self.config.add_user(username, password_hash, role)
        
        # Set current user
        self.current_user = username
        self.current_role = role
        
        print(f"✓ User '{username}' created with role '{role}'")
        return True
    
    def _login_user(self) -> bool:
        """Login existing user"""
        print("\n=== Login ===")
        
        username = input("Username: ").strip()
        if not username:
            return False
        
        user_data = self.config.get_user(username)
        if not user_data:
            print("User not found")
            return False
        
        password = getpass.getpass("Password: ")
        password_hash = self._hash_password(password)
        
        if password_hash != user_data["password_hash"]:
            print("Invalid password")
            return False
        
        # Set current user
        self.current_user = username
        self.current_role = user_data["role"]
        
        print(f"✓ Welcome back, {username}! ({self.current_role})")
        return True
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def has_permission(self, permission: str) -> bool:
        """Check if current user has specific permission"""
        if not self.current_role:
            return False
        
        role_permissions = self.config.get_role_permissions(self.current_role)
        return role_permissions.get(permission, False)
    
    def get_current_user(self) -> Optional[str]:
        """Get current username"""
        return self.current_user
    
    def get_current_role(self) -> Optional[str]:
        """Get current user role"""
        return self.current_role