import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session


from src.auth.auth import auth_service
from src.models.models import User


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        
    async def test_read_contacts(self):
        ...
    
    async def test_find_contacts_with_birthdays(self):
        ...
    
    async def test_find_contacts(self):
        ...

    async def test_read_contact(self):
        ...

    async def test_create_contact(self):
        ...

    async def test_update_contact(self):
        ...

    async def test_delete_contact(self):
        ...


if __name__ == '__main__':
    unittest.main()
