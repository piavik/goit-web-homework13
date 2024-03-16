import unittest
from unittest.mock import MagicMock

from datetime import datetime, timedelta
from fastapi import Depends
from sqlalchemy.orm import Session
from libgravatar import Gravatar

from src.models.models import User
from src.models.schemas import UserModel


class TestUser(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email_ok(self):
        ...

    async def test_get_user_by_email_not_found(self):
        ...

    async def test_create_user(self):
        ...


    async def test_update_token(self):
        ...



    async def test_read_users_me(self):
        ...
    
    async def test_avatar_user(self):
        ...


if __name__ == '__main__':
    unittest.main()
