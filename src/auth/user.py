
from datetime import datetime, timedelta
from fastapi import Depends
from sqlalchemy.orm import Session
from libgravatar import Gravatar

# from src.models.db import get_db
from src.models.models import User
from src.models.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()

async def create_user(body: UserModel, avatar: str, db: Session) -> User:
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
    user.refresh_token = token
    db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
