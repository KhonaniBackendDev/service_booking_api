from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..oauth2 import get_current_user
from .. import models, schemas
from typing import List

router = APIRouter(prefix="/services", tags=["Services"])


# CREATE SERVICE
@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.ServiceResponse
)
def create_service(
    service_details: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "owner":
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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service name already exists",
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
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only service owners can update services",
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
            detail="Not authorized to update this service",
        )

    service.service = service_details.service
    service.details = service_details.details
    service.price = service_details.price

    db.commit()
    db.refresh(service)

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


# # Basic CRUD
# router = APIRouter(prefix="/services", tags=["Services"])


# # CREATE SERVICE
# @router.post(
#     "/", status_code=status.HTTP_201_CREATED, response_model=schemas.ServiceResponse
# )
# def create_service(
#     service_details: schemas.ServiceCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
# ):
#     if current_user.role != "owner":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only service owners can create services",
#         )
#     new_service = models.Service(
#         user_id=current_user.id, **service_details.model_dump()
#     )

#     try:
#         db.add(new_service)
#         db.commit()
#         db.refresh(new_service)
#     except IntegrityError:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT, detail="Service name already exists"
#         )

#     return new_service


# # UPDATE SERVICE
# @router.put("/{id}", response_model=schemas.ServiceResponse)
# def update_service(
#     id: int,
#     service: schemas.ServiceCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
# ):
#     if current_user.role != "owner":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only service owners can update services",
#         )
#     get_service = db.execute(
#         select(models.Service).where(models.Service.id == id)
#     ).scalar_one_or_none()

#     if get_service is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Service with id: {id} is not found",
#         )

#     if get_service.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update this service",
#         )

#     result = db.execute(
#         update(models.Service)
#         .where(models.Service.id == id)
#         .values(**service.model_dump())
#         .returning(models.Service)
#     )
#     db.commit()
#     updated_service = result.scalar_one_or_none()

#     return updated_service


# # DELETE SERVICE (ONE)
# @router.delete("/{id}")
# def delete_service(
#     id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
# ):
#     if current_user.role != "owner":
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Only service owners can delete services",
#         )

#     service = db.execute(
#         select(models.Service).where(models.Service.id == id)
#     ).scalar_one_or_none()

#     if service is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Service with id: {id} is not found",
#         )
#     if service.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to delete this service",
#         )

#     db.execute(delete(models.Service).where(models.Service.id == id))
#     db.commit()
#     return Response(status_code=status.HTTP_204_NO_CONTENT)


# # DELETE ALL
# @router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
# def delete_all_services(
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
# ):
#     if current_user.role != "owner":
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Only service owners can delete services",
#         )

#     db.execute(delete(models.Service).where(models.Service.user_id == current_user.id))
#     db.commit()
#     return Response(status_code=status.HTTP_204_NO_CONTENT)


# # GET ALL SERVICES
# @router.get("/", response_model=List[schemas.ServiceResponse])
# def get_services(db: Session = Depends(get_db)):
#     services = db.execute(select(models.Service)).scalars().all()

#     return services


# # GET ONE SERVICE
# @router.get("/{id}", response_model=schemas.ServiceResponse)
# def get_services(id: int, db: Session = Depends(get_db)):
#     service = db.execute(
#         select(models.Service).where(models.Service.id == id)
#     ).scalar_one_or_none()

#     if service is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Service with id: {id} is not found",
#         )
#     return service
