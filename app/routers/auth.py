from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from ..database import get_db
from ..utils import verify
from ..oauth2 import create_token
from .. import models, schemas
from app.logger import logger

router = APIRouter(prefix="/login", tags=["Authentication"])

MAX_ATTEMPTS = 3
LOCK_TIME = timedelta(minutes=30)


@router.post("/", response_model=schemas.Token)
def login_user(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    # Get user
    user = db.execute(
        select(models.User).where(models.User.email == user_credentials.username)
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect user credentials"
        )

    if user.lock_until and user.lock_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account locked. Try again later",
        )
    # Wrong password
    if not verify(user_credentials.password, user.password):
        user.failed_attempts += 1

        if user.failed_attempts >= MAX_ATTEMPTS:
            user.lock_until = datetime.now(timezone.utc) + LOCK_TIME
            user.failed_attempts = 0  # reset after lock

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    # Correct password
    user.failed_attempts = 0
    user.lock_until = None
    db.commit()

    access_token = create_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
