from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    logger.info("Initializing database...")
    settings.create_directories()
    
    # Import models to ensure they're registered with Base
    from src.models import File, Content, SearchIndex
    
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully") 