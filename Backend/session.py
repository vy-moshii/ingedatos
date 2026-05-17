from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # Verifica la conexión antes de usarla
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency de FastAPI para inyectar sesión de BD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_connection() -> bool:
    """Verifica que la BD esté accesible (usado en health-check)."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
