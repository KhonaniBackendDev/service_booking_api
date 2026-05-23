from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..utils import pass_hash
from .. import models, schemas
from app.logger import logger

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse
)
def create_user(user_info: schemas.UserCreate, db: Session = Depends(get_db)):

    user_dict = user_info.model_dump()
    user_dict["password"] = pass_hash(user_info.password)

    new_user = models.User(**user_dict)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    return new_user
