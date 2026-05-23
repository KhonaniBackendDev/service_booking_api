import json
import stripe
from fastapi import APIRouter, Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from .. import models
from app.config import settings
from app.logger import logger

client = stripe.StripeClient(settings.stripe_secret_key)

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload"
        )
    except stripe.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        )

    if event.type == "checkout.session.completed":

        payload_dict = json.loads(payload)
        session_data = payload_dict["data"]["object"]

        booking_id = (session_data.get("metadata") or {}).get("booking_id")

        if not booking_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing booking_id in metadata",
            )

        booking = db.execute(
            select(models.Booking).where(models.Booking.id == int(booking_id))
        ).scalar_one_or_none()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        if booking.payment_status != "paid":
            try:
                booking.payment_status = "paid"
                booking.stripe_session_id = session_data.get("id")
                db.commit()
            except Exception:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database error",
                )

    elif event.type == "payment_intent.succeeded":
        pass

    elif event.type == "payment_intent.payment_failed":
        pass

    return {"status": "success"}


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
        "stripe_session_id": booking.stripe_session_id,
    }


@router.get("/cancel")
async def payment_cancel(booking_id: int, db: Session = Depends(get_db)):
    booking = db.execute(
        select(models.Booking).where(models.Booking.id == booking_id)
    ).scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    return {
        "message": "Payment cancelled",
        "booking_id": booking_id,
        "payment_status": booking.payment_status,
    }
