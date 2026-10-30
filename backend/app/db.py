from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def create_tables(target_engine=engine) -> None:
    Base.metadata.create_all(bind=target_engine)
    if target_engine.dialect.name == "sqlite":
        with target_engine.begin() as connection:
            columns = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(transactions)")}
            if "is_self_transfer" not in columns:
                connection.exec_driver_sql(
                    "ALTER TABLE transactions ADD COLUMN is_self_transfer BOOLEAN NOT NULL DEFAULT 0"
                )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
