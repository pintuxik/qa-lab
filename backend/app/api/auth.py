from datetime import timedelta

from app.core.config import settings
from app.core.security import authenticate_user, create_access_token, get_current_user, get_password_hash
from app.database import get_db
from app.models import User
from app.schemas import TestCleanupRequest, Token, UserCreate
from app.schemas import User as UserSchema
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.delete("/delete")
def delete_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete user account - users can only delete their own account"""

    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User successfully deleted"}


@router.post("/test-cleanup")
def test_cleanup(
    request: TestCleanupRequest,
    db: Session = Depends(get_db),
    x_test_api_key: str = Header(None, alias="X-Test-API-Key"),
):
    """Test-only endpoint to clean up test users. Requires TEST_MODE_ENABLED and valid API key."""
    # Check if test mode is enabled
    if not settings.TEST_MODE_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not available")

    # Validate API key
    if not x_test_api_key or x_test_api_key != settings.TEST_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing test API key")

    deleted_count = 0
    deleted_users = []

    # Delete users by IDs
    if request.user_ids:
        for user_id in request.user_ids:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                deleted_users.append({"id": user.id, "username": user.username})
                db.delete(user)
                deleted_count += 1

    # Delete users by username patterns
    if request.username_patterns:
        for pattern in request.username_patterns:
            # Convert glob pattern to SQL LIKE pattern
            sql_pattern = pattern.replace("*", "%").replace("?", "_")
            users = db.query(User).filter(User.username.like(sql_pattern)).all()
            for user in users:
                # Avoid double deletion if already deleted by ID
                if user.id not in [u["id"] for u in deleted_users]:
                    deleted_users.append({"id": user.id, "username": user.username})
                    db.delete(user)
                    deleted_count += 1

    db.commit()

    return {
        "message": f"Successfully deleted {deleted_count} test user(s)",
        "deleted_count": deleted_count,
        "deleted_users": deleted_users,
    }
