from sqlalchemy import Integer, Column, String, Date, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.schema import ForeignKey

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id            = Column(Integer, primary_key=True)
    first_name    = Column('name', String(50), nullable=False)
    last_name     = Column('surname', String(50), nullable=False)
    email         = Column('email', String(100), unique=True, nullable=False)
    phone         = Column('phone', String(15), unique=True, nullable=False)
    birthday      = Column('birthday', Date, nullable=False)
    notes         = Column('notes', String, nullable=True, default="")
    user_id       = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user          = relationship('User', backref='contacts')

class User(Base):
    __tablename__   = "users"
    id              = Column(Integer, primary_key=True)
    username        = Column('username', String(50), nullable=False)
    email           = Column('email', String(150), nullable=False, unique=True)
    password        = Column('hash', String(255), nullable=False)
    created_at      = Column('crated_at', DateTime, default=func.now())
    refresh_token   = Column(String(255), nullable=True)
    