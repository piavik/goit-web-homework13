import unittest
import jwt
from unittest.mock import MagicMock, patch
# from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException

from src.models.models import User
from src.services.auth import auth_service


class TestAuth(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.password = "correct_password"
        self.email = "example@example.com"
        self.password_hash = '$2b$12$297gxHDvVhxOSpBjBhERJeevB/FeHsXP1ohNrfQpw4z8BXLnxmx42'
        self.password_incorrect = "Not-correct_password"
        self.refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJleGFtcGxlQGV4YW1wbGUuY29tIiwiaWF0IjoxNzEwNjQwNTg4LCJleHAiOjE3MTEyNDUzODgsInNjb3BlIjoicmVmcmVzaF90b2tlbiJ9.DA4Zt7mGHhvQUwLShMQyz4l-Ai9cGuAaqPOTsVP3Yv8"
        self.wrong_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJleGFtcGxlQGV4YW1wbGUuY29tIiwiaWF0IjoxNzEwNjQwNTg4LCJleHAiOjE3MTA2NDE0ODgsInNjb3BlIjoiYWNjZXNzX3Rva2VuIn0.5WOg-7TmGuiax7qq5AW4WhywsR94jlDKxATWCupcbL0"

    async def test_verify_password_correct_password(self):
        result = auth_service.verify_password(self.password, self.password_hash)
        self.assertTrue(result)

    async def test_verify_password_not_correct_password(self):
        result = auth_service.verify_password(self.password_incorrect, self.password_hash)
        self.assertFalse(result)

    async def test_get_password_hash(self):
        result = auth_service.get_password_hash(self.password)
        self.assertIsInstance(self.password_hash, str)
    
    async def test_create_access_token(self):
        token = await auth_service.create_access_token(data={"sub": self.email}, expires_delta=30)
        jwt_payload = jwt.decode(token, auth_service.SECRET_KEY, [auth_service.ALGORITHM])
        test_email = jwt_payload['sub']
        self.assertEqual(test_email, self.email)

    async def test_create_refresh_token(self):
        token = await auth_service.create_refresh_token(data={"sub": self.email})
        jwt_payload = jwt.decode(token, auth_service.SECRET_KEY, [auth_service.ALGORITHM])
        test_email = jwt_payload['sub']
        test_scope = jwt_payload['scope']
        self.assertEqual(test_email, self.email)
        self.assertEqual(test_scope, "refresh_token")
    
    async def test_get_email_from_refresh_token_correct(self):
        result = await auth_service.get_email_from_refresh_token(self.refresh_token)
        self.assertEqual(result, self.email)
    
    async def test_get_email_from_refresh_token_incorrect_token(self):
        with self.assertRaises(HTTPException):
            await auth_service.get_email_from_refresh_token(self.wrong_token)

    async def test_get_current_user(self):
        ...

    async def test_create_email_token(self):
        token = await auth_service.create_email_token(data={"sub": self.email})
        jwt_payload = jwt.decode(token, auth_service.SECRET_KEY, [auth_service.ALGORITHM])
        test_email = jwt_payload['sub']
        self.assertEqual(test_email, self.email)

    async def test_get_email_from_token_correct(self):
        email_token_data = {"sub": self.email, "iat": 1710640588 , "exp": 1711245388, "scope": "email_token"}
        email_token = jwt.encode(email_token_data, auth_service.SECRET_KEY, auth_service.ALGORITHM)
        test_email = await auth_service.get_email_from_token(email_token)
        self.assertEqual(test_email, self.email)

    async def test_get_email_from_token_invalid(self):
        email_token_data = {"sub": "somemail@test.com", "iat": 1710640588, "exp": 1711245388, "scope": "email_token"}
        email_token = jwt.encode(email_token_data, auth_service.SECRET_KEY, auth_service.ALGORITHM)
        test_email = await auth_service.get_email_from_token(email_token)
        self.assertNotEqual(test_email, self.email)

if __name__ == '__main__':
    unittest.main()
