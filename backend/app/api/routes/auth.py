from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserRegister,
)
from backend.app.services.auth import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register")
def register(
    data: UserRegister,
    db: Session = Depends(get_db),
):
    try:

        user = AuthService.register_user(
            db=db,
            name=data.name,
            email=data.email,
            password=data.password,
        )

        return {
            "message": "User registered successfully",
            "user_id": user.id,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: UserLogin,
    db: Session = Depends(get_db),
):

    user = AuthService.authenticate_user(
        db=db,
        email=data.email,
        password=data.password,
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = AuthService.create_access_token(
        user_id=user.id,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
