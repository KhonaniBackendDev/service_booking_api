import stripe
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from app.config import settings
from app.logger import logger

client = stripe.StripeClient(settings.stripe_secret_key)

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/checkout/{booking_id}")
async def create_checkout_session(booking_id: int, db: Session = Depends(get_db)):

    # Get booking
    booking = db.execute(
        select(models.Booking).where(models.Booking.id == booking_id)
    ).scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )
    if booking.payment_status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking #{booking_id} has already been paid",
        )
    try:
        session = client.v1.checkout.sessions.create(
            params={
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"Booking #{booking_id}",
                            },
                            "unit_amount": int(booking.price * 100),
                        },
                        "quantity": 1,
                    }
                ],
                "mode": "payment",
                "success_url": f"{settings.base_url}/payments/success?booking_id={booking_id}",
                "cancel_url": f"{settings.base_url}/payments/cancel",
                "metadata": {"booking_id": str(booking_id)},
            }
        )

        # Save session ID to booking
        booking.stripe_session_id = session.id
        db.commit()

        return {"checkout_url": session.url}

    except stripe.StripeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/success")
async def payment_success(booking_id: int, db: Session = Depends(get_db)):
    booking = db.execute(
        select(models.Booking).where(models.Booking.id == booking_id)
    ).scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    return {
        "message": "Payment successful",
        "booking_id": booking_id,
        "payment_status": booking.payment_status,
    }
