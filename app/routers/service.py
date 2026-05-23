from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..oauth2 import get_current_user
from .. import models, schemas
from typing import List
import logging

router = APIRouter(prefix="/services", tags=["Services"])
logger = logging.getLogger(__name__)


# CREATE SERVICE
@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.ServiceResponse
)
def create_service(
    service_details: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    logger.info(
        f"Create service attempt - user_id={current_user.id}, "
        f"role={current_user.role}, service_name={service_details.service}"
    )
    if current_user.role != "owner":
        logger.warning(
            f"Forbidden - non-owner tried to create a service",
            f"user_id={current_user.id}, role={current_user.role}",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only service owners can create services",
        )

    new_service = models.Service(
        user_id=current_user.id, **service_details.model_dump()
    )

    try:
        db.add(new_service)
        db.commit()
        db.refresh(new_service)
    except IntegrityError:
        db.rollback()

        logger.warning(
            f"Service creation conflit - duplicate name",
            f"'{service_details.service}' for user_id={current_user.id}",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service name already exists",
        )
    logger.info(
        f"Service created successfully — service_id={new_service.id}, "
        f"name='{new_service.service}', owner_id={current_user.id}"
    )
    return new_service


# UPDATE SERVICE
@router.put("/{id}", response_model=schemas.ServiceResponse)
def update_service(
    id: int,
    service_details: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    logger.info(
        f"Update service attempt - user_id={current_user.id}",
        f"role={current_user.role}, service_name={service_details.service}",
    )
    if current_user.role != "owner":
        logger.warning(
            "Forbidden - non-owner tried to created service",
            f"user_id={current_user.id}, role={current_user.role}",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only service owners can update services",
        )
    try:
        service = db.execute(
            select(models.Service).where(models.Service.id == id)
        ).scalar_one_or_none()
    except Exception as e:
        logger.error(
            f"Database error fetching service_id={id}"
            f"for update by user_id={current_user,id}:{e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )

    if not service:
        logger.warning(
            f"Service with id={id} is not found"
            f"Requested by user_id={current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with id {id} not found",
        )

    if service.user_id != current_user.id:
        logger.warning(
            f"Forbidden — user_id={current_user.id} tried to update "
            f"service_id={id} which belongs to user_id={service.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this service",
        )

    service.service = service_details.service
    service.details = service_details.details
    service.price = service_details.price

    try:
        db.commit()
        db.refresh(service)
    except Exception as e:
        db.rollback()
        logger.error(
            f"Database error saving update for "
            f"service_id={id}, user_id={current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update service",
        )
    logger.info(
        f"Service updated successfully — service_id={id}, "
        f"owner_id={current_user.id}, new_name='{service.service}'"
    )

    return service


# DELETE ONE SERVICE
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only service owners can delete services",
        )

    service = db.execute(
        select(models.Service).where(models.Service.id == id)
    ).scalar_one_or_none()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with id {id} not found",
        )

    if service.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this service",
        )

    db.delete(service)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# DELETE ALL SERVICES (owner only)
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_services(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only service owners can delete services",
        )

    db.execute(delete(models.Service).where(models.Service.user_id == current_user.id))
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# GET ALL SERVICES
@router.get("/", response_model=List[schemas.ServiceResponse])
def get_services(db: Session = Depends(get_db)):
    services = db.execute(select(models.Service)).scalars().all()
    return services


# GET ONE SERVICE
@router.get("/{id}", response_model=schemas.ServiceResponse)
def get_service(id: int, db: Session = Depends(get_db)):
    service = db.execute(
        select(models.Service).where(models.Service.id == id)
    ).scalar_one_or_none()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with id {id} not found",
        )

    return service
