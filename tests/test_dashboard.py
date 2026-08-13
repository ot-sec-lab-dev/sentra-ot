import json
from urllib.request import urlopen


def test_dashboard_assessment_3():
    with urlopen("http://localhost:8000/assessments/3/dashboard") as response:
        assert response.status == 200
        datos = json.loads(response.read().decode("utf-8"))

    assert datos["assessment_id"] == 3

    # Riesgo global
    assert datos["riesgo_global"]["score"] == 77.39
    assert datos["riesgo_global"]["nivel"] == "crítico"

    frameworks = datos["riesgo_global"]["frameworks"]
    assert frameworks["IEC62443"] == 71.43
    assert frameworks["MITRE-ATTCK-ICS"] == 100.0

    # Indicadores
    assert datos["indicadores"]["hallazgos_criticos"] == 2
    assert datos["indicadores"]["hallazgos_totales"] == 3
    assert datos["indicadores"]["fases_roadmap"] == 2

    # Top riesgos
    riesgos = {
        riesgo["codigo"]: riesgo
        for riesgo in datos["top_riesgos"]
    }

    assert len(riesgos) == 3
    assert riesgos["SR 5.1"]["criticidad"] == 9
    assert riesgos["T0855"]["criticidad"] == 8
    assert riesgos["SR 6.2"]["criticidad"] == 6

    # Roadmap
    roadmap = {
        item["fase"]: item
        for item in datos["roadmap"]
    }

    assert roadmap["Largo plazo"]["items"] == 1
    assert roadmap["Largo plazo"]["horas"] is None
    assert roadmap["Medio plazo"]["items"] == 2
    assert roadmap["Medio plazo"]["horas"] == 24

    print("TEST PASSED")


if __name__ == "__main__":
    test_dashboard_assessment_3()
