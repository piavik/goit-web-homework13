import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.models.models import User
from src.models.schemas import UserModel
import src.services.users as users


class TestUser(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJleGFtcGxlQGV4YW1wbGUuY29tIiwiaWF0IjoxNzEwNjQwNTg4LCJleHAiOjE3MTEyNDUzODgsInNjb3BlIjoicmVmcmVzaF90b2tlbiJ9.DA4Zt7mGHhvQUwLShMQyz4l-Ai9cGuAaqPOTsVP3Yv8"
        self.url = "https://test.com"
        self.email = "example@example.com"
        self.body = UserModel(
            username = "test_user",
            email = self.email,
            password = "Password!2345"
        )

    async def test_get_user_by_email_ok(self):
        self.session.query().filter().first.return_value = self.user
        result = await users.get_user_by_email(email=self.email, db=self.session)
        self.assertEqual(result, self.user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await users.get_user_by_email(email=self.email, db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        result = await users.create_user(body=self.body, db=self.session)
        self.assertEqual(result.username, self.body.username)
        self.assertEqual(result.email, self.body.email)
        self.assertEqual(result.password, self.body.password)
    
    async def test_update_token(self):
        self.session.query().filter().first.return_value = self.user
        await users.update_token(user=self.user, token=self.refresh_token, db=self.session)
        self.assertIsInstance(self.user.refresh_token, str)

    async def test_confirmed_email(self):
        user = User(email=self.email)
        self.session.query().filter().first.return_value = user
        await users.confirmed_email(email=self.email, db=self.session)
        self.assertEqual(user.confirmed, True)
    
    async def test_avatar_user(self):
        result = await users.update_avatar(email=self.email, url=self.url, db=self.session)
        self.assertEqual(result.avatar, self.url)


if __name__ == '__main__':
    unittest.main()
