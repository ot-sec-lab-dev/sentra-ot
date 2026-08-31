"""
SentraOT — OT Assessment Engine PRO v2.1 + AUTH
API FastAPI que orquesta los motores del Assessment Engine:
  Cliente → Assessment → Risk Engine → AI Report Builder →
  Executive Dashboard → Roadmap Generator

v2.1: Añadido Auth admin/sentra2024 + login.html + dashboard protegido
FIX v2.1.1: Logo webp 9.7KB + mounts únicos sin duplicar + sin carga infinita
"""

from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy import text
from jinja2 import Environment, FileSystemLoader
from starlette.middleware.sessions import SessionMiddleware
import os

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

app = FastAPI(title="SentraOT — OT Assessment Engine PRO v2.1 AUTH")

# ---------- AUTH CONFIG ----------
SECRET_KEY = os.getenv("SECRET_KEY", "sentra-ot-super-secret-2024-coria-piloto-v2")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "sentra2024")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=8*3600)

def require_login(request: Request):
    if not request.session.get("user"):
        raise HTTPException(status_code=302, headers={"Location":"/login"})

def check_login(request: Request):
    return request.session.get("user")

# ---------- FIX v2.1.1: STATIC Y OUTPUT ÚNICOS (ANTES DUPLICADO 5 VECES) ----------
STATIC_DIR = None
for cand in ["static", "/app/static", "app/static"]:
    if os.path.isdir(cand):
        STATIC_DIR = cand
        break

if STATIC_DIR:
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    print(f"[FIX] Static montado desde: {STATIC_DIR}")
else:
    print("[FIX] WARNING: No existe carpeta static - crea static/logo_512.webp")

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output")
for cand in [OUTPUT_DIR, "/app/output", "app/output", "output"]:
    if os.path.isdir(cand):
        OUTPUT_DIR = cand
        break

os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")
print(f"[FIX] Output montado desde: {OUTPUT_DIR}")


# Jinja env
template_dir = "templates" if os.path.exists("templates") else "/app/templates"
jinja_env = Environment(loader=FileSystemLoader(template_dir))


@app.on_event("startup")
def startup():
    cargar_catalogo()

# ---------------------------------------------------------------
# AUTH ROUTES - NUEVO v2.1
# ---------------------------------------------------------------

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    try:
        template = jinja_env.get_template("login.html")
        return HTMLResponse(template.render(error=None))
    except:
        # fallback si no existe login.html
        return HTMLResponse(f"""
        <html><body style="font-family:Segoe UI;background:#0a1931;display:grid;place-items:center;height:100vh">
        <form method="post" action="/login" style="background:#fff;padding:32px;border-radius:12px;width:360px">
        <h2>SENTRA OT Login</h2><p style="color:#64748b;font-size:13px">admin / sentra2024</p>
        <input name="username" placeholder="admin" style="width:100%;padding:12px;margin:10px 0" required>
        <input name="password" type="password" placeholder="password" style="width:100%;padding:12px;margin:10px 0" required>
        <button style="width:100%;padding:12px;background:#0a1931;color:#fff;border:none;border-radius:8px">Entrar</button>
        </form></body></html>
        """)

