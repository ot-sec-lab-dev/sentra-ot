🛡 Sentra OS
AI-Powered OT Cybersecurity Assessment Platform
Assess · Discover · Prioritize · Remediate

Sentra OS is a modern OT cybersecurity platform that enables industrial organizations to assess cyber risk, discover industrial assets, manage IEC 62443 compliance and generate executive security reports from a single platform.

Version
Status
License
Python
FastAPI
Docker
PostgreSQL
IEC62443
MITRE ATT&CK ICS

Overview
Industrial organizations continue to face a common challenge: fragmented asset inventories, manual cybersecurity assessments, spreadsheet-based compliance tracking and disconnected reporting processes.

Sentra OS has been designed to centralize these activities into a single OT cybersecurity platform.

The platform enables industrial organizations, cybersecurity consultants and critical infrastructure operators to:

Discover and inventory industrial assets.
Assess cybersecurity posture using IEC 62443.
Correlate risks with MITRE ATT&CK for ICS.
Prioritize remediation actions based on business impact.
Generate executive reports automatically (PDF Pro vendible).
Build long-term cybersecurity roadmaps.
Rather than replacing existing OT security solutions, Sentra OS acts as an assessment and decision-support platform that helps organizations understand their current cybersecurity posture and continuously improve it.

Current Release
🚀 Latest Stable Release
Version: v0.8.0 — PRODUCTION READY

