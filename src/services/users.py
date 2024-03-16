
from datetime import datetime, timedelta
from fastapi import Depends
from sqlalchemy.orm import Session
from libgravatar import Gravatar

from src.models.models import User
from src.models.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Get user object by user's email

    Args:
        email (str): User's email
        db (Session): Database session

    Returns:
        User: User object
    """
    return db.query(User).filter(User.email == email).first()

async def create_user(body: UserModel, db: Session) -> User:
    """
    Create user object and write to DB
    Includes avatar creation with Gravatar service

    Args:
        body (UserModel): User attributes
        db (Session): Database session

    Returns:
        User: User object
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), created_at=datetime.now(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def update_token(user: User, token: str | None , db: Session) -> None:
    """
    Save user's refresh token to the database

    Args:
        user (User): User object
        token (str): User's refresh token
        db (Session): DB session
    """
    user.refresh_token = token
    db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    """
    Update flag in DB to see that email was confirmed by email

    Args:
        email (str): user's email
        db (Session): DB session
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update user's avatar

    Args:
        email (str): user's email
        url (str): URL to user's avatar at GRavatar service
        db (Session): DB session

    Returns:
        User: User object with updated avatar attribute.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user