from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

# Singleton del cliente — se inicializa en el lifespan de FastAPI
_client: AsyncIOMotorClient | None = None


def init_client() -> None:
    """Inicializa el cliente Motor. Llamar en lifespan startup."""
    global _client
    _client = AsyncIOMotorClient(settings.MONGODB_URL)


def close_client() -> None:
    """Cierra el cliente Motor. Llamar en lifespan shutdown."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_motor_client() -> AsyncIOMotorClient:
    if _client is None:
        raise RuntimeError("Motor client no inicializado. Verifica el lifespan.")
    return _client


def get_db() -> AsyncIOMotorDatabase:
    """Dependencia FastAPI: inyecta la base de datos en cada endpoint."""
    return get_motor_client()[settings.DB_NAME]


async def check_connection() -> bool:
    """Ping a MongoDB para el health-check."""
    try:
        await get_motor_client().admin.command("ping")
        return True
    except Exception:
        return False