Highlights v0.8.0
✅ Executive Dashboard V2 — Vendible (http://localhost:8000/dashboard-view)
✅ PDF Reports Pro — Generación automática en ./output/
✅ Persistencia de Entregables — Volumen Docker output:/app/output
✅ Alembic Database Versioning
✅ Asset Discovery Engine
✅ Asset Risk Engine
✅ Asset Baseline Management
✅ Executive Reports
✅ Docker Deployment — 4 containers UP
✅ Render Cloud Deployment
Release Notes

https://github.com/juanjocaladoc/sentra-os/releases/latest

Key Features
Assessment
IEC 62443 Assessment Engine (17 controles, 5 niveles)
MITRE ATT&CK ICS Mapping
Automated Risk Scoring (0-5 y 0-100%)
Compliance Gap Analysis (7 implantados, 5 parciales, 5 no implantados)
Asset Management
Asset Discovery
Asset Inventory
Asset Risk Dashboard V2
Baseline Management
Reporting — NUEVO v0.8.0
Executive Reports V2 — Dashboard con logo Sentra, métricas y exportación limpia
PDF Pro — POST /assessments/{id}/report?formato=pdf → /app/output/sentra_os_informe_{id}_{timestamp}.pdf
Remediation Roadmaps con Quick Wins priorizados
HTML Reports para previsualización
Entregable Cliente: PDF de 5 páginas listo para facturar, guardado en ./output/ local
Platform
REST API (FastAPI)
Docker Deployment con volúmenes persistentes
PostgreSQL 16
Alembic Database Versioning
Render Cloud Deployment
Output Persistence: ./output:/app/output
AI (Roadmap)
Executive AI Summaries
AI-assisted Risk Recommendations
AI-generated Remediation Plans
Platform Architecture
mermaid
flowchart TD

A[Web Client / Dashboard V2] --> B[FastAPI REST API]

B --> C[Assessment Engine]
B --> D[Asset Discovery]
B --> E[Risk Engine]
B --> F[Baseline Engine]
B --> G[Roadmap Engine]
B --> H[Report Engine Pro - PDF]

C --> DB[(PostgreSQL)]
D --> DB
E --> DB
F --> DB
G --> DB
H --> OUT[./output/ - PDF Vendible]

DB --> I[IEC 62443 Controls]
DB --> J[MITRE ATT&CK ICS]
DB --> K[Assets]
DB --> L[Assessments]
Technology Stack
Python 3.12
FastAPI
PostgreSQL 16
SQLAlchemy
Docker & Docker Compose (4 services)
Jinja2 Templates (Dashboard V2 + Informe PDF)
Anthropic Claude API
Report Engine Pro (HTML → PDF)
Quick Start
Clone the repository
bash
git clone https://github.com/juanjocaladoc/sentra-os.git
cd sentra-os/sentra-os
Run with Docker — v0.8.0 Pro
bash
# Crear carpeta de entregables
mkdir output -Force

# Levantar stack pro
docker compose up -d --build

# Verificar 4 contenedores UP
docker ps
API Documentation
Local:

http://localhost:8000/docs          # Swagger
http://localhost:8000/dashboard-view # Dashboard V2 Ejecutivo - NUEVO
Production:

https://sentra-os.onrender.com/docs
Flujo de Venta (2 minutos) — NUEVO v0.8.0
bash
1. Abre http://localhost:8000/dashboard-view
2. Selecciona Assessment ID 3
3. Pulsa "Informe PDF Pro"
4. Recoge PDF en ./output/sentra_os_informe_3_*.pdf
5. Entrega a cliente
Assessment Workflow
Create Assessment
Import Assets
Execute Interview (17 controles)
Calculate Risk Score (0-5 / 0-100%)
Generate Roadmap (Top 3 riesgos + Quick Wins)
Generate Executive Report V2 (Dashboard)
Export PDF Pro → ./output/ (Vendible)
Current Status — Actualizado v0.8.0
Component	Status
IEC 62443 Assessment Engine	✅ Complete
Asset Discovery	✅ Complete
Asset Risk Engine	✅ Complete
Asset Baseline Engine	✅ Complete
Executive Reports V2	✅ Complete — Dashboard vendible
HTML Reports	✅ Complete
PDF Reports Pro	✅ Complete — v0.8.0
Output Persistence	✅ Complete — ./output/
Docker Deployment (4 UP)	✅ Complete
PostgreSQL	✅ Complete
Alembic Migrations	✅ Complete
Render Deployment	✅ Complete
Executive Dashboard V2	✅ Complete — v0.8.0
Authentication	🚧 In Progress
Multi-Tenant Architecture	🚧 In Progress
AI Executive Summary	🚧 In Progress
Hercules Knowledge Engine	📅 Planned
Threat Intelligence Integration	📅 Planned
API Endpoints
Endpoint	Description
GET /dashboard-view	Dashboard Ejecutivo V2 — NUEVO v0.8.0
POST /assessments	Create Assessment
POST /interview	Execute Assessment
POST /risk-score	Calculate Risk
POST /assessments/{id}/report?formato=pdf	Generate PDF Pro → ./output/ — NUEVO
GET /docs	Swagger API
Repository Structure — v0.8.0
sentra-os/
│
├── app/
│   ├── main.py (23KB pro)
│   ├── models.py
│   ├── db.py
│   ├── templates/
│   │   ├── dashboard_v2.html
│   │   └── informe_pdf.html
│   └── modules/
│       ├── assessment_engine.py
│       ├── asset_discovery.py
│       ├── asset_risk_engine.py
│       ├── asset_baseline_engine.py
│       ├── asset_dashboard.py
│       ├── roadmap_engine.py
│       ├── report_engine.py
│       └── ai_engine.py
│
├── alembic/
│   └── versions/
│
├── output/  — NUEVO v0.8.0 — Entregables vendibles
│   └── sentra_os_informe_{id}_{timestamp}.pdf
│
├── db/
├── seed/
├── docker-compose.yml — con volumen output:/app/output
└── README.md
Product Roadmap
Version	Status	Main Features
v0.7.1	✅ Released	Alembic, Asset Dashboard, Baselines, Docker, Render
v0.8.0	✅ Released — TODAY	Dashboard V2 Vendible, PDF Pro, Output Persistence, 4 containers UP
v0.8.5	🚧 In Progress	Exportación PDF limpia sin botones, Marca blanca
v0.9	📅 Planned	Hercules Knowledge Engine, AI Recommendations, Multi-cliente
v1.0	🎯 Target	Complete OT Assessment Platform, Auth, Compliance Dashboards, Threat Intel
Maintainer
Juan José Calado Carrillo

OT Cybersecurity Engineer

Industrial Control Systems (ICS) • IEC 62443 • MITRE ATT&CK ICS • OT Risk Assessment • Industrial Asset Security

GitHub: https://github.com/juanjocaladoc
LinkedIn: https://www.linkedin.com/in/juanjocaladoc/
Location: Sevilla, Spain — Coria del Río
License
MIT License — SentraOT OS — Hecho en Sevilla para industria OT.

