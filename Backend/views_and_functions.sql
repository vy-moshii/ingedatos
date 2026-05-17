-- =============================================================================
-- AgroCredit Insight — Vistas y funciones SQL
-- Este script debe ejecutarse en la BD antes de levantar la API.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- VISTA: vw_paises
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_paises AS
SELECT
    p.id          AS pais_id,
    p.nombre,
    p.codigo,
    p.region
FROM paises p;

-- ---------------------------------------------------------------------------
-- VISTA: vw_indicadores_findex
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_indicadores_findex AS
SELECT
    f.id,
    f.pais_id,
    f.anio,
    f.cuenta_bancaria_pct,
    f.credito_formal_pct,
    f.ahorro_formal_pct,
    f.uso_movil_financiero_pct,
    f.brecha_genero_cuenta_pct,
    f.poblacion_rural_sin_cuenta_pct
FROM indicadores_findex f;

-- ---------------------------------------------------------------------------
-- VISTA: vw_oferta_credito
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_oferta_credito AS
SELECT
    o.id,
    o.pais_id,
    o.anio,
    o.institucion,
    o.tipo_institucion,
    o.cartera_agricola_mn,
    o.num_creditos
FROM oferta_credito o;

-- ---------------------------------------------------------------------------
-- VISTA: vw_tipo_credito
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_tipo_credito AS
SELECT
    t.id,
    t.pais_id,
    t.anio,
    t.tipo_credito,
    t.monto_promedio_mn,
    t.participacion_pct
FROM tipo_credito t;

-- ---------------------------------------------------------------------------
-- VISTA: vw_rural_urbano
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_rural_urbano AS
SELECT
    r.id,
    r.pais_id,
    r.anio,
    r.zona,
    r.acceso_credito_formal_pct,
    r.uso_credito_informal_pct,
    r.tasa_bancarizacion_pct
FROM rural_urbano r;

-- ---------------------------------------------------------------------------
-- VISTA: vw_datos_faltantes
-- Detecta NULLs en indicadores_findex agrupados por país y año.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_datos_faltantes AS
SELECT
    p.id                              AS pais_id,
    p.nombre                          AS pais,
    f.anio,
    'indicadores_findex'              AS tabla,
    unnest(ARRAY[
        'cuenta_bancaria_pct',
        'credito_formal_pct',
        'ahorro_formal_pct',
        'uso_movil_financiero_pct',
        'brecha_genero_cuenta_pct',
        'poblacion_rural_sin_cuenta_pct'
    ])                                AS campo,
    SUM(CASE
        WHEN f.cuenta_bancaria_pct            IS NULL THEN 1
        WHEN f.credito_formal_pct             IS NULL THEN 1
        WHEN f.ahorro_formal_pct              IS NULL THEN 1
        WHEN f.uso_movil_financiero_pct       IS NULL THEN 1
        WHEN f.brecha_genero_cuenta_pct       IS NULL THEN 1
        WHEN f.poblacion_rural_sin_cuenta_pct IS NULL THEN 1
        ELSE 0
    END)                              AS total_nulos
FROM indicadores_findex f
JOIN paises p ON p.id = f.pais_id
GROUP BY p.id, p.nombre, f.anio;

-- ---------------------------------------------------------------------------
-- VISTA: vw_metadatos
-- Catálogo de variables. Requiere tabla metadatos en la BD.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_metadatos AS
SELECT
    m.tabla,
    m.campo,
    m.descripcion,
    m.unidad,
    m.fuente
FROM metadatos m;

-- ---------------------------------------------------------------------------
-- FUNCIÓN: fn_diagnostico(pais_id INT, anio INT)
-- Devuelve una fila con el diagnóstico consolidado.
-- Personalizar la lógica según los criterios del equipo.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_diagnostico(p_pais_id INT, p_anio INT)
RETURNS TABLE (
    pais_id                  INT,
    anio                     INT,
    nivel_inclusion          TEXT,
    score_inclusion          NUMERIC,
    brecha_genero            TEXT,
    acces_rural              TEXT,
    oferta_credito_agricola  TEXT,
    resumen                  TEXT
)
LANGUAGE plpgsql AS $$
DECLARE
    v_cuenta    NUMERIC;
    v_credito   NUMERIC;
    v_brecha    NUMERIC;
    v_rural     NUMERIC;
    v_score     NUMERIC;
