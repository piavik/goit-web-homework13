import unittest
from unittest.mock import MagicMock

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
        token = await auth_service.create_access_token(data={"sub": "test"}, expires_delta=30)
        self.assertIsInstance(token, str)

    async def test_create_refresh_token(self):
        token = await auth_service.create_refresh_token(data={"sub": "test"})
        self.assertIsInstance(token, str)
    
    async def test_get_email_from_refresh_token_correct(self):
        result = await auth_service.get_email_from_refresh_token(self.refresh_token)
        self.assertEqual(result, self.email)
    
    async def test_get_email_from_refresh_token_incorrect_scope(self):
        result = await auth_service.get_email_from_refresh_token(self.wrong_token)
        self.assertRaises(HTTPException)

    async def test_get_email_from_refresh_token_incorrect_token(self):
        result = await auth_service.get_email_from_refresh_token(self.wrong_token)
        self.assertRaises(HTTPException)

    async def test_get_current_user(self):
        ...

    async def test_create_email_token(self):
        token = await auth_service.create_email_token(data={"sub": "test"}, expires_delta=30)
        self.assertIsInstance(token, str)

    async def test_get_email_from_token(self):
        result = await auth_service.get_email_from_token(self.refresh_token)
        self.assertEqual(result, self.email)
    

if __name__ == '__main__':
    unittest.main()
