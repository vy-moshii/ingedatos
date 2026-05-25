# AgroCredit Insight

**AgroCredit Insight** es un proyecto de análisis y diagnóstico de brechas en crédito productivo rural, inclusión financiera y digitalización en Colombia, Ecuador y Paraguay (2019-2024).

## Qué ofrece

- Dashboard analítico construido con Streamlit.
- API REST con FastAPI para consulta de datos y métricas.
- Diagnóstico automático de brecha crediticia.
- Recomendaciones basadas en indicadores de inclusión financiera.
- Comparaciones por país y año.
- Exportación de resultados a CSV.

## Estructura del repositorio

- `Backend/`: API FastAPI, conexión PostgreSQL y modelos SQLAlchemy.
- `frontend/`: aplicación Streamlit, cliente de datos y páginas de análisis.
- `README.md`: documentación del proyecto.

## Requisitos

- Python 3.10+.
- PostgreSQL.
- `pip`.

## Configuración del entorno

### Backend

1. Crear un archivo `.env` en `Backend/`.
2. Agregar la variable de conexión a la base de datos:

```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/proyecto_datos
```

3. Instalar dependencias desde `Backend/`:

```bash
cd Backend
pip install -r requirements.txt
```

4. Ejecutar el backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Ver la documentación de la API en:

```text
http://localhost:8000/docs
```

### Frontend

1. Copiar `frontend/example_env.txt` a `frontend/.env`.
2. Ajustar si es necesario:

```env
AGROCREDIT_API_URL=http://localhost:8000/api/v1
AGROCREDIT_DATA_MODE=api
```

3. Instalar dependencias desde `frontend/`:

```bash
cd frontend
pip install -r requirements.txt
```

4. Ejecutar Streamlit:

```bash
streamlit run app.py
```

5. Abrir la app en:

```text
http://localhost:8501
```

## Funcionalidades principales

- Consultas por país y año.
- Comparación entre Colombia, Ecuador y Paraguay.
- Visualización de crédito agropecuario y datos Findex.
- Diagnóstico de brecha digital vs. crédito productivo.
- Recomendaciones por país.
- Descarga de datos filtrados.

## API disponibles

- `GET /api/v1/paises`
- `GET /api/v1/cartera/{pais_id}`
- `GET /api/v1/tipo_credito/{pais_id}`
- `GET /api/v1/findex`
- `GET /api/v1/oferta`
- `GET /api/v1/rural_urban`
- `GET /api/v1/diagnosticos`
- `GET /api/v1/recomendaciones`
- `GET /api/v1/missing`
- `GET /api/v1/fuentes`

## Notas

- El backend requiere que `DATABASE_URL` apunte a una instancia PostgreSQL válida.
- El proyecto crea modelos y tablas desde `Backend/app/main.py` con SQLAlchemy.
- Si dispone de datos cargados en PostgreSQL con las tablas esperadas, el dashboard los consumirá automáticamente.

## Contribuidores

- Jacobo Rincón — pruebas / experiencia de usuario
- Luisa Gutiérrez — diseño
- Valery Ortegon — gerencia / documentación
