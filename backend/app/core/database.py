from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@db:5432/business_db"
)

# Configure engine with connection pooling for production stability
# ponytail: pool_size and max_overflow tuned for moderate load (5-15 concurrent connections)
# pool_pre_ping checks connection health before use (avoids stale connections)
# pool_recycle closes/reopens connections after 1 hour (prevents transaction ID wraparound)
# pool_timeout raises error if no connection available within 30s (fails fast)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Register ORM tenant auto-filter event
from app.core.tenant_context import current_tenant_id  # noqa: E402, F401


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
