from typing import List
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.sql import extract, expression, or_

from src.models.models import Contact
from src.models.schemas import ContactModel, UserModel, ContactResponse

async def get_contacts(skip: int, limit: int, db: Session) -> List[Contact]:
    """
    Get contacts from the database.

    Args:
        skip (int): Number of contacts from start to be skipped.
        limit (int): Number of contacts to be returned.
        db (Session): Database session

    Returns:
        List[Contact]: List of contacts
    """
    return db.query(Contact).offset(skip).limit(limit).all()

async def get_contact(contact_id: int, db: Session) -> ContactResponse | None:
    """
    Get contact from the database by contact ID

    Args:
        contact_id (int): Contact ID
        db (Session): Database session

    Returns:
        ContactResponse: Contact object from DB or None if not found
    """
    return db.query(Contact).filter(Contact.id == contact_id).first()

async def create_contact(body: ContactModel, db: Session, current_user: UserModel) -> ContactResponse:
    """
    Create contact entry in the database

    Args:
        body (ContactModel): Contact attributes
        db (Session): Database session
        current_user (User): Current user associated with this contact entry

    Returns:
        ContactResponse: Contact object
    """
    contact = Contact(first_name=body.first_name.capitalize(), 
                      last_name=body.last_name.capitalize(), 
                      email=body.email.lower(),
                      phone=body.phone,
                      birthday=body.birthday,
                      notes=body.notes,
                      user_id=current_user.id
                      )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def update_contact(contact_id: int, body: ContactModel, db: Session, current_user: UserModel) -> ContactResponse:
    """
    Update contact entry in the database

    Args:
        contact_id (int): Contact id
        body (ContactModel): Contact attributes
        db (Session): Database session
        current_user (User): Current user associated with this contact entry
    Returns:
        ContactResponse: Contact object
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.first_name = body.first_name.capitalize()
        contact.last_name = body.last_name.capitalize()
        contact.email = body.email.lower()
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.notes = body.notes
        contact.used_id = current_user.id
        db.commit()
    db.refresh(contact)
    return contact

async def delete_contact(contact_id: int, db: Session) -> ContactResponse | None:
    """
    Delete contact entry from the database

    Returns:
        ContactResponse: Contact object from DB or None if contact did not exist
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

async def find_contacts(first_name: str, 
                        last_name: str,
                        email: str, 
                        db: Session
                        ) -> List[ContactResponse]:
    """
    Search the database fro the user on a given criterion.
    Only first existing parameter will be evaluated.

    Args:
        first_name (str): User first name
        last_name (str): User last name 
        email (str): User email
        db (Session): Database session

    Returns:
        List[Contact]: List of contacts found by the search criterion
    """
    if first_name:
        contacts = db.query(Contact).filter(Contact.first_name == first_name.capitalize()).all()
    elif last_name:
        contacts = db.query(Contact).filter(Contact.last_name == last_name.capitalize()).all()
    elif email:
        contacts = db.query(Contact).filter(Contact.email == email.lower()).all()

    else:
        contacts = None
    return  contacts
    
async def find_contacts_with_birthdays(days: int, include_today: bool, db: Session) -> List[ContactResponse]:
    """
    Get contacts from the database, whose birthdays are in next 'days' days.

    Args:
        days (int): Number of days from today.
        include_today (bool): Include today or not.
        db (Session): Database session

    Returns:
        List[Contact]: list of contacts that have birthday in next 'days' days
    """
    today_doy = datetime.today().timetuple().tm_yday        # doy = Day Of Year

    days_per_year, leap_delta = (366, 1) if datetime.now().year%4 == 0 and datetime.now().year%400 == 0 else (365, 0)

    start_doy = today_doy + leap_delta
    next_doy = today_doy + days

    if next_doy > days_per_year :
        start_doy = leap_delta
        next_doy -= days_per_year

    contacts = db.query(Contact).filter(or_(
        expression.between(extract('doy', Contact.birthday), start_doy - include_today, next_doy-1),        # -1 because "between" includes end date
        expression.between(extract('doy', Contact.birthday), today_doy - include_today, today_doy+days-1),
        )).all()



    return  contacts