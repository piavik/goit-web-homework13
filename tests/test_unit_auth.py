import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session


from src.services.auth import auth_service
from src.models.models import User

class TestAuth(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_signup(self):
        ...
    
    async def test_login(self):
        ...

    async def test_refresh(self):
        ...

    async def test_confirmed_email(self):
        ...

    async def test_request_email(self):
        ...

if __name__ == '__main__':
    unittest.main()