@app.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        request.session["user"] = username
        return RedirectResponse("/dashboard-view", status_code=302)
    try:
        template = jinja_env.get_template("login.html")
        return HTMLResponse(template.render(error="Usuario o contraseña incorrectos"), status_code=401)
    except:
        return HTMLResponse("Usuario o contraseña incorrectos - <a href='/login'>Volver</a>", status_code=401)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

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
def crear_cliente(cliente: ClienteIn, request: Request):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
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
def crear_assessment(assessment: AssessmentIn, request: Request):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
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
def catalogo_controles(request: Request, framework: str | None = None):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
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
def descubrir_activos(assessment_id: int, data: ActivosIn, request: Request):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    return asset_discovery.registrar_activos(assessment_id, data.activos)


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
def registrar_entrevista(assessment_id: int, hallazgo: HallazgoIn, request: Request):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    try:
        return interview_engine.registrar_respuesta_entrevista(
            assessment_id, hallazgo.model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------
# Questionnaire Engine
# ---------------------------------------------------------------

class CuestionarioIn(BaseModel):
    respuestas: list[dict]


@app.post("/assessments/{assessment_id}/questionnaire")
def registrar_cuestionario(assessment_id: int, cuestionario: CuestionarioIn, request: Request):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    return questionnaire.registrar_cuestionario(assessment_id, cuestionario.respuestas)


# ---------------------------------------------------------------
# Asset Baselines
# ---------------------------------------------------------------

@app.post("/assets/{asset_id}/baselines")
def registrar_baselines(asset_id: int, data: BaselinesIn, request: Request):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    return asset_baseline_engine.registrar_baselines(asset_id, data.baselines)


@app.get("/assets/{asset_id}/baselines")
def obtener_baselines(asset_id: int, request: Request):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    return asset_baseline_engine.obtener_baselines(asset_id)


# ---------------------------------------------------------------
# Risk Engine
# ---------------------------------------------------------------

@app.post("/assessments/{assessment_id}/risk-score")
def calcular_riesgo(assessment_id: int, request: Request):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    try:
        return risk_engine.calcular_riesgo(assessment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------
# Roadmap Generator
# ---------------------------------------------------------------

@app.post("/assessments/{assessment_id}/roadmap")
def generar_roadmap(assessment_id: int, request: Request):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    return {"roadmap": roadmap_engine.generar_roadmap(assessment_id)}


# ---------------------------------------------------------------
# Asset Risk Engine
# ---------------------------------------------------------------

@app.post("/assessments/{assessment_id}/asset-risk")
def calcular_riesgo_activos(assessment_id: int, request: Request):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    return {"assets": asset_risk_engine.calcular_riesgo_activos(assessment_id)}


@app.get("/assessments/{assessment_id}/assets/dashboard")
def dashboard_activos(assessment_id: int, request: Request):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    return {"assets": asset_dashboard.obtener_dashboard_activos(assessment_id)}


# ---------------------------------------------------------------
# AI Report Builder
# ---------------------------------------------------------------

@app.post("/assessments/{assessment_id}/report")
def generar_informe(assessment_id: int, request: Request, usar_ia: bool = True, formato: str = "html"):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    resumen = ""
    if usar_ia:
        try:
            resumen = ai_engine.generar_resumen_ejecutivo(assessment_id)
        except Exception:
            resumen = ""
    try:
        resultado = report_engine.generar_informe(
            assessment_id, resumen_ejecutivo=resumen, formato=formato
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------
# Executive Dashboard API (JSON)
# ---------------------------------------------------------------

@app.get("/assessments/{assessment_id}/dashboard")
def dashboard_ejecutivo(assessment_id: int, request: Request):
    if not check_login(request):
        raise HTTPException(status_code=401, detail="No autorizado")
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
            "hallazgos_criticos": len([r for r in top_riesgos if r[2] >= 8]),
            "hallazgos_totales": len(top_riesgos),
            "fases_roadmap": len(roadmap_resumen),
        },
        "top_riesgos": [
            {"codigo": r[0], "nombre": r[1], "criticidad": r[2], "estado": r[3]}
            for r in top_riesgos
        ],
        "roadmap": [
            {"fase": r[0], "items": r[1], "horas": r[2]} for r in roadmap_resumen
        ],
    }


# ---------------------------------------------------------------
# Executive Dashboard VIEW (HTML Visual - RECUPERADO PRO v2 + AUTH + FIX LOGO)
# ---------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def root_redirect(request: Request):
    if not check_login(request):
        return RedirectResponse("/login", status_code=302)
    return """
    <html><head><meta http-equiv="refresh" content="0; url=/dashboard-view"></head>
    <body>Redirigiendo a <a href="/dashboard-view">Dashboard</a></body></html>
    """

@app.get("/dashboard-view", response_class=HTMLResponse)
def dashboard_view(request: Request):
    """Dashboard visual PRO para cliente - recuperado y mejorado + AUTH"""
    if not check_login(request):
        return RedirectResponse("/login", status_code=302)
    try:
        with engine.begin() as conn:
            assessments = conn.execute(
                text("""
                    SELECT a.id, a.nombre, c.nombre as cliente, 
                           rs.score, rs.nivel
                    FROM assessments a
                    JOIN clients c ON a.client_id = c.id
                    LEFT JOIN (
                        SELECT DISTINCT ON (assessment_id) 
                               assessment_id, score, nivel
                        FROM risk_scores ORDER BY assessment_id, calculated_at DESC
                    ) rs ON rs.assessment_id = a.id
                    ORDER BY a.id DESC
                """)
            ).fetchall()
    except:
        assessments = []

    rows_html = ""
    for aid, anombre, cliente, score, nivel in assessments:
        if not score:
            score_pct = "N/A"
        elif score > 10:
            score_pct = f"{score:.1f}%"
        else:
            score_pct = f"{(score*10):.1f}%" if score > 5 else f"{(score*20):.1f}%"
        nivel_color = "#0e3b5c" if nivel == "Bajo" else "#e67e22" if nivel == "Medio" else "#c0392b"
        rows_html += f"""
        <tr>
            <td><strong>#{aid}</strong></td>
            <td>{cliente}</td>
            <td>{anombre}</td>
            <td><span class="badge" style="background:{nivel_color}">{score_pct} {nivel or ''}</span></td>
            <td>
                <button onclick="generarInforme({aid}, 'html')" class="btn btn-primary">Informe HTML PRO</button>
                <button onclick="generarInforme({aid}, 'pdf')" class="btn btn-dark">PDF</button>
                <button onclick="verDashboard({aid})" class="btn btn-outline">JSON</button>
            </td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sentra OT - Executive Dashboard PRO v2.1 AUTH FIXED</title>
<style>
*{{box-sizing:border-box}} body{{margin:0;font-family:Inter,Helvetica,Arial,sans-serif;background:#f6f8fa;color:#1a2332}}
.header{{background:#0a1931;color:white;padding:20px 32px;display:flex;align-items:center;justify-content:space-between;border-bottom:4px solid #00d4c8}}
.header img{{height:42px;width:auto;display:block}} .header h1{{margin:0;font-size:18px;letter-spacing:1px}}
.container{{max-width:1200px;margin:32px auto;padding:0 24px}}
.card{{background:white;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.08);padding:24px;margin-bottom:24px;border:1px solid #e1e8ed}}
.table{{width:100%;border-collapse:collapse}} .table th{{text-align:left;padding:12px 8px;border-bottom:2px solid #0a1931;font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#5a6c7d}} .table td{{padding:14px 8px;border-bottom:1px solid #eef2f7;font-size:13px}}
.badge{{color:white;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700}}
.btn{{padding:8px 14px;border-radius:6px;border:none;cursor:pointer;font-size:12px;font-weight:600;margin-right:6px;transition:all 0.2s}} .btn-primary{{background:#0e3b5c;color:white}} .btn-primary:hover{{background:#00d4c8;color:#0a1931}} .btn-dark{{background:#1a2332;color:white}} .btn-outline{{background:white;border:1px solid #cbd6e2}} .btn-outline:hover{{background:#f6f8fa}}
.status{{margin-top:16px;padding:12px;background:#e8f8f5;border-radius:8px;border-left:4px solid #00d4c8;font-size:13px;display:none}}
.footer{{text-align:center;padding:24px;color:#89939b;font-size:11px}}
.logout{{color:#00d4c8;text-decoration:none;font-size:12px;border:1px solid #00d4c8;padding:6px 12px;border-radius:20px}}
.logout:hover{{background:#00d4c8;color:#0a1931}}
</style>
</head>
<body>
<div class="header">
  <div style="display:flex;align-items:center;gap:16px">
    <!-- FIX v2.1.1: webp 9.7KB con fallback, nunca display:none -->
    <img src="/static/logo_512.webp" onerror="this.onerror=null; this.src='/static/logo.png'; this.onerror=function(){{this.src='/static/logo_512.png';}}" alt="Sentra OT">
    <h1>SENTRA OT — EXECUTIVE DASHBOARD PRO v2.1 AUTH FIXED</h1>
  </div>
  <div style="display:flex;align-items:center;gap:16px">
    <span style="font-size:11px;opacity:0.8">admin</span>
    <a href="/logout" class="logout">Salir</a>
  </div>
</div>

<div class="container">
  <div class="card">
    <h2 style="margin:0 0 8px 0;color:#0a1931">Assessments</h2>
    <p style="margin:0 0 20px 0;color:#5a6c7d;font-size:13px">Selecciona un assessment y genera el informe PRO vendible. Protegido con Auth. FIX logo + sin carga infinita.</p>
    <table class="table">
      <thead><tr><th>ID</th><th>Cliente</th><th>Assessment</th><th>Score</th><th>Acciones</th></tr></thead>
      <tbody>{rows_html or '<tr><td colspan=5 style="text-align:center;color:#89939b;padding:32px">No hay assessments. Crea uno en POST /assessments</td></tr>'}</tbody>
    </table>
    <div id="status" class="status"></div>
  </div>

  <div class="card">
    <h3 style="margin:0 0 12px 0">Último informe bueno (ID 7)</h3>
    <code>/app/output/sentra_os_informe_1_20260828161713.html (156KB PRO)</code>
    <p style="font-size:12px;color:#5a6c7d">Ahora con Auth activo: admin / sentra2024 - FIX aplicado</p>
  </div>
</div>

<div class="footer">SENTRA OT · CONFIDENTIAL — PRO v2.1 AUTH FIXED · admin / sentra2024</div>

<script>
function showStatus(msg, isError=false){{
  const el=document.getElementById('status'); el.style.display='block';
  el.style.borderLeftColor=isError?'#c0392b':'#00d4c8'; el.style.background=isError?'#fdeaea':'#e8f8f5';
  el.innerHTML=msg;
}}
async function generarInforme(id, formato){{
  showStatus(`⏳ Generando informe ${{formato.toUpperCase()}} para assessment ${{id}}... IA: true`);
  try{{
    const res=await fetch(`/assessments/${{id}}/report?usar_ia=true&formato=${{formato}}`,{{method:'POST'}});
    const data=await res.json();
    if(res.ok){{
      const fname = data.path.split('/').pop();
      showStatus(`✅ Generado: <strong>${{fname}}</strong> · Score: ${{data.score}} (${{data.score_100}}%) · <a href="/output/${{fname}}" target="_blank">Abrir</a>`);
      setTimeout(()=>{{ window.open('/output/'+fname,'_blank'); }}, 400);
    }} else {{
      showStatus(`❌ Error: ${{data.detail || JSON.stringify(data)}}`, true);
    }}
  }} catch(e){{
    showStatus(`❌ Error de red: ${{e.message}}`, true);
  }}
}}
function verDashboard(id){{ window.open(`/assessments/${{id}}/dashboard`,'_blank'); }}
</script>
</body>
</html>
    """
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
