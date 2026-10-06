from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings
import logging

logger = logging.getLogger(__name__)

try:
    # Simple engine creation for Vercel serverless
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    if engine.dialect.name == "sqlite":
        @event.listens_for(engine, "connect")
        def enable_sqlite_foreign_keys(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Error creating database engine: {e}")
    raise

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(error)) from error
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="Database relationship or assessment constraint prevents this change") from error
    finally:
        db.close()
