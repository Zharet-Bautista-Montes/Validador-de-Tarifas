from fastapi.testclient import TestClient

from app.config import TARIFA_BASE, VALOR_TRANSBORDO
from app.main import app
from app.tarifas import aplicar_descuento
from app.modelos import Perfil

cliente = TestClient(app)


def test_salud():
    r = cliente.get("/salud")
    assert r.status_code == 200
    assert r.json() == {"estado": "ok"}


def test_una_validacion_paga_tarifa_completa():
    r = cliente.post(
        "/tarifas/calcular",
        json={
            "tarjeta": "T-TEST-001",
            "perfil": "general",
            "validaciones": [
                {"id": "v1", "estacion": "E01", "fecha_hora": "2025-03-10T07:12:00-05:00"}
            ],
        },
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == TARIFA_BASE
    assert cuerpo["cobros"][0]["tipo"] == "tarifa"


def test_historial_registra_el_calculo():
    cliente.post(
        "/tarifas/calcular",
        json={
            "tarjeta": "T-TEST-002",
            "validaciones": [
                {"id": "v1", "estacion": "E04", "fecha_hora": "2025-03-10T09:00:00-05:00"}
            ],
        },
    )
    r = cliente.get("/tarjetas/T-TEST-002/historial")
    assert r.status_code == 200
    assert len(r.json()) >= 1

# Revisa el manejo de transbordos ($500 para el primero, $0 para el segundo, al tercero reinicia)
def test_primer_segundo_tercer_transbordo():
    r = cliente.post(
        "/tarifas/calcular",
        json={
            "tarjeta": "T-TEST-ABC",
            "perfil": "general",
            "validaciones": [
                {"id": "v6", "estacion": "E03", "fecha_hora": "2025-03-19T10:30:00-05:00"},
                {"id": "v7", "estacion": "E04", "fecha_hora": "2025-03-19T10:45:00-05:00"},
                {"id": "v8", "estacion": "E05", "fecha_hora": "2025-03-19T11:00:00-05:00"},
                {"id": "v9", "estacion": "E02", "fecha_hora": "2025-03-19T11:15:00-05:00"},
                {"id": "v10", "estacion": "E01", "fecha_hora": "2025-03-19T11:30:00-05:00"}
            ],
        },
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == 2 * (TARIFA_BASE + VALOR_TRANSBORDO)
    assert cuerpo["cobros"][0]["tipo"] == "tarifa"
    assert cuerpo["cobros"][0]["valor"] == TARIFA_BASE
    assert cuerpo["cobros"][1]["tipo"] == "transbordo"
    assert cuerpo["cobros"][1]["valor"] == VALOR_TRANSBORDO
    assert cuerpo["cobros"][2]["tipo"] == "transbordo_gratis"
    assert cuerpo["cobros"][2]["valor"] == 0
    assert cuerpo["cobros"][3]["tipo"] == "tarifa"
    assert cuerpo["cobros"][3]["valor"] == TARIFA_BASE
    assert cuerpo["cobros"][4]["tipo"] == "transbordo"
    assert cuerpo["cobros"][4]["valor"] == VALOR_TRANSBORDO

# Confirma que no se aplican transbordos fuera de la ventana de 90 minutos
def test_fuera_de_ventana():
    r = cliente.post(
        "/tarifas/calcular",
        json={
            "tarjeta": "T-TEST-003",
            "perfil": "general",
            "validaciones": [
                {"id": "v6", "estacion": "E03", "fecha_hora": "2025-03-19T10:00:00-05:00"},
                {"id": "v7", "estacion": "E04", "fecha_hora": "2025-03-19T11:31:00-05:00"},
                {"id": "v8", "estacion": "E05", "fecha_hora": "2025-03-19T13:02:00-05:00"}
            ],
        },
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == TARIFA_BASE * 3
    assert cuerpo["cobros"][0]["tipo"] == "tarifa"
    assert cuerpo["cobros"][0]["valor"] == TARIFA_BASE
    assert cuerpo["cobros"][1]["tipo"] == "tarifa"
    assert cuerpo["cobros"][1]["valor"] == TARIFA_BASE
    assert cuerpo["cobros"][2]["tipo"] == "tarifa"
    assert cuerpo["cobros"][2]["valor"] == TARIFA_BASE

# Valida que se aplica el descuento según el perfil, tanto en tarifas como en transbordos
def test_descuento_por_perfil():
    r = cliente.post(
        "/tarifas/calcular",
        json={
            "tarjeta": "T-TEST-004",
            "perfil": "adulto_mayor",
            "validaciones": [
                {"id": "v10", "estacion": "E12", "fecha_hora": "2025-03-19T20:30:00-05:00"},
                {"id": "v9", "estacion": "E11", "fecha_hora": "2025-03-19T19:00:00-05:00"}
            ],
        },
    )
    assert r.status_code == 200
    nueva_tarifa = aplicar_descuento(TARIFA_BASE, Perfil.ADULTO_MAYOR)
    nuevo_transbordo = aplicar_descuento(VALOR_TRANSBORDO, Perfil.ADULTO_MAYOR)
    cuerpo = r.json()
    assert cuerpo["total"] == nueva_tarifa + nuevo_transbordo
    assert cuerpo["cobros"][0]["tipo"] == "tarifa"
    assert cuerpo["cobros"][0]["valor"] == nueva_tarifa
    assert cuerpo["cobros"][1]["tipo"] == "transbordo"
    assert cuerpo["cobros"][1]["valor"] == nuevo_transbordo
    r = cliente.post(
        "/tarifas/calcular",
        json={
            "tarjeta": "T-TEST-005",
            "perfil": "estudiante",
            "validaciones": [
                {"id": "v10", "estacion": "E12", "fecha_hora": "2025-03-19T20:30:00-05:00"},
                {"id": "v9", "estacion": "E11", "fecha_hora": "2025-03-19T19:00:00-05:00"}
            ],
        },
    )
    assert r.status_code == 200
    nueva_tarifa = aplicar_descuento(TARIFA_BASE, Perfil.ESTUDIANTE)
    nuevo_transbordo = aplicar_descuento(VALOR_TRANSBORDO, Perfil.ESTUDIANTE)
    cuerpo = r.json()
    assert cuerpo["total"] == nueva_tarifa + nuevo_transbordo
    assert cuerpo["cobros"][0]["tipo"] == "tarifa"
    assert cuerpo["cobros"][0]["valor"] == nueva_tarifa
    assert cuerpo["cobros"][1]["tipo"] == "transbordo"
    assert cuerpo["cobros"][1]["valor"] == nuevo_transbordo

