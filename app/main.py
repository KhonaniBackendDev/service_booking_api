from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, user, service, booking, payment, webhook

### models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(service.router)
app.include_router(booking.router)
app.include_router(payment.router)
app.include_router(webhook.router)
