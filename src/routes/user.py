from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.models.db import get_db
from src.models.models import User
from src.models.schemas import UserDb, UserModel
from src.auth.user import update_avatar
from src.auth.auth import auth_service
from src.config.settings import settings

router = APIRouter(prefix="", tags=["users"])

@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: UserModel = Depends(auth_service.get_current_user)):
    """
    Get current user's info.
    Requres authentication.

    Args:
        current_user (User): Dependency injection for the current user. Defaults to Depends(auth_service.get_current_user).

    Returns:
        UserDb: The current user db object
    """
    return current_user

@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), 
                             db: Session = Depends(get_db),
                             current_user: UserModel = Depends(auth_service.get_current_user)):
    """
    Update user's avatar on Gravatar service.
    Requres authentication.

    Args:
        file (UploadFile): Avatar picture file. Defaults to File().
        db (Session): Dependency injection for DB session. Defaults to Depends(get_db).
        current_user (UserModel): Dependency injection for the current user. Defaults to Depends(auth_service.get_current_user).

    Returns:
        UserDb: The user db object that has the avater changed
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    r = cloudinary.uploader.upload(file.file, public_id=f'ContactsApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactsApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await update_avatar(current_user.email, src_url, db)
    return user
