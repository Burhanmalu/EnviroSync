import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, LoginRequest
from app.core.security import verify_password, get_password_hash, create_access_token

class AuthService:
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        user_id = f"user-{uuid.uuid4().hex[:8]}"
        user = User(
            id=user_id,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            role=user_in.role,
            assigned_hall_id=user_in.assigned_hall_id,
            is_active=user_in.is_active
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def authenticate(self, db: AsyncSession, login_data: LoginRequest) -> Optional[tuple[User, str]]:
        user = await self.get_user_by_email(db, login_data.email)
        if not user:
            return None
        if not verify_password(login_data.password, user.hashed_password):
            return None
        
        token = create_access_token(subject=user.id, role=user.role.value)
        return user, token

auth_service = AuthService()
