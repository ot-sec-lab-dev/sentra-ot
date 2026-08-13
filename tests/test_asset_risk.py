from app.modules import asset_risk_engine


def test_asset_risk_assessment_3():
    resultados = asset_risk_engine.calcular_riesgo_activos(3)

    assert len(resultados) == 3

    riesgos = {
        activo["nombre"]: activo["risk_score"]
        for activo in resultados
    }

    assert riesgos["PLC Linea 1"] == 100
    assert riesgos["HMI Producción"] == 60
    assert riesgos["Servidor SCADA Central"] == 70

    print("TEST PASSED")


if __name__ == "__main__":
    test_asset_risk_assessment_3()