BEGIN
    SELECT
        COALESCE(f.cuenta_bancaria_pct, 0),
        COALESCE(f.credito_formal_pct, 0),
        COALESCE(f.brecha_genero_cuenta_pct, 0),
        COALESCE(f.poblacion_rural_sin_cuenta_pct, 0)
    INTO v_cuenta, v_credito, v_brecha, v_rural
    FROM indicadores_findex f
    WHERE f.pais_id = p_pais_id AND f.anio = p_anio
    LIMIT 1;

    IF NOT FOUND THEN
        RETURN;  -- Sin datos: la API devuelve 404
    END IF;

    v_score := ROUND((v_cuenta * 0.4 + v_credito * 0.6), 2);

    RETURN QUERY SELECT
        p_pais_id,
        p_anio,
        CASE
            WHEN v_score >= 70 THEN 'Alto'
            WHEN v_score >= 40 THEN 'Medio'
            ELSE 'Bajo'
        END,
        v_score,
        CASE WHEN v_brecha > 15 THEN 'Brecha significativa' ELSE 'Brecha moderada' END,
        CASE WHEN v_rural > 50  THEN 'Acceso limitado'      ELSE 'Acceso aceptable' END,
        (
            SELECT CASE
                WHEN SUM(o.cartera_agricola_mn) > 1000000 THEN 'Oferta amplia'
                WHEN SUM(o.cartera_agricola_mn) > 100000  THEN 'Oferta media'
                ELSE 'Oferta reducida'
            END
            FROM oferta_credito o
            WHERE o.pais_id = p_pais_id AND o.anio = p_anio
        ),
        'Diagnóstico generado automáticamente para país ' || p_pais_id::TEXT || ', año ' || p_anio::TEXT;
END;
$$;

-- ---------------------------------------------------------------------------
-- FUNCIÓN: fn_recomendaciones(pais_id INT, anio INT)
-- Devuelve un conjunto de recomendaciones priorizadas.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_recomendaciones(p_pais_id INT, p_anio INT)
RETURNS TABLE (
    orden          INT,
    categoria      TEXT,
    recomendacion  TEXT,
    prioridad      TEXT
)
LANGUAGE plpgsql AS $$
DECLARE
    v_credito NUMERIC;
    v_rural   NUMERIC;
    v_brecha  NUMERIC;
BEGIN
    SELECT
        COALESCE(f.credito_formal_pct, 0),
        COALESCE(f.poblacion_rural_sin_cuenta_pct, 0),
        COALESCE(f.brecha_genero_cuenta_pct, 0)
    INTO v_credito, v_rural, v_brecha
    FROM indicadores_findex f
    WHERE f.pais_id = p_pais_id AND f.anio = p_anio
    LIMIT 1;

    IF NOT FOUND THEN
        RETURN;
    END IF;

    IF v_credito < 40 THEN
        RETURN QUERY SELECT 1, 'Crédito formal',
            'Ampliar programas de crédito formal en el sector agrícola',
            'Alta'::TEXT;
    END IF;

    IF v_rural > 50 THEN
        RETURN QUERY SELECT 2, 'Inclusión rural',
            'Implementar puntos de acceso financiero en zonas rurales',
            'Alta'::TEXT;
    END IF;

    IF v_brecha > 15 THEN
        RETURN QUERY SELECT 3, 'Equidad de género',
            'Diseñar productos financieros específicos para mujeres rurales',
            'Media'::TEXT;
    END IF;

    RETURN QUERY SELECT 4, 'General',
        'Fortalecer educación financiera en comunidades agrícolas',
        'Media'::TEXT;
END;
$$;

-- ---------------------------------------------------------------------------
-- TRIGGER EJEMPLO: auditoría de cambios en indicadores_findex
-- La API activa este trigger automáticamente en INSERT / UPDATE.
-- ---------------------------------------------------------------------------

-- Tabla de auditoría (crear si no existe)
CREATE TABLE IF NOT EXISTS auditoria_indicadores (
    id          SERIAL PRIMARY KEY,
    operacion   CHAR(1) NOT NULL,   -- I / U / D
    tabla       TEXT    NOT NULL,
    registro_id INT,
    usuario     TEXT    DEFAULT current_user,
    fecha       TIMESTAMPTZ DEFAULT now()
);

CREATE OR REPLACE FUNCTION trg_fn_audit_indicadores()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO auditoria_indicadores (operacion, tabla, registro_id)
    VALUES (
        LEFT(TG_OP, 1),
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id)
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_audit_indicadores ON indicadores_findex;
CREATE TRIGGER trg_audit_indicadores
AFTER INSERT OR UPDATE OR DELETE ON indicadores_findex
FOR EACH ROW EXECUTE FUNCTION trg_fn_audit_indicadores();
