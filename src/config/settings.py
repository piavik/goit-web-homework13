import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    sqlalchemy_database_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_token_ttl: int = 15 # minutes

    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_from_name: str
    mail_starttls: bool
    mail_ssl_tls: bool
    mail_use_credentials: bool
    mail_validate_certs: bool

    redis_host: str
    redis_port: int

    model_config = SettingsConfigDict(env_file=".env", extra='allow')

    # that is pydantic 1.x format
    # class Config:
    #     extra = Extra.allow
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"


settings = Settings()
