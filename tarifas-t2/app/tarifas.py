"""Cálculo de lo que se le cobra a una tarjeta por sus validaciones."""
from datetime import timedelta
from app.config import DESCUENTOS, MULTIPLO_REDONDEO, TARIFA_BASE, VENTANA_TRANSBORDO_MIN, VALOR_TRANSBORDO
from app.modelos import Cobro, Perfil, RespuestaTarifa, SolicitudTarifa
from app.verificaciones import VerificadorSolicitudTarifa

_verificador = VerificadorSolicitudTarifa()


def aplicar_descuento(valor: int, perfil: Perfil) -> int:
    """Aplica el descuento del perfil y redondea al múltiplo de 50 más cercano."""
    descuento = DESCUENTOS[perfil.value] / 100
    valor_con_descuento = valor * (1 - descuento)
    return round(valor_con_descuento / MULTIPLO_REDONDEO) * MULTIPLO_REDONDEO


def calcular_tarifa(solicitud: SolicitudTarifa) -> RespuestaTarifa:
    # Primero realiza las verificaciones sobre la solicitud recibida
    _verificador.verificar(solicitud)
    # Ahora se aplica la política de transbordos.
    ventana = timedelta(minutes=VENTANA_TRANSBORDO_MIN)
    inicio_viaje = None
    transbordos_usados = 0
    cobros = []

    # Ordena las validaciones para garantizar el correcto cálculo de diferencias de tiempo
    validaciones = sorted(solicitud.validaciones, key=lambda v: v.fecha_hora)
    for validacion in validaciones:

        """Si ya se había iniciado un viaje nuevo, la nueva validación no es la tercera desde que
        inició este viaje y está dentro de los siguientes 90 minutos, se trata como transbordo"""
        es_transbordo = (
            inicio_viaje is not None
            and validacion.fecha_hora - inicio_viaje <= ventana
            and transbordos_usados < 2
        )

        # Define el valor base y tipo según si es viaje nuevo, primer o segundo transbordo
        if es_transbordo:
            if transbordos_usados == 0:
                tipo = "transbordo"
                valor_base = VALOR_TRANSBORDO
            else:
                tipo = "transbordo_gratis"
                valor_base = 0
            transbordos_usados += 1
        else:
            tipo = "tarifa"
            valor_base = TARIFA_BASE
            inicio_viaje = validacion.fecha_hora
            transbordos_usados = 0
        # Si no es transbordo, se reanuda la cuenta en 0; de lo contrario, se suman de a 1

        # Finalmente, se calcula el descuento y se crea el cobro
        cobros.append(
            Cobro(
                validacion_id=validacion.id,
                fecha_hora=validacion.fecha_hora,
                tipo=tipo,
                valor=aplicar_descuento(valor_base, solicitud.perfil),
            )
        )

    total = sum(c.valor for c in cobros)
    return RespuestaTarifa(
        tarjeta=solicitud.tarjeta,
        perfil=solicitud.perfil,
        cobros=cobros,
        total=total,
    )
