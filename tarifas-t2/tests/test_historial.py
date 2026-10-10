from fastapi.testclient import TestClient

from app.historial import HistorialTarjeta
from app.main import app

cliente = TestClient(app)

# Función auxiliar para simular el ingreso de una nueva validación
def _registrar_prueba(tarjeta: str, id_validacion: str) -> None:
    r = cliente.post(
        "/tarifas/calcular",
        json={
            "tarjeta": tarjeta,
            "perfil": "general",
            "validaciones": [
                {
                    "id": id_validacion,
                    "estacion": "E01",
                    "fecha_hora": "2026-01-31T04:40:00-05:00",
                }
            ],
        },
    )
    assert r.status_code == 200

# Confirma que los historiales de instancias distintas son independientes
def test_historiales_independientes():
    a = HistorialTarjeta("T-UNIT-A")
    b = HistorialTarjeta("T-UNIT-B")
    c = HistorialTarjeta("T-UNIT-C")
    assert a.calculos is not b.calculos and a.calculos is not c.calculos and c.calculos is not b.calculos

# Revisa que con cada nueva consulta se obtienen todos los registros hasta ese momento
def test_historial_actualizado():
    historial_c0 = cliente.get("/tarjetas/T-TEST-C/historial").json()
    assert len(historial_c0) == 0
    _registrar_prueba("T-TEST-C", "c1")
    historial_c1 = cliente.get("/tarjetas/T-TEST-C/historial").json()
    assert len(historial_c1) == 1
    _registrar_prueba("T-TEST-C", "c2")
    historial_c2 = cliente.get("/tarjetas/T-TEST-C/historial").json()
    assert len(historial_c2) == 2

# Valida que el historial devuelve solo los cobros de la tarjeta consultada
def test_historial_tarjeta_consultada():
    _registrar_prueba("T-HIST-A", "a1")
    _registrar_prueba("T-HIST-B", "b1")
    _registrar_prueba("T-HIST-B", "b2")
    _registrar_prueba("T-HIST-B", "b3")
    historial_a = cliente.get("/tarjetas/T-HIST-A/historial").json()
    historial_b = cliente.get("/tarjetas/T-HIST-B/historial").json()
    assert [c["tarjeta"] for c in historial_a] == ["T-HIST-A"]
    assert [c["tarjeta"] for c in historial_b] == ["T-HIST-B", "T-HIST-B", "T-HIST-B"]
