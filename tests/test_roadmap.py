from app.modules import roadmap_engine


def test_roadmap_assessment_3():
    resultados = roadmap_engine.generar_roadmap(3)

    assert len(resultados) == 3

    # SR 5.1
    sr51 = next(r for r in resultados if r["control_evaluation_id"] == 2)
    assert sr51["fase"] == "Medio plazo"
    assert sr51["prioridad"] == 1
    assert sr51["titulo"] == "Desplegar VLAN dedicada y firewall entre red corporativa y red OT."
    assert sr51["horas"] == 16

    # SR 6.2
    sr62 = next(r for r in resultados if r["control_evaluation_id"] == 4)
    assert sr62["fase"] == "Medio plazo"
    assert sr62["prioridad"] == 2
    assert sr62["titulo"] == "Integrar el SCADA central en el SIEM existente."
    assert sr62["horas"] == 8

    # T0855
    t0855 = next(r for r in resultados if r["control_evaluation_id"] == 3)
    assert t0855["fase"] == "Largo plazo"
    assert t0855["prioridad"] == 3
    assert t0855["titulo"] == "Remediar T0855 — Unauthorized Command Message"
    assert t0855["horas"] is None

    print("TEST PASSED")


if __name__ == "__main__":
    test_roadmap_assessment_3()
