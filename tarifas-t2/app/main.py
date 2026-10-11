from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.historial import obtener_historial
from app.modelos import RespuestaTarifa, SolicitudTarifa
from app.tarifas import calcular_tarifa
from app.verificaciones import ErrorVerificacionTarifa

app = FastAPI(title="Tarifas Línea T2", version="0.3.0")

@app.exception_handler(ErrorVerificacionTarifa)
async def manejar_error_validacion_tarifa(
    request: Request, exc: ErrorVerificacionTarifa
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.errores})

@app.get("/salud")
def salud() -> dict[str, str]:
    return {"estado": "ok"}


@app.post("/tarifas/calcular", response_model=RespuestaTarifa)
def calcular(solicitud: SolicitudTarifa) -> RespuestaTarifa:
    respuesta = calcular_tarifa(solicitud)
    obtener_historial(solicitud.tarjeta).registrar(respuesta)
    return respuesta


@app.get("/tarjetas/{tarjeta}/historial", response_model=list[RespuestaTarifa])
def historial(tarjeta: str) -> list[RespuestaTarifa]:
    return obtener_historial(tarjeta).listar()
