"""Verificaciones de negocio de la solicitud de cálculo de tarifa."""

from app.modelos import Perfil, SolicitudTarifa


class ErrorVerificacionTarifa(Exception):
    """La solicitud no cumple las reglas; lleva todos los errores encontrados."""

    def __init__(self, errores: list[dict]):
        super().__init__("Solicitud de tarifa inválida")
        self.errores = errores


class VerificadorSolicitudTarifa:
    PERFILES_VALIDOS = tuple(perfil.value for perfil in Perfil)
    # Verifica cualquiera de los errores en una solicitud
    def verificar(self, solicitud: SolicitudTarifa) -> None:
        errores = [
            *self._errores_perfil(solicitud),
            *self._errores_ids_duplicados(solicitud),
            *self._errores_zona_horaria(solicitud),
        ]
        if errores:
            raise ErrorVerificacionTarifa(errores)

    def _errores_perfil(self, solicitud: SolicitudTarifa) -> list[dict]:
        perfil = getattr(solicitud.perfil, "value", solicitud.perfil)
        if perfil in self.PERFILES_VALIDOS:
            return []
        permitidos = ", ".join(self.PERFILES_VALIDOS)
        return [
            self._error(
                ["body", "perfil", perfil],
                f"Perfil '{perfil}' no válido; use uno entre: {permitidos}",
                "perfil_invalido",
            )
        ]

    def _errores_ids_duplicados(self, solicitud: SolicitudTarifa) -> list[dict]:
        vistos = set()
        errores = []
        for indice, validacion in enumerate(solicitud.validaciones):
            if validacion.id in vistos:
                errores.append(
                    self._error(
                        ["body", "validaciones", indice, "id", validacion.id],
                        f"El id '{validacion.id}' está repetido",
                        "validacion_duplicada",
                    )
                )
            vistos.add(validacion.id)
        return errores

    def _errores_zona_horaria(self, solicitud: SolicitudTarifa) -> list[dict]:
        errores = []
        for indice, validacion in enumerate(solicitud.validaciones):
            if validacion.fecha_hora.utcoffset() is None:
                errores.append(
                    self._error(
                        ["body", "validaciones", indice, "fecha_hora", str(validacion.fecha_hora)],
                        "fecha_hora debe incluir zona horaria (por ejemplo -05:00 o Z)",
                        "zona_horaria_faltante",
                    )
                )
        return errores

    @staticmethod
    def _error(ubicacion: list, mensaje: str, tipo: str) -> dict:
        return {"loc": ubicacion, "msg": mensaje, "type": tipo}