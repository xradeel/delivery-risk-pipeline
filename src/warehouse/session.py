import os
from contextlib import contextmanager
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()

DATABASE_URL = URL.create(
    drivername="postgresql",
    username=os.getenv("WAREHOUSE_USER"),
    password=os.getenv("WAREHOUSE_PASSWORD"),
    host=os.getenv("WAREHOUSE_HOST"),
    port=int(os.getenv("WAREHOUSE_PORT")),
    database=os.getenv("WAREHOUSE_DB"),
)

# SQLAlchemy 2.0 Engine & Session factory
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
  """Declarative base class for data warehouse ORM models."""

  pass


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
  """Context manager for managing transaction lifecycle:

  - Yields session
  - Commits on completion
  - Rolls back automatically on error
  - Always closes connection
  """
  session = SessionLocal()
  try:
    yield session
    session.commit()
  except Exception:
    session.rollback()
    raise
  finally:
    session.close()