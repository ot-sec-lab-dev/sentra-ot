# SENTRA OT — OT Assessment Engine PRO v2.1

> **OT Security Assessment Automation** — Cliente → Assessment → Risk Engine → AI Report Builder → Executive Dashboard → Roadmap

Piloto real en **Coria del Río** (Sevilla) para evaluación de ciberseguridad OT según **IEC 62443 / NIST CSF**.

![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Postgres](https://img.shields.io/badge/Postgres-15-316192)
![Python](https://img.shields.io/badge/Python-3.12-3776AB)
![Status](https://img.shields.io/badge/Status-Pilot%20Coria%20OK-brightgreen)

### 🎯 Qué hace

- **Auth protegida** `admin / sentra2024` con sesiones seguras (SessionMiddleware lax)
- **Asset Discovery** + **Asset Risk Engine** + **Baseline Compliance**
- **Interview & Questionnaire Engine** (frameworks: IEC62443, NIST, etc.)
- **Risk Scoring** automático con desglose por frameworks
- **AI Executive Summary** (resumen ejecutivo generado por IA)
- **Report Engine** HTML PRO (156KB vendible) + PDF
- **Roadmap Generator** con fases, horas y costes
- **Executive Dashboard** PRO v2.1 con logo optimizado 9.7KB webp

### 🏗️ Arquitectura

```
Browser (login) → FastAPI (main.py) → Postgres (frameworks, clients, assessments)
                → modules/
                    controls_catalog.py → carga IEC62443
                    asset_discovery.py
                    risk_engine.py
                    report_engine.py → /app/output/*.html
                    roadmap_engine.py
                    ai_engine.py
                → n8n (automatización opcional)
```

### 🚀 Quick Start

```bash
cd sentra-ot
docker-compose down -v  # primera vez limpia
docker-compose up -d --build
# espera 10s
docker-compose logs -f sentra_assessment_engine
# debe salir: Application startup complete. Uvicorn running on http://0.0.0.0:8000
```

Abrir: http://127.0.0.1:8000/login
User: `admin` Pass: `sentra2024` (definido en .env → ADMIN_USER/ADMIN_PASS)

### 🔧 FIX v2.1.2 aplicado

- **Startup crea tablas si no existen** → evita `relation "frameworks" does not exist`
- `Base.metadata.create_all(bind=engine)` + `CREATE TABLE IF NOT EXISTS`
- SessionMiddleware con `same_site="lax", https_only=False` → login no entra en bucle
- Logo `logo_512.webp` con fallback + mounts únicos (fix carga infinita)

### 📁 Estructura

```
app/
  main.py (19KB CORREGIDO v2.1.2)
  db.py / database.py
  models.py
  modules/
    controls_catalog.py
    ...
  static/logo_512.webp
  templates/login.html
  output/ → informes generados
docker-compose.yml
Dockerfile
requirements.txt
```

### 🔐 Env

```
SECRET_KEY=sentra-ot-super-secret-2024-coria-piloto-v2
ADMIN_USER=admin
ADMIN_PASS=sentra2024
OUTPUT_DIR=output
```

### 📊 Demo Dashboard

`/dashboard-view` → lista assessments + botones Informe HTML PRO / PDF / JSON

### 🛣️ Roadmap

- [x] v2.0 PRO base
- [x] v2.1 AUTH + login.html
- [x] v2.1.1 fix logo webp + mounts
- [x] v2.1.2 fix BD frameworks
- [ ] v2.2 Multi-cliente + RBAC
- [ ] v2.3 Export PDF con WeasyPrint premium

---
**SENTRA OT · CONFIDENTIAL — PILOTO CORIA DEL RÍO · OT Security Assessment Automation**
