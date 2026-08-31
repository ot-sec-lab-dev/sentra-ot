# SENTRA OT v3.4 PRO — Assessment OT para Pymes Industriales

> **Proyecto personal I+D fuera de horario laboral, con medios propios. Open source MIT educativo. No relacionado con mi actividad profesional.**
> **Foco: Pymes industriales 20-250 empleados (agro, food, agua, metal) que no disponen de SOC OT - segmento no cubierto por grandes consultoras.**

**Demo real: Planta Piloto Coria del Río (Sevilla) - Agroindustrial 14 activos - Score 50% - [PDF 82KB](docs/demo/SENTRA_OT_Coria_50_Demo.pdf)**

### ¿Por qué pymes?

Las grandes consultoras no entran por debajo de 25k€. Una almazara, una EDAR pequeña o una conservera no puede pagar eso, pero tiene el mismo riesgo: PLC sin password, red plana.

SENTRA OT Express cubre ese hueco: informe CISO vendible en 15 min.

### Quick Start
docker-compose up -d --build
docker exec sentra_assessment_engine python seed_coria.py
# login admin / sentra2024

### Modelo no competitivo
- Express Pyme (20-30 activos): 2.900€ - para cooperativas, EDAR pequeña
- Industrial Local (hasta 100 activos): 8.900€ - metalmecánica, logística frío
- No oferto a: Utilities >500 empleados, transporte crítico, defensa (mercado grandes consultoras)

Stack: FastAPI + PostgreSQL + WeasyPrint + Matplotlib
