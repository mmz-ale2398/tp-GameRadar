""" catalogo.py
-----------
Capa de acceso a datos de Game Radar.

Define la interfaz `FuenteDeDatos` (contrato que debe cumplir cualquier
origen de datos) y sus implementaciones concretas. Hoy el sistema usa
`FuenteTXT` sobre el mismo dataset delimitado por '|'.

La clase `Catalogo` es la que consume el resto de los módulos: recibe una
fuente, carga los videojuegos y ofrece las operaciones de consulta
(buscar, listar, filtrar). """

import os

from abc import ABC, abstractmethod

from modelos import Videojuego


class ErrorDeCarga(Exception):
    """Error propio del sistema al cargar el dataset."""


class FuenteDeDatos(ABC):
    """
    Interfaz entre el catálogo y el origen de los datos.
    Cualquier fuente concreta debe saber leer y devolver objetos Videojuego.
    """

    def __init__(self, ruta):
        self._ruta = ruta

    @property
    def ruta(self):
        return self._ruta

    @abstractmethod
    def leer(self):
        """Devuelve una lista de objetos Videojuego."""

    def _verificar_existencia(self):
        if not os.path.exists(self._ruta):
            raise ErrorDeCarga(f"No se encontró el archivo '{self._ruta}'.")


class FuenteTXT(FuenteDeDatos):
    """
    Lee el dataset delimitado por '|' con el formato:
        ID|Título|Géneros|Plataformas|Año|Puntuación
    """

    SEPARADOR_CAMPOS = "|"
    SEPARADOR_LISTAS = ","
    CANTIDAD_CAMPOS = 6

    def leer(self):
        self._verificar_existencia()
        juegos = []

        try:
            with open(self._ruta, "r", encoding="utf-8") as archivo:
                for numero, linea in enumerate(archivo, start=1):
                    linea = linea.strip()
                    if not linea or linea.startswith("#"):
                        continue  # líneas vacías o comentarios
                    juego = self._parsear_linea(linea, numero)
                    if juego is not None:
                        juegos.append(juego)
        except OSError as error:
            raise ErrorDeCarga(f"No se pudo leer '{self._ruta}': {error}") from error

        return juegos

    def _parsear_linea(self, linea, numero):
        """Convierte una línea en Videojuego, o avisa y devuelve None."""
        campos = linea.split(self.SEPARADOR_CAMPOS)

        if len(campos) != self.CANTIDAD_CAMPOS:
            print(f"[AVISO] Línea {numero} ignorada (formato inválido).")
            return None

        id_texto, titulo, generos, plataformas, anio, puntuacion = campos

        try:
            return Videojuego(
                id_juego=id_texto,
                titulo=titulo,
                generos=self._dividir(generos),
                plataformas=self._dividir(plataformas),
                anio=anio,
                puntuacion=puntuacion,
            )
        except ValueError as error:
            print(f"[AVISO] Línea {numero} ignorada ({error}).")
            return None

    def _dividir(self, texto):
        return [t.strip() for t in texto.split(self.SEPARADOR_LISTAS) if t.strip()]

#---------------------clase catalogo-----------------------------

"""Colección de videojuegos cargada desde una FuenteDeDatos.
Es la interfaz que usan la terminal y el recomendador para consultar
el dataset; ninguno de los dos sabe de qué tipo de archivo vino."""

class Catalogo:

    def __init__(self, fuente):
        self._fuente = fuente
        self._juegos = []
        self._indice_por_id = {}

    # ---------------- Carga ---------------------------------------------

    def cargar(self):
        """Lee la fuente y arma el índice interno. Devuelve la cantidad cargada."""
        self._juegos = self._fuente.leer()
        self._indice_por_id = {juego.id: juego for juego in self._juegos}
        return len(self._juegos)

    # ---------------- Operaciones de consulta ---------------------------

    def listar(self, orden="titulo"):
        """
        Operación LISTAR: devuelve todos los videojuegos del catálogo,
        ordenados por título, puntuación o año.
        """
        claves = {
            "titulo": (lambda j: j.titulo, False),
            "puntuacion": (lambda j: j.puntuacion, True),
            "anio": (lambda j: j.anio, True),
        }
        clave, descendente = claves.get(orden, claves["titulo"])
        return sorted(self._juegos, key=clave, reverse=descendente)

    def buscar(self, texto):
        """Operación BUSCAR: coincidencia parcial por título."""
        return [j for j in self._juegos if j.coincide_titulo(texto)]

    def filtrar(self, genero=None, plataforma=None, anio=None, puntuacion_minima=None):
        """
        Operación FILTRAR: combina varios criterios. Los parámetros en None
        simplemente no se aplican, así que se pueden mezclar libremente.
        """
        resultados = self._juegos

        if genero:
            resultados = [j for j in resultados if j.tiene_genero(genero)]
        if plataforma:
            resultados = [j for j in resultados if j.tiene_plataforma(plataforma)]
        if anio is not None:
            resultados = [j for j in resultados if j.anio == int(anio)]
        if puntuacion_minima is not None:
            resultados = [j for j in resultados if j.puntuacion >= float(puntuacion_minima)]

        return resultados

    def obtener_por_id(self, id_juego):
        """Acceso directo O(1) por id. Devuelve None si no existe."""
        return self._indice_por_id.get(int(id_juego))

    # ---------------- Información agregada -------------------------------

    def generos_disponibles(self):
        generos = set()
        for juego in self._juegos:
            generos.update(juego.generos)
        return sorted(g.nombre for g in generos)

    def plataformas_disponibles(self):
        plataformas = set()
        for juego in self._juegos:
            plataformas.update(juego.plataformas)
        return sorted(p.nombre for p in plataformas)

    def anios_disponibles(self):
        return sorted({j.anio for j in self._juegos})

    def __len__(self):
        return len(self._juegos)

    def __iter__(self):
        return iter(self._juegos)

    def __repr__(self):
        return f"Catalogo({len(self._juegos)} videojuegos desde '{self._fuente.ruta}')"