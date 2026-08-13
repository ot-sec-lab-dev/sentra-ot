"""
SentraOT — OT Assessment Engine
================================
API FastAPI que orquesta los motores del Assessment Engine:

  Cliente → Assessment → Risk Engine → AI Report Builder →
  Executive Dashboard → Roadmap Generator

Cada motor vive en su propio módulo (modules/) y es responsable de una
sola cosa. Esta API solo conecta las piezas y expone el flujo como
endpoints HTTP, listos para llamarse desde n8n.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from db import engine
from modules.controls_catalog import cargar_catalogo, listar_controles
from modules import (
    asset_discovery,
    asset_risk_engine,
    asset_baseline_engine,
    asset_dashboard,
    interview_engine,
    questionnaire,
    risk_engine,
    roadmap_engine,
    report_engine,
    ai_engine,
)

app = FastAPI(title="SentraOT — OT Assessment Engine")


@app.on_event("startup")
def startup():
    cargar_catalogo()


# ---------------------------------------------------------------
# Cliente / Assessment
# ---------------------------------------------------------------

class ClienteIn(BaseModel):
    nombre: str
    sector: str | None = None


class AssessmentIn(BaseModel):
    client_id: int
    nombre: str
    alcance: str | None = None


@app.post("/clients")
def crear_cliente(cliente: ClienteIn):
    with engine.begin() as conn:
        cid = conn.execute(
            text(
                "INSERT INTO clients (nombre, sector) "
                "VALUES (:n, :s) RETURNING id"
            ),
            {
                "n": cliente.nombre,
                "s": cliente.sector,
            },
        ).scalar()

    return {"client_id": cid}


@app.post("/assessments")
def crear_assessment(assessment: AssessmentIn):
    with engine.begin() as conn:
        aid = conn.execute(
            text(
                """INSERT INTO assessments (client_id, nombre, alcance)
                   VALUES (:cid, :n, :a) RETURNING id"""
            ),
            {
                "cid": assessment.client_id,
                "n": assessment.nombre,
                "a": assessment.alcance,
            },
        ).scalar()

    return {"assessment_id": aid}


@app.get("/controls")
def catalogo_controles(framework: str | None = None):
    return listar_controles(framework)


# ---------------------------------------------------------------
# Asset Discovery
# ---------------------------------------------------------------

class ActivosIn(BaseModel):
    activos: list[dict]


class BaselineIn(BaseModel):
    baseline_name: str
    expected_value: str | None = None
    current_value: str | None = None
    compliance: bool = False


class BaselinesIn(BaseModel):
    baselines: list[BaselineIn]


@app.post("/assessments/{assessment_id}/assets")
def descubrir_activos(
    assessment_id: int,
    data: ActivosIn,
):
    return asset_discovery.registrar_activos(
        assessment_id,
        data.activos,
    )


# ---------------------------------------------------------------
# Interview Engine
# ---------------------------------------------------------------

class HallazgoIn(BaseModel):
    framework: str
    codigo: str
    estado: str
    criticidad: int
    evidencia: str | None = None
    impacto: str | None = None
    quick_win: str | None = None
    coste_estimado: str | None = None
    horas: int | None = None
    asset_id: int | None = None


@app.post("/assessments/{assessment_id}/interview")
def registrar_entrevista(
    assessment_id: int,
    hallazgo: HallazgoIn,
):
    try:
        return interview_engine.registrar_respuesta_entrevista(
            assessment_id,
            hallazgo.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ---------------------------------------------------------------
# Questionnaire Engine
# ---------------------------------------------------------------

class CuestionarioIn(BaseModel):
    respuestas: list[dict]


@app.post("/assessments/{assessment_id}/questionnaire")
def registrar_cuestionario(
    assessment_id: int,
    cuestionario: CuestionarioIn,
):
    return questionnaire.registrar_cuestionario(
        assessment_id,
        cuestionario.respuestas,
    )


# ---------------------------------------------------------------
# Asset Baselines
# ---------------------------------------------------------------

@app.post("/assets/{asset_id}/baselines")
def registrar_baselines(
    asset_id: int,
    data: BaselinesIn,
):
    return asset_baseline_engine.registrar_baselines(
        asset_id,
        data.baselines,
    )


@app.get("/assets/{asset_id}/baselines")
def obtener_baselines(asset_id: int):
    return asset_baseline_engine.obtener_baselines(asset_id)


# ---------------------------------------------------------------
# Risk Engine
# ---------------------------------------------------------------

@app.post("/assessments/{assessment_id}/risk-score")
def calcular_riesgo(assessment_id: int):
    try:
        return risk_engine.calcular_riesgo(assessment_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ---------------------------------------------------------------
# Roadmap Generator
# ---------------------------------------------------------------

@app.post("/assessments/{assessment_id}/roadmap")
def generar_roadmap(assessment_id: int):
    return {
        "roadmap": roadmap_engine.generar_roadmap(assessment_id)
    }


# ---------------------------------------------------------------
# Asset Risk Engine
# ---------------------------------------------------------------

@app.post("/assessments/{assessment_id}/asset-risk")
def calcular_riesgo_activos(assessment_id: int):
    return {
        "assets": asset_risk_engine.calcular_riesgo_activos(
            assessment_id
        )
    }


@app.get("/assessments/{assessment_id}/assets/dashboard")
def dashboard_activos(assessment_id: int):
    return {
        "assets": asset_dashboard.obtener_dashboard_activos(
            assessment_id
        )
    }


# ---------------------------------------------------------------
# AI Report Builder
# ---------------------------------------------------------------

@app.post("/assessments/{assessment_id}/report")
def generar_informe(
    assessment_id: int,
    usar_ia: bool = True,
    formato: str = "html",
):
    resumen = ""

    if usar_ia:
        try:
            resumen = ai_engine.generar_resumen_ejecutivo(
                assessment_id
            )
        except Exception:
            resumen = ""

    try:
        resultado = report_engine.generar_informe(
            assessment_id,
            resumen_ejecutivo=resumen,
            formato=formato,
        )

        return resultado

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ---------------------------------------------------------------
# Executive Dashboard
# ---------------------------------------------------------------

@app.get("/assessments/{assessment_id}/dashboard")
def dashboard_ejecutivo(assessment_id: int):
    with engine.begin() as conn:
        score_row = conn.execute(
            text(
                """SELECT score, nivel, desglose, calculated_at
                   FROM risk_scores
                   WHERE assessment_id = :aid
                   ORDER BY calculated_at DESC
                   LIMIT 1"""
            ),
            {"aid": assessment_id},
        ).fetchone()

        top_riesgos = conn.execute(
            text(
                """SELECT c.codigo, c.nombre, ce.criticidad, ce.estado
                   FROM control_evaluations ce
                   JOIN controls c ON ce.control_id = c.id
                   WHERE ce.assessment_id = :aid
                     AND ce.estado != 'Implantado'
                   ORDER BY ce.criticidad DESC
                   LIMIT 5"""
            ),
            {"aid": assessment_id},
        ).fetchall()

        roadmap_resumen = conn.execute(
            text(
                """SELECT fase, COUNT(*), SUM(horas)
                   FROM roadmap_items
                   WHERE assessment_id = :aid
                   GROUP BY fase"""
            ),
            {"aid": assessment_id},
        ).fetchall()

    return {
        "assessment_id": assessment_id,
        "riesgo_global": {
            "score": score_row[0] if score_row else None,
            "nivel": score_row[1] if score_row else None,
            "frameworks": score_row[2] if score_row else {},
        },
        "indicadores": {
            "hallazgos_criticos": len(
                [r for r in top_riesgos if r[2] >= 8]
            ),
            "hallazgos_totales": len(top_riesgos),
            "fases_roadmap": len(roadmap_resumen),
        },
        "top_riesgos": [
            {
                "codigo": r[0],
                "nombre": r[1],
                "criticidad": r[2],
                "estado": r[3],
            }
            for r in top_riesgos
        ],
        "roadmap": [
            {
                "fase": r[0],
                "items": r[1],
                "horas": r[2],
            }
            for r in roadmap_resumen
        ],
    }


# ---------------------------------------------------------------
# Arranque del servidor
# ---------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )