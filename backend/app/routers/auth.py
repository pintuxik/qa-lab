"""Authentication router - handles login and token operations."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.routers.dependencies import AuthServiceDep
from app.schemas import Token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    auth_service: AuthServiceDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Authenticate user and return access token.

    OAuth2 password flow
    - Uses OAuth2PasswordRequestForm from FastAPI
    - Expects username and password in form data
    - Returns JWT token on success
    - Follows OAuth2 spec for password grant type
    """
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}
