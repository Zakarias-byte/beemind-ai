"""
Authentication and Authorization System for BeeMind
Provides JWT-based authentication, role-based access control, and session management
"""

import jwt
import bcrypt
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import secrets
import hashlib
from pathlib import Path

class UserRole(Enum):
    """User roles with different access levels"""
    ADMIN = "admin"
    RESEARCHER = "researcher" 
    VIEWER = "viewer"
    GUEST = "guest"

@dataclass
class User:
    """User data model"""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True
    api_key: Optional[str] = None
    permissions: List[str] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = self._get_default_permissions()
    
    def _get_default_permissions(self) -> List[str]:
        """Get default permissions based on role"""
        role_permissions = {
            UserRole.ADMIN: [
                "view_dashboard", "manage_users", "manage_evolution", 
                "view_analytics", "export_data", "manage_system",
                "view_blockchain", "manage_api_keys"
            ],
            UserRole.RESEARCHER: [
                "view_dashboard", "manage_evolution", "view_analytics", 
                "export_data", "view_blockchain"
            ],
            UserRole.VIEWER: [
                "view_dashboard", "view_analytics", "view_blockchain"
            ],
            UserRole.GUEST: [
                "view_dashboard"
            ]
        }
        return role_permissions.get(self.role, [])

@dataclass
class Session:
    """User session data"""
    session_id: str
    user_id: str
    created_at: str
    expires_at: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True

