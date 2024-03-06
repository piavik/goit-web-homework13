from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.models.db import get_db
from src.models.schemas import ContactModel, ContactResponse,UserModel
from src.workers import contacts
from src.auth.auth import auth_service


router = APIRouter(prefix='/contacts', dependencies=[Depends(RateLimiter(times=2, seconds=5))])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, 
                        limit: int = 100, 
                        db: Session = Depends(get_db)
                        ):
    contacts = await contacts.get_contacts(skip, limit, db)
    return contacts

@router.get("/query/birtdays", response_model=List[ContactResponse])
async def find_contacts_with_birthdays( days: int = 7, 
                                        today: bool = False, 
                                        db: Session = Depends(get_db), 
                                        current_user: UserModel = Depends(auth_service.get_current_user)
                                       ):
    contacts = await contacts.find_contacts_with_birthdays(days, today, db)
    if contacts == [] or contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contacts not found")
    return contacts

@router.get("/query", response_model=List[ContactResponse])
async def find_contacts(first_name: str = "",
                        last_name: str = "",
                        email: str = "",
                        db: Session = Depends(get_db),
                        current_user: UserModel = Depends(auth_service.get_current_user)
                        ):
    contacts = await contacts.find_contacts(first_name, last_name, email, db)
    if contacts == [] or contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contacts not found")
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact( contact_id: int, 
                        db: Session = Depends(get_db), 
                        current_user: UserModel = Depends(auth_service.get_current_user)
                        ):
    contact = await contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact

@router.post("/", response_model=ContactResponse)
async def create_contact(body: ContactModel, 
                        db: Session = Depends(get_db), 
                        current_user: UserModel = Depends(auth_service.get_current_user)
                        ):
    return await contacts.create_contact(body, db, current_user)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactModel, 
                        contact_id: int, 
                        db: Session = Depends(get_db), 
                        current_user: UserModel = Depends(auth_service.get_current_user)
                        ):
    contact = await contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int,
                        db: Session = Depends(get_db),
                        current_user: UserModel = Depends(auth_service.get_current_user)
                        ):
    contact = await contacts.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact


