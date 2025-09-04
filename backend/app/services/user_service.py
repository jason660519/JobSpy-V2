"""
User service for user management operations
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models.user import User
from ..core.security import get_password_hash, verify_password


class UserService:
    """Service for user-related operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create_user(
        self,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Create new user"""
        # Check if user already exists
        existing_user = await self.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user
        hashed_password = get_password_hash(password)
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        
        user = User(
            email=email,
            password_hash=hashed_password,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name if full_name else None,
            is_active=True,
            is_verified=False
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_by_email(email)
        
        if not user or not verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        return user
    
    async def update_user(
        self,
        user_id: str,
        **kwargs
    ) -> Optional[User]:
        """Update user information"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        # Update full name if first/last name changed
        if 'first_name' in kwargs or 'last_name' in kwargs:
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            user.full_name = full_name if full_name else None
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        # Verify old password
        if not verify_password(old_password, user.password_hash):
            return False
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        user.password_changed_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def verify_email(self, user_id: str) -> bool:
        """Mark user email as verified"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.is_verified = True
        await self.db.commit()
        return True