from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, user, service, booking, payment, webhook
import time
from app.logger import logger

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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"Completed: {request.method} {request.url} "
        f"- Status: {response.status_code} "
        f"- Duration: {round(duration * 1000)}ms"
    )
    return response
