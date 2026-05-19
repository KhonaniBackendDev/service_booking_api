from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    text,
    ForeignKey,
    Numeric,
    Boolean,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from .database import Base
from .schemas import UserRole


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)
    failed_attempts = Column(Integer, server_default="0", nullable=False)
    lock_until = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    service = Column(String, nullable=False, unique=True)
    details = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    published = Column(Boolean, server_default="True", nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, nullable=False)
    service_id = Column(
        Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    price = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(
        SAEnum("pending", "paid", "failed", name="payment_status_enum"),
        server_default="pending",
        nullable=False,
    )
    stripe_session_id = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )

    service = relationship("Service")
    user = relationship("User")


# class Booking(Base):
#     __tablename__ = "bookings"

#     id = Column(Integer, primary_key=True, nullable=False)

#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

#     # VERY IMPORTANT — snapshot of price at booking time
#     price = Column(Integer, nullable=False)

#     # payment tracking
#     payment_status = Column(String, default="pending")

#     # optional but useful
#     stripe_session_id = Column(String, nullable=True)

#     created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
