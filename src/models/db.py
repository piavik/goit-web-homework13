"""
Creates database connection Session object
"""

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings

db_uri = settings.sqlalchemy_database_url

engine = create_engine(db_uri, echo=True) 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    """
    Get database session object

    Yields:
        Session: DB session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()