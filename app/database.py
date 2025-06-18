from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql://avnadmin:AVNS_E4qNk5OdgfihQe_xGD9@mysql-lucid-redis-demo.j.aivencloud.com:11709/defaultdb?ssl_mode=REQUIRED") # huh
# DATABASE_URL = "mysql://avnadmin:AVNS_E4qNk5OdgfihQe_xGD9@mysql-lucid-redis-demo.j.aivencloud.com:11709/defaultdb?ssl_mode=REQUIRED"
# DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping = True,
    pool_recycle = 300,
    echo = False
)

# engine = create_engine(
#     DATABASE_URL,
#     connect_args={"check_same_thread": False},  # Required for SQLite with SQLAlchemy in multithreaded environments like FastAPI
#     echo=False
# )


SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()