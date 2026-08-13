from app.modules import risk_engine


def test_scoring_assessment_3():
    resultado = risk_engine.calcular_riesgo(3)

    assert resultado["score"] == 77.39
    assert resultado["nivel"] == "crítico"

    assert "IEC62443" in resultado["desglose_por_framework"]
    assert "MITRE-ATTCK-ICS" in resultado["desglose_por_framework"]

    print("TEST PASSED")


if __name__ == "__main__":
    test_scoring_assessment_3()
