import jwt
import pickle
import redis

from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.models.db import get_db
from src.models.models import User
from src.models.schemas import UserModel
from src.services.users import get_user_by_email


class Auth:
    '''
    Class for user authentication and JWT generation
    '''
    pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
    SECRET_KEY    = settings.jwt_secret_key
    ALGORITHM     = settings.jwt_algorithm
    TOKEN_TTL     = settings.jwt_token_ttl
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password) -> bool:
        """
        Verify if plain_password corresponds to hashed_password

        Args:
            plain_password (str): Plaintext password
            hashed_password (bool): Password hash

        Returns:
            bool: Comparison result of provided hash and calculated hash
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Create hash for provided plaintext password

        Args:
            password (str): plaintext password

        Returns:
            str: Hash for provided plaintext password
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Create JWT access token

        Args:
            data (dict): Claims for JWT
            expires_delta (Optional[float], optional): The number of seconds for JWT lifetime. Defaults to None.

        Returns:
            str:  Access token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.TOKEN_TTL)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict) -> str:
        """
        Create JWT refresh token

        Args:
            data (dict):  Claims for JWT

        Returns:
            str: Refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def get_email_from_refresh_token(self, refresh_token: str) -> str:
        """
        Get user's email from JWT refresh token

        Args:
            refresh_token (str): Refresh token

        Raises:
            HTTPException: 401 Unauthorized. If token scope is not 'refresh_token'
            HTTPException: 401 Unauthorized. If provided token is invalid

        Returns:
            str: User's email
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')
        except jwt.exceptions.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """
        Get authenticated user onject

        Args:
            token (str): User's authorization token. Defaults to Depends(oauth2_scheme).
            db (Session): Dependency injection for DB session. Defaults to Depends(get_db).

        Raises:
            credentials_exception: Custom HTTPException for 401 Unauthorized.

        Returns:
            User: Authenticated user object
        """
        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                              detail="Could not validate credentials",
                                              headers={"WWW-Authenticate": "Bearer"},)
        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except jwt.exceptions.InvalidTokenError as e:
            raise credentials_exception
        # check cache
        user = self.r.get(f"user:{email}")
        if user is None:
            user = await get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            # write to chache
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user

    async def create_email_token(self, data: dict) -> str:
        """
        Create token for email validation

        Args:
            data (dict): Claims for JWT

        Returns:
            str: JWT token that will be sent in email URL
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=self.TOKEN_TTL)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
        email_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return email_token

    async def get_email_from_token(self, token: str) -> str:
        """
        Get user's email from JWT token

        Args:
            token (str): JWT token

        Raises:
            HTTPException: JWT token is invalid

        Returns:
            str: user's emailobtained from JWT token
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'email_token':
                email = payload['sub']
                return email
        except jwt.exceptions.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid token for email verification')


auth_service = Auth()
