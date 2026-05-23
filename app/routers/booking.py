from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..oauth2 import get_current_user
from .. import models, schemas
from app.logger import logger

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# CREATE BOOKING
@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.BookingResponse
)
def create_booking(
    booking_details: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can book services",
        )

    service = db.execute(
        select(models.Service).where(models.Service.id == booking_details.service_id)
    ).scalar_one_or_none()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    new_booking = models.Booking(
        user_id=current_user.id,
        service_id=service.id,
        price=service.price,
        payment_status="pending",
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking


# DELETE BOOKING
@router.delete("/{id}")
def delete_booking(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    booking = db.execute(
        select(models.Booking).where(models.Booking.id == id)
    ).scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    if booking.payment_status == "paid":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a paid booking",
        )

    db.delete(booking)
    db.commit()

    return {"message": "Booking deleted"}


@router.get("/", response_model=List[schemas.BookingResponse])
def get_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    bookings = (
        db.execute(
            select(models.Booking).where(models.Booking.user_id == current_user.id)
        )
        .scalars()
        .all()
    )

    return bookings


@router.get("/{id}", response_model=schemas.BookingResponse)
def get_booking(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    booking = db.execute(
        select(models.Booking).where(models.Booking.id == id)
    ).scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    return booking
