from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.database import engine, Base

# Crear tablas (si no existen) - normalmente ya están desde el script SQL
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AgroCredit Insight API",
    description="API para datos de crédito agropecuario e inclusión financiera en Colombia, Ecuador y Paraguay",
    version="1.0.0"
)

# Configurar CORS para permitir conexión desde Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "AgroCredit Insight API - Documentación en /docs"}