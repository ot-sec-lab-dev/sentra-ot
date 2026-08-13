"""
Report Engine / PDF Builder
----------------------------
Punto de ensamblaje final del informe Sentra OS.

Este módulo recopila la información del Assessment, Risk Engine,
hallazgos, activos y Roadmap, y la entrega a la plantilla HTML
para generar el informe final en HTML o PDF.

Este módulo NO calcula riesgo ni modifica los datos del Assessment.
Su función es recopilar, estructurar y presentar la información.
"""

import os
from datetime import datetime

from sqlalchemy import text
from jinja2 import Environment, FileSystemLoader

from db import engine


OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/app/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

jinja_env = Environment(
    loader=FileSystemLoader("templates")
)


def generar_informe(
    assessment_id: int,
    resumen_ejecutivo: str = "",
    formato: str = "html",
) -> dict:
    """
    Genera el informe de un Assessment.

    formato:
        - "html": genera únicamente el HTML.
        - "pdf": genera el PDF mediante WeasyPrint.

    El módulo recopila la información existente y la entrega
    a la plantilla report.html.
    """

    if formato not in ("html", "pdf"):
        raise ValueError("formato debe ser 'html' o 'pdf'")

    with engine.begin() as conn:

        # ============================================================
        # ASSESSMENT
        # ============================================================

        assessment = conn.execute(
            text(
                """
                SELECT
                    a.id,
                    a.nombre,
                    a.alcance,
                    cl.nombre,
                    cl.sector
                FROM assessments a
                JOIN clients cl
                    ON a.client_id = cl.id
                WHERE a.id = :aid
                """
            ),
            {"aid": assessment_id},
        ).fetchone()

        if assessment is None:
            raise ValueError("assessment no encontrado")

        (
            _,
            assessment_nombre,
            alcance,
            cliente_nombre,
            sector,
        ) = assessment

        # ============================================================
        # RISK SCORE
        # ============================================================

        risk = conn.execute(
            text(
                """
                SELECT
                    score,
                    nivel,
                    desglose
                FROM risk_scores
                WHERE assessment_id = :aid
                ORDER BY calculated_at DESC
                LIMIT 1
                """
            ),
            {"aid": assessment_id},
        ).fetchone()

        if risk is None:
            raise ValueError(
                "no hay risk_score calculado; "
                "ejecuta Risk Engine primero"
            )

        score, nivel, desglose = risk

        # ============================================================
        # ASSETS / INVENTARIO
        # ============================================================

        assets_rows = conn.execute(
            text(
                """
                SELECT
                    id,
                    nombre,
                    tipo,
                    fabricante,
                    modelo,
                    ip,
                    mac,
                    sistema_operativo,
                    firmware,
                    ubicacion,
                    zona_purdue,
                    criticidad,
                    criticidad_negocio,
                    owner,
                    estado,
                    last_seen
                FROM assets
                WHERE assessment_id = :aid
                ORDER BY
                    criticidad_negocio DESC,
                    criticidad DESC,
                    id
                """
            ),
            {"aid": assessment_id},
        ).fetchall()

        assets = [
            {
                "id": asset[0],
                "nombre": asset[1],
                "tipo": asset[2],
                "fabricante": asset[3],
                "modelo": asset[4],
                "ip": asset[5],
                "mac": asset[6],
                "sistema_operativo": asset[7],
                "firmware": asset[8],
                "ubicacion": asset[9],
                "zona_purdue": asset[10],
                "criticidad": asset[11],
                "criticidad_negocio": asset[12],
                "owner": asset[13],
                "estado": asset[14],
                "last_seen": asset[15],
            }
            for asset in assets_rows
        ]

        # ============================================================
        # HALLAZGOS
        #
        # Cada hallazgo queda relacionado con:
        #   Assessment
        #       └── Control Evaluation
        #               ├── Control
        #               │     └── Framework
        #               └── Asset (opcional)
        # ============================================================

        findings_rows = conn.execute(
            text(
                """
                SELECT
                    ce.id,
                    c.codigo,
                    c.nombre,
                    c.descripcion,
                    f.nombre AS framework,

                    ce.asset_id,
                    a.nombre AS activo,

                    ce.estado,
                    ce.criticidad,
                    ce.evidencia,
                    ce.impacto,
                    ce.quick_win,
                    ce.coste_estimado,
                    ce.horas

                FROM control_evaluations ce

                JOIN controls c
                    ON ce.control_id = c.id

                LEFT JOIN frameworks f
                    ON c.framework_id = f.id

                LEFT JOIN assets a
                    ON ce.asset_id = a.id

                WHERE ce.assessment_id = :aid

                ORDER BY
                    ce.criticidad DESC,
                    ce.id
                """
            ),
            {"aid": assessment_id},
        ).fetchall()

        hallazgos = [
            {
                "id": finding[0],
                "codigo": finding[1],
                "nombre": finding[2],
                "descripcion": finding[3],
                "framework": finding[4],

                "asset_id": finding[5],
                "activo": finding[6],

                "estado": finding[7],
                "criticidad": finding[8],
                "evidencia": finding[9],
                "impacto": finding[10],
                "quick_win": finding[11],
                "coste_estimado": finding[12],
                "horas": finding[13],
            }
            for finding in findings_rows
        ]

        # ============================================================
        # ROADMAP
        #
        # Cada acción conserva su relación con:
        #   - Control Evaluation
        #   - Control
        #   - Framework
        #   - Asset
        # ============================================================

        roadmap_rows = conn.execute(
            text(
                """
                SELECT
                    ri.id,
                    ri.control_evaluation_id,
                    ri.fase,
                    ri.prioridad,
                    ri.titulo,
                    ri.horas,
                    ri.coste_estimado,

                    c.codigo,
                    c.nombre,
                    f.nombre AS framework,

                    ce.asset_id,
                    a.nombre AS activo

                FROM roadmap_items ri

                LEFT JOIN control_evaluations ce
                    ON ri.control_evaluation_id = ce.id

                LEFT JOIN controls c
                    ON ce.control_id = c.id

                LEFT JOIN frameworks f
                    ON c.framework_id = f.id

                LEFT JOIN assets a
                    ON ce.asset_id = a.id

                WHERE ri.assessment_id = :aid

                ORDER BY
                    ri.prioridad,
                    ri.id
                """
            ),
            {"aid": assessment_id},
        ).fetchall()

        roadmap = [
            {
                "id": item[0],
                "control_evaluation_id": item[1],
                "fase": item[2],
                "prioridad": item[3],
                "titulo": item[4],
                "horas": item[5],
                "coste_estimado": item[6],

                "codigo": item[7],
                "control": item[8],
                "framework": item[9],

                "asset_id": item[10],
                "activo": item[11],
            }
            for item in roadmap_rows
        ]

        # ============================================================
        # TEMPLATE
        # ============================================================

        template = jinja_env.get_template("report.html")

        html_content = template.render(
            cliente_nombre=cliente_nombre,
            sector=sector,
            assessment_nombre=assessment_nombre,
            alcance=alcance,

            score=score,
            nivel=nivel,
            desglose=desglose,

            resumen_ejecutivo=resumen_ejecutivo,

            assets=assets,

            hallazgos=hallazgos,

            roadmap=roadmap,

            fecha=datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            ),
        )

        # ============================================================
        # OUTPUT
        # ============================================================

        timestamp = datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )

        extension = (
            "pdf"
            if formato == "pdf"
            else "html"
        )

        filename = (
            f"sentra_os_informe_"
            f"{assessment_id}_"
            f"{timestamp}."
            f"{extension}"
        )

        output_path = os.path.join(
            OUTPUT_DIR,
            filename,
        )

        # ============================================================
        # GENERACIÓN HTML / PDF
        # ============================================================

        if formato == "pdf":

            from weasyprint import HTML

            base_url = "/app/"

            HTML(
                string=html_content,
                base_url=base_url,
            ).write_pdf(
                output_path
            )

        else:

            with open(
                output_path,
                "w",
                encoding="utf-8",
            ) as file:
                file.write(html_content)

        # ============================================================
        # REGISTRO DEL INFORME
        # ============================================================

        report_id = conn.execute(
            text(
                """
                INSERT INTO reports (
                    assessment_id,
                    resumen_ejecutivo,
                    pdf_path
                )
                VALUES (
                    :aid,
                    :resumen,
                    :path
                )
                RETURNING id
                """
            ),
            {
                "aid": assessment_id,
                "resumen": resumen_ejecutivo,
                "path": output_path,
            },
        ).scalar()

    # ============================================================
    # RESULTADO
    # ============================================================

    return {
        "report_id": report_id,
        "path": output_path,
        "formato": formato,
    }