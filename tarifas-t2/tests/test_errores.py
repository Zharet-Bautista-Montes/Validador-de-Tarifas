from fastapi.testclient import TestClient

from app.config import TARIFA_BASE
from app.main import app

cliente = TestClient(app)

# Falla si el perfil es diferente a "general", "estudiante" o "adulto_mayor"
def test_registro_con_perfil_invalido():
    r = cliente.post(
        "/tarifas/calcular",
        json={
            "tarjeta": "T-TEST-00X",
            "perfil": "oficial",
            "validaciones": [
                {"id": "v1", "estacion": "E00", "fecha_hora": "2025-03-10T07:12:00-05:00"}
            ],
        },
    )
    assert r.status_code == 422

# Falla si hay más de una validación con un id repetido
def test_validacion_con_id_repetido():
    r = cliente.post(
        "/tarifas/calcular",
        json={
            "tarjeta": "T-TEST-00Y",
            "perfil": "adulto_mayor",
            "validaciones": [
                {"id": "v1", "estacion": "E01", "fecha_hora": "2025-03-10T07:12:00-05:00"},
                {"id": "v1", "estacion": "E02", "fecha_hora": "2025-03-10T07:12:01-05:00"}
            ],
        },
    )
    assert r.status_code == 422

# Falla cuando alguna fecha_hora no incluye zona horaria (ej.: -05:00 o Z al final)
def test_validaciones_sin_zona_horaria():
    r = cliente.post(
        "/tarifas/calcular",
        json={
            "tarjeta": "T-TEST-00Z",
            "perfil": "estudiante",
            "validaciones": [
                {"id": "v10", "estacion": "E03", "fecha_hora": "2025-03-10T07:14:00"},
                {"id": "v11", "estacion": "E04", "fecha_hora": "2025-03-10T07:16:00"},
                {"id": "v12", "estacion": "E05", "fecha_hora": "2025-03-10T07:18:00"}
            ],
        },
    )
    assert r.status_code == 422

# Identifica todos los errores en la misma solicitud
def test_errores_conjunto():
    r = cliente.post(
        "/tarifas/calcular",
        json={
            "tarjeta": "T-TEST-00Z",
            "perfil": "general",
            "validaciones": [
                {"id": "v10", "estacion": "E06", "fecha_hora": "2025-03-10T07:12:00Z"},
                {"id": "v10", "estacion": "E07", "fecha_hora": "2025-03-10T07:14:00Z"},
                {"id": "v11", "estacion": "E08", "fecha_hora": "2025-03-10T07:16:00Z"},
                {"id": "v12", "estacion": "E09", "fecha_hora": "2025-03-10T07:18:00"}
            ],
        },
    )
    assert r.status_code == 422
    cuerpo = r.json()
    assert len(cuerpo["detail"]) == 2 #En este caso hay 2 errores