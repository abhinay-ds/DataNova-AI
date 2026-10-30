from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import os


BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

default_db_dir = settings.DATA_DIR if settings.DATA_DIR else BACKEND_DIR
os.makedirs(default_db_dir, exist_ok=True)
default_db_path = os.path.join(default_db_dir, "datanova.db").replace("\\", "/")

DATABASE_URL = settings.DATABASE_URL or os.getenv(
    "DATABASE_URL",
    f"sqlite:///{default_db_path}",
)

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
