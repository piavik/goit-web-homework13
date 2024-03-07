import unittest
from unittest.mock import patch, Mock

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

# from src.config.settings import settings
# from src.models.db import get_db
# from src.models.models import User
# from src.models.schemas import UserModel
# from src.auth.user import get_user_by_email
from src.auth.auth import auth_service

class TestAuth(unittest.TestCase):
    # def setUp(self):
    #     self.plain_password = "just_a_password"

    def test_verify_password(self):
        self.plain_password = "uhbaisdkoaskjd"
        self.hashed_password = CryptContext(schemes=["bcrypt"]).hash(self.plain_password)
        self.assertEqual(auth_service.verify_password(self.plain_password, self.hashed_password), True)




if __name__ == '__main__':
    unittest.main()