class BeeMindAuthManager:
    """
    Authentication and authorization manager for BeeMind
    """
    
    def __init__(self, secret_key: Optional[str] = None, users_file: str = "users.json", 
                 sessions_file: str = "sessions.json"):
        """
        Initialize authentication manager
        
        Args:
            secret_key: JWT secret key (generated if not provided)
            users_file: Path to users database file
            sessions_file: Path to sessions database file
        """
        self.secret_key = secret_key or self._generate_secret_key()
        self.users_file = Path(users_file)
        self.sessions_file = Path(sessions_file)
        
        # Ensure auth directory exists
        auth_dir = Path("auth_data")
        auth_dir.mkdir(exist_ok=True)
        
        self.users_file = auth_dir / users_file
        self.sessions_file = auth_dir / sessions_file
        
        # Load existing data
        self.users = self._load_users()
        self.sessions = self._load_sessions()
        
        # Create default admin user if no users exist
        if not self.users:
            self._create_default_admin()
        
        print(f"BeeMind Auth Manager initialized with {len(self.users)} users")
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key for JWT"""
        return secrets.token_urlsafe(32)
    
    def _load_users(self) -> Dict[str, User]:
        """Load users from file"""
        if not self.users_file.exists():
            return {}
        
        try:
            with open(self.users_file, 'r') as f:
                users_data = json.load(f)
            
            users = {}
            for user_id, user_data in users_data.items():
                user_data['role'] = UserRole(user_data['role'])
                users[user_id] = User(**user_data)
            
            return users
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}
    
    def _save_users(self):
        """Save users to file"""
        try:
            users_data = {}
            for user_id, user in self.users.items():
                user_dict = asdict(user)
                user_dict['role'] = user.role.value
                users_data[user_id] = user_dict
            
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def _load_sessions(self) -> Dict[str, Session]:
        """Load sessions from file"""
        if not self.sessions_file.exists():
            return {}
        
        try:
            with open(self.sessions_file, 'r') as f:
                sessions_data = json.load(f)
            
            sessions = {}
            for session_id, session_data in sessions_data.items():
                sessions[session_id] = Session(**session_data)
            
            # Clean expired sessions
            self._cleanup_expired_sessions()
            
            return sessions
        except Exception as e:
            print(f"Error loading sessions: {e}")
            return {}
    
    def _save_sessions(self):
        """Save sessions to file"""
        try:
            sessions_data = {}
            for session_id, session in self.sessions.items():
                sessions_data[session_id] = asdict(session)
            
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions_data, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")
    
    def _create_default_admin(self):
        """Create default admin user"""
        admin_user = self.create_user(
            username="admin",
            email="admin@beemind.dev",
            password="BeeMind2025!",
            role=UserRole.ADMIN
        )
        
        if admin_user:
            print("Default admin user created:")
            print(f"Username: admin")
            print(f"Password: BeeMind2025!")
            print("Please change the password after first login!")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def create_user(self, username: str, email: str, password: str, 
                   role: UserRole = UserRole.VIEWER) -> Optional[User]:
        """
        Create a new user
        
        Args:
            username: Unique username
            email: User email
            password: Plain text password
            role: User role
            
        Returns:
            Created user or None if creation failed
        """
        # Check if username or email already exists
        for user in self.users.values():
            if user.username == username or user.email == email:
                print(f"User with username '{username}' or email '{email}' already exists")
                return None
        
        # Generate user ID
        user_id = hashlib.sha256(f"{username}{email}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        # Create user
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=self.hash_password(password),
            role=role,
            created_at=datetime.now().isoformat(),
            api_key=self._generate_api_key()
        )
        
        self.users[user_id] = user
        self._save_users()
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            Authenticated user or None
        """
        # Find user by username or email
        user = None
        for u in self.users.values():
            if u.username == username or u.email == username:
                user = u
                break
        
        if not user or not user.is_active:
            return None
        
        if self.verify_password(password, user.password_hash):
            # Update last login
            user.last_login = datetime.now().isoformat()
            self._save_users()
            return user
        
        return None
    
    def create_session(self, user: User, ip_address: Optional[str] = None, 
                      user_agent: Optional[str] = None, duration_hours: int = 24) -> Session:
        """
        Create a new session for user
        
        Args:
            user: Authenticated user
            ip_address: Client IP address
            user_agent: Client user agent
            duration_hours: Session duration in hours
            
        Returns:
            Created session
        """
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=duration_hours)
        
        session = Session(
            session_id=session_id,
            user_id=user.user_id,
            created_at=datetime.now().isoformat(),
            expires_at=expires_at.isoformat(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.sessions[session_id] = session
        self._save_sessions()
        
        return session
    
    def validate_session(self, session_id: str) -> Optional[User]:
        """
        Validate session and return user
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            User if session is valid, None otherwise
        """
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return None
        
        # Check if session is expired
        expires_at = datetime.fromisoformat(session.expires_at)
        if datetime.now() > expires_at:
            session.is_active = False
            self._save_sessions()
            return None
        
        # Return user
        return self.users.get(session.user_id)
    
    def create_jwt_token(self, user: User, duration_hours: int = 24) -> str:
        """
        Create JWT token for user
        
        Args:
            user: User to create token for
            duration_hours: Token duration in hours
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role.value,
            'permissions': user.permissions,
            'exp': datetime.utcnow() + timedelta(hours=duration_hours),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token
        
        Args:
            token: JWT token to validate
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Check if user still exists and is active
            user = self.users.get(payload['user_id'])
            if not user or not user.is_active:
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def check_permission(self, user: User, permission: str) -> bool:
        """
        Check if user has specific permission
        
        Args:
            user: User to check
            permission: Permission to check
            
        Returns:
            True if user has permission
        """
        return permission in user.permissions
    
    def _generate_api_key(self) -> str:
        """Generate API key for user"""
        return f"bm_{secrets.token_urlsafe(32)}"
    
    def validate_api_key(self, api_key: str) -> Optional[User]:
        """
        Validate API key and return user
        
        Args:
            api_key: API key to validate
            
        Returns:
            User if API key is valid
        """
        for user in self.users.values():
            if user.api_key == api_key and user.is_active:
                return user
        return None
    
    def logout_session(self, session_id: str) -> bool:
        """
        Logout session (deactivate)
        
        Args:
            session_id: Session ID to logout
            
        Returns:
            True if successful
        """
        session = self.sessions.get(session_id)
        if session:
            session.is_active = False
            self._save_sessions()
            return True
        return False
    
    def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            expires_at = datetime.fromisoformat(session.expires_at)
            if current_time > expires_at:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self._save_sessions()
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        active_users = sum(1 for user in self.users.values() if user.is_active)
        role_counts = {}
        
        for user in self.users.values():
            role = user.role.value
            role_counts[role] = role_counts.get(role, 0) + 1
        
        active_sessions = sum(1 for session in self.sessions.values() if session.is_active)
        
        return {
            'total_users': len(self.users),
            'active_users': active_users,
            'role_distribution': role_counts,
            'active_sessions': active_sessions,
            'total_sessions': len(self.sessions)
        }
    
    def export_audit_log(self) -> Dict[str, Any]:
        """Export audit log for security review"""
        return {
            'export_timestamp': datetime.now().isoformat(),
            'users': [
                {
                    'user_id': user.user_id,
                    'username': user.username,
                    'role': user.role.value,
                    'created_at': user.created_at,
                    'last_login': user.last_login,
                    'is_active': user.is_active
                }
                for user in self.users.values()
            ],
            'sessions': [
                {
                    'session_id': session.session_id,
                    'user_id': session.user_id,
                    'created_at': session.created_at,
                    'expires_at': session.expires_at,
                    'is_active': session.is_active,
                    'ip_address': session.ip_address
                }
                for session in self.sessions.values()
            ],
            'statistics': self.get_user_stats()
        }

# Utility functions for easy integration
def initialize_auth_manager() -> BeeMindAuthManager:
    """Initialize authentication manager with default settings"""
    return BeeMindAuthManager()

def require_permission(permission: str):
    """Decorator to require specific permission for API endpoints"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be implemented in the FastAPI integration
            # For now, it's a placeholder for the concept
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role: UserRole):
    """Decorator to require specific role for API endpoints"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be implemented in the FastAPI integration
            # For now, it's a placeholder for the concept
            return func(*args, **kwargs)
        return wrapper
    return decorator
