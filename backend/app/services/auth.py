from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)
from backend.app.models.user import User


class AuthService:
    @staticmethod
    def hash_password(password:str)->str:
        password_bytes = password.encode("utf-8")
        return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain_password:str,hashed_password:str)->bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    @staticmethod
    def create_access_token(
            user_id: int,
    ) -> str:

        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload = {
            "sub": str(user_id),
            "exp": expire,
        }

        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

    @staticmethod
    def decode_access_token(token: str) -> int | None:
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
            )
        except jwt.PyJWTError:
            return None

        subject = payload.get("sub")

        if subject is None:
            return None

        try:
            return int(subject)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def register_user(
            db: Session,
            name: str,
            email: str,
            password: str,
    ) -> User:

        statement = select(User).where(
            User.email == email
        )

        existing_user = db.execute(statement).scalar_one_or_none()

        if existing_user:
            raise ValueError("Email already registered")

        user = User(
            name=name,
            email=email,
            hashed_password=AuthService.hash_password(password),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def authenticate_user(
            db: Session,
            email: str,
            password: str,
    ) -> User | None:

        statement = select(User).where(
            User.email == email
        )

        user = db.execute(statement).scalar_one_or_none()

        if not user:
            return None

        if not AuthService.verify_password(
                password,
                user.hashed_password,
        ):
            return None

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)