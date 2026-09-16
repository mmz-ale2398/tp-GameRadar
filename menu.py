"""
main.py
-------
Punto de entrada de Game Radar (versión orientada a objetos).

Acá se arman las piezas del sistema y se inyectan como dependencias:

    FuenteTXT  ->  Catalogo  ─┐
    Usuario                   ├─>  AplicacionTerminal
    RecomendadorPorContenido ─┘

Ejecutar con:
    python main.py
"""

import os
import sys

from catalogo import Catalogo, ErrorDeCarga, FuenteTXT
from interfaz import AplicacionTerminal, Consola
from modelos import Usuario
from recomendador import RecomendadorPorContenido

RUTA_DATASET = os.path.join(os.path.dirname(__file__), "datos", "videojuegos.txt")


def construir_catalogo(ruta=RUTA_DATASET):
    """
    Crea el catálogo a partir del dataset .txt. Si falla la carga, se
    informa el problema con claridad en vez de dejar caer el programa.
    """
    catalogo = Catalogo(FuenteTXT(ruta))
    try:
        cantidad = catalogo.cargar()
    except ErrorDeCarga as error:
        print(f"[ERROR] {error}")
        print("Verificá que exista la carpeta 'datos' con el archivo 'videojuegos.txt'.")
        return None

    if cantidad == 0:
        print("[ERROR] El dataset se leyó pero no contiene videojuegos válidos.")
        return None

    print(f"Catálogo cargado: {cantidad} videojuegos.\n")
    return catalogo


def main():
    Consola.titulo("GAME RADAR", "Tu próxima aventura")
    catalogo = construir_catalogo()
    if catalogo is None:
        sys.exit(1)

    nombre = Consola.texto("¿Cómo te llamás? ", permitir_vacio=True)
    usuario = Usuario(nombre or "Jugador")
    recomendador = RecomendadorPorContenido()

    aplicacion = AplicacionTerminal(catalogo, usuario, recomendador)
    aplicacion.ejecutar()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido. ¡Hasta luego!")
