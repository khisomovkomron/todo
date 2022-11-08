import sys
sys.path.append('..')

from .auth import get_current_user, get_user_exception
from .todo import successful_response, http_exception
from fastapi import Depends, APIRouter
from logs.loguru import fastapi_logs
from sqlalchemy.orm import Session
from database import SessionLocal
from pydantic import BaseModel
from typing import Optional
import models


logger = fastapi_logs(router='ADDRESS')


router = APIRouter(
    prefix='/address',
    tags=['addres'],
    responses={404: {'description': 'Not found'}}
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
        
class Address(BaseModel):
    address1: str
    address2: Optional[str]
    city: str
    state: str
    country: str
    postalcode: str
    apt_num: Optional[int]


@router.get('/')
async def read_all_addresses(db: Session = Depends(get_db)):
    
    logger.info("READING ALL ADDRESSES")
    
    return db.query(models.Address).all()


@router.get('/{address_id}')
async def read_address_by_id(address_id: int,
                             user: dict = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    logger.info("READING ADDRESS BY ID")

    if user is None:
        raise get_user_exception()
    
    return db.query(models.Address).filter(models.Address.id == address_id).first()


@router.get('/user/')
async def read_current_user_address(user: dict = Depends(get_current_user),
                                    db: Session = Depends(get_db)):
    
    logger.info("READING ADDRESS OF CURRENT USER")

    if user is None:
        raise get_user_exception()
    
    return db.query(models.Address).filter(models.Users.id == user.get('id')).all()


@router.post('/')
async def create_address(address: Address,
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    
    logger.info("CREATING ADDRESS")

    if user is None:
        raise get_user_exception()
    
    address_model = models.Address()
    address_model.address1 = address.address1
    address_model.address2 = address.address2
    address_model.city = address.city
    address_model.state = address.state
    address_model.country = address.country
    address_model.postalcode = address.postalcode
    address_model.apt_num = address.apt_num
    
    db.add(address_model)
    db.flush()
    
    user_model = db.query(models.Users).filter(models.Users.id == user.get('id')).first()
    
    user_model.address_id = address_model.id
    
    db.add(user_model)
    db.commit()
    return successful_response(201)


@router.put('/{address_id}')
async def update_address(address_id: int,
                         address: Address,
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    
    logger.info("UPDATING ADDRESS BY ID")

    if user is None:
        raise get_user_exception()
    
    address_model = db.query(models.Address)\
        .filter(models.Address.id == address_id)\
        .first()
    
    if address_model is None:
        raise http_exception()
    
    address_model.address1 = address.address1
    address_model.address2 = address.address2
    address_model.city = address.city
    address_model.state = address.state
    address_model.country = address.country
    address_model.postalcode = address.postalcode
    address_model.apt_num = address.apt_num
    
    
    db.add(address_model)
    db.commit()
    
    return successful_response(200)

@router.delete('/{address_id}')
async def delete_address(address_id: int,
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    logger.info("DELETING ADDRESS BY ID")

    if user is None:
        raise get_user_exception()
    
    db.query(models.Address).filter(models.Address.id == address_id).delete()
    
    db.commit()

    return successful_response(204)


@router.delete('/')
async def delete_all_addresses(user: dict = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    logger.info("DELETING ALL ADDRESSES")

    if user is None:
        raise get_user_exception()
    
    db.query(models.Address).delete()
    
    db.commit()

    return successful_response(204)
