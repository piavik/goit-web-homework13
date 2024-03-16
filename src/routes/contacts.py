from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.models.db import get_db
from src.models.models import Contact
from src.models.schemas import ContactModel, ContactResponse,UserModel
from src.services import contacts
from src.services.auth import auth_service


router = APIRouter(prefix='/contacts', dependencies=[Depends(RateLimiter(times=2, seconds=5))])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, 
                        limit: int = 100, 
                        db: Session = Depends(get_db)
                        ):
    """
    Get contacts from the database.

    Args:
        skip (int): Number of contacts from start to be skipped. Defaults to 0.
        limit (int): Number of contacts to be returned. Defaults to 100.
        db (Session):git status Dependency injection for DB session. Defaults to Depends(get_db).

    Returns:
        List[ContactResponse]: list of contacts
    """
    list_of_contacts = await contacts.get_contacts(skip, limit, db)
    return list_of_contacts

@router.get("/query/birtdays", response_model=List[ContactResponse])
async def find_contacts_with_birthdays( days: int = 7, 
                                        today: bool = False, 
                                        db: Session = Depends(get_db), 
                                        current_user: UserModel = Depends(auth_service.get_current_user)
                                       ):
    """
    Get contacts from the database, whose birthdays are in next 'days' days.
    Authentication required.

    Args:
        days (int): Number of days from today. Defaults to 7.
        today (bool): Include today or not. Defaults to False.
        db (Session): Dependency injection for DB session. Defaults to Depends(get_db).
        current_user (UserModel): Dependency injection for the current user. Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException: 404 NotFound - no contacts found with given search criteria

    Returns:
        List[ContactResponse]: list of contacts that have birthday in next 'days' days
    """
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
    """
    Search for the contact by given parameter.
    Only first given parameter is evaluated. I.e. if first name ane email are given - search will be made by the first  name only.
    Authentication required.

    Args:
        first_name (str): Search by first name. Defaults to "".
        last_name (str): Search by last name. Defaults to "".
        email (str): Search by email. Defaults to "".
        db (Session): Dependency injection for DB session. Defaults to Depends(get_db).
        current_user (UserModel): Dependency injection for the current user. Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException: 404 NotFound - no contacts found with given search criteria

    Returns:
        List[ContactResponse]: list of contacts by given search criteria
    """
    contacts = await contacts.find_contacts(first_name, last_name, email, db)
    if contacts == [] or contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contacts not found")
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact( contact_id: int, 
                        db: Session = Depends(get_db), 
                        current_user: UserModel = Depends(auth_service.get_current_user)
                        ):
    """
    Get contact by its ID.
    Authentication required.

    Args:
        contact_id (int): Contact ID
        db (Session): Dependency injection for DB session. Defaults to Depends(get_db).
        current_user (UserModel): Dependency injection for the current user. Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException:  404 NotFound - no contacts found with given ID.

    Returns:
        ContactResponse: contact attributes 
    """
    contact = await contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact

@router.post("/", response_model=ContactResponse)
async def create_contact(body: ContactModel, 
                        db: Session = Depends(get_db), 
                        current_user: UserModel = Depends(auth_service.get_current_user)
                        ):
    """
    Create contact wrapper.
    Authentication required.

    Args:
        body (ContactModel): Contact attributes
        db (Session): Dependency injection for DB session. Defaults to Depends(get_db).
        current_user (UserModel): Dependency injection for the current user. Defaults to Depends(auth_service.get_current_user).

    Returns:
        ContactResponse: The Contact attributes for the contact that was created
    """
    return await contacts.create_contact(body, db, current_user)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactModel, 
                        contact_id: int, 
                        db: Session = Depends(get_db), 
                        current_user: UserModel = Depends(auth_service.get_current_user)
                        ):
    """
    Update contact wrapper.
    Authentication required.

    Args:
        body (ContactModel): Contact attributes
        contact_id (int): Contact ID
        db (Session): Dependency injection for DB session. Defaults to Depends(get_db).
        current_user (UserModel): Dependency injection for the current user. Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException: 404 NotFound - no contacts found with given ID.

    Returns:
        ContactResponse: The Contact attributes for the contact that was updated
    """
    contact = await contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int,
                        db: Session = Depends(get_db),
                        current_user: UserModel = Depends(auth_service.get_current_user)
                        ) -> Contact:
    """AI is creating summary for delete_contact

    Args:
        contact_id (int): Contact ID
        db (Session): Dependency injection for DB session. Defaults to Depends(get_db).
        current_user (UserModel): Dependency injection for the current user. Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException: 404 NotFound - no contacts found with given ID.

    Returns:
        ContactResponse: The Contact attributes for the contact that was deleted
    """
    contact = await contacts.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact


