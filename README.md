# AgroCredit Insight

Sistema de análisis y diagnóstico de brechas en crédito productivo rural para Colombia, Ecuador y Paraguay entre 2019 y 2024.

## Integrantes

| Nombre | Rol(documento) |Aportes
Jacobo Rincon-Pruebas/Experencia de usuario-
Luisa Gutierrez-Diseño-
Valery Ortegon-Gerencia/Documentación-

## Estructura del proyecto

- `backend/`: API con FastAPI.
- `frontend/`: dashboard en Streamlit.
- `sql/`: scripts SQL.
- `docs/`: documentación.
- `evidencias/`: capturas del progreso.

## Cómo ejecutar la base de datos

1. Crear una base de datos en PostgreSQL llamada `proyecto_datos`.
2. Abrir pgAdmin.
3. Ejecutar `sql/01_script_maestro.sql`.
4. Ejecutar `sql/02_tablas_extra.sql`.
5. Ejecutar `sql/03_vistas.sql`.

## Cómo ejecutar el backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
