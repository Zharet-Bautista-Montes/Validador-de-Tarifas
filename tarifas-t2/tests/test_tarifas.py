from app.config import TARIFA_BASE
from app.modelos import Perfil
from app.tarifas import aplicar_descuento


def test_general_no_tiene_descuento():
    assert aplicar_descuento(TARIFA_BASE, Perfil.GENERAL) == TARIFA_BASE


def test_descuento_redondea_a_multiplo_de_50():
    assert aplicar_descuento(TARIFA_BASE, Perfil.ESTUDIANTE) % 50 == 0

# Asegura que se aplica un descuento distinto para cada perfil
def test_descuento_por_perfil():
    tarifa_G = aplicar_descuento(TARIFA_BASE, Perfil.GENERAL)
    tarifa_E = aplicar_descuento(TARIFA_BASE, Perfil.ESTUDIANTE)
    tarifa_AM = aplicar_descuento(TARIFA_BASE, Perfil.ADULTO_MAYOR)
    assert tarifa_G != tarifa_E and tarifa_E != tarifa_AM and tarifa_G != tarifa_AM