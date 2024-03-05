import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


config = configparser.ConfigParser()
config.read('config.ini')

post_engine = config.get('DB', 'engine')
post_user   = config.get('DB', 'user')
post_pass   = config.get('DB', 'pass')
post_host   = config.get('DB', 'host')
post_port   = config.get('DB', 'port')
post_db     = config.get('DB', 'db_name')

# ----- posgres connect -----
db_uri = f"""{post_engine}://{post_user}:{post_pass}@{post_host}:{post_port}/{post_db}"""
engine = create_engine(db_uri, echo=True) 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()