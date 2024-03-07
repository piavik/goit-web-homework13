"""
FastAPI routes module for user authentication
"""
from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from fastapi_limiter.depends import RateLimiter

from src.models.db import get_db
from src.models.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.auth.user import get_user_by_email, create_user, update_token, confirmed_email
from src.auth.auth import auth_service
from src.workers.email import send_email


router   = APIRouter(prefix='', tags=["auth"], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
security = HTTPBearer()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, 
                 background_tasks: BackgroundTasks, 
                 request: Request, 
                 db: Session = Depends(get_db)):
    """
    Sign up a new user.

    Args:
        body (UserModel): User's attributes
        background_tasks (BackgroundTasks): FastAPI background_tasks parameter
        request (Request): The request object
        db (Session): DB session object. Defaults to Depends(get_db).

    Raises:
        HTTPException: 409 Conflict. If the user altready exists.

    Returns:
        UserResponse: User attributes and a simple message
    """
    # check if user exists
    exist_user = await get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created"}

@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Existing user log in function.

    Args:
        body (OAuth2PasswordRequestForm): Dependency injection for FastAPI OAuth2 authentication.
        db (Session): Dependency injection for DB session. Defaults to Depends(get_db).

    Raises:
        HTTPException: 401 Unauthorized. The user's email has not been found in users DB.
        HTTPException: 401 Unauthorized. The user's email has not been confirmed.
        HTTPException: 401 Unauthorized. The password is invalid.

    Returns:
        TokenModel: json with access token, refresh token and token type
    """
    user = await get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/refresh", response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Refresh access token if expired.

    Args:
        credentials (HTTPAuthorizationCredentials): Dependency injection for user authentication. Defaults to Security(security).
        db (Session): Dependency injection for DB session. Defaults to Depends(get_db).

    Raises:
        HTTPException: [description]

    Returns:
        TokenModel: json with access token, refresh token and token type
    """
    token = credentials.credentials
    email = await auth_service.get_email_from_refresh_token(token)
    user = await get_user_by_email(email, db)
    if user.refresh_token != token:
        await update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/confirm_email/{token}")
async def confirm_email(token: str, db: Session = Depends(get_db)) -> dict:
    """
    Endpoint for email confirmation

    Args:
        token (str): email token that was sent to the user via email
        db (Session): Dependency injection for DB session. Defaults to Depends(get_db).

    Raises:
        HTTPException: 400 BadRequest. Token does not correspond to the user's email.

    Returns:
        dict: json message
    """
    email = await auth_service.get_email_from_token(token)
    user = await get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await confirmed_email(email, db)
    return {"message": "Email verified"}

@router.post("/request_email")
async def request_email(body: RequestEmail, 
                        background_tasks: BackgroundTasks, 
                        request: Request, 
                        db: Session = Depends(get_db)) -> dict:
    """
    Create email with user attributes and send via background_tasks

    Args:
        body (RequestEmail): request email attributes
        background_tasks (BackgroundTasks): FastAPI background_tasks
        request (Request): Request object
        db (Session): Dependency injection for DB session. Defaults to Depends(get_db).

    Returns:
        dict: json message
    """
    user = await get_user_by_email(body.email, db)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}
