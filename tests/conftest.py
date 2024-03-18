import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock

from main import app
from src.models.models import Base
# from src.models.schemas import UserModel
from src.models.db import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database for tests

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client(session) -> TestClient:
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()       # TDOD: fix AttributeError: 'function' object has no attribute 'close' 

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def user():
    return {"username": "biakabuka", 
            "email": "buka@example.com", 
            "password": "123456789"}

# @pytest.fixture(scope="module", autouse=True)
# def patch_fastapi_limiter(monkeypatch):
#     monkeypatch.setattr("src.services.email.send_email", mock_send_email)
#     monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
#     monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
#     monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock()) 
