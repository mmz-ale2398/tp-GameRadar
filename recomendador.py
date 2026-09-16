"""
recomendador.py
---------------
Motor de recomendaciones de Game Radar.

Define una interfaz `Recomendador` y una implementación concreta
`RecomendadorPorContenido`, que compara características de los
videojuegos (géneros, plataformas y puntuación) contra los favoritos
del usuario.

Separar la interfaz de la implementación permite agregar más adelante,
por ejemplo, un `RecomendadorPorPopularidad` sin cambiar la terminal.
"""

from abc import ABC, abstractmethod


class Recomendacion:
    """
    Resultado individual del motor: un videojuego junto con su porcentaje
    de similitud y el motivo por el cual fue recomendado.
    """

    def __init__(self, juego, similitud, motivo=""):
        self._juego = juego
        self._similitud = round(float(similitud), 1)
        self._motivo = motivo

    @property
    def juego(self):
        return self._juego

    @property
    def similitud(self):
        return self._similitud

    @property
    def motivo(self):
        return self._motivo

    def __repr__(self):
        return f"{self._juego.titulo} — {self._similitud}%"

    def __lt__(self, otra):
        """Permite ordenar recomendaciones directamente con sorted()."""
        return self._similitud < otra._similitud


class Recomendador(ABC):
    """Interfaz común a todos los motores de recomendación."""

    @abstractmethod
    def recomendar(self, usuario, catalogo, cantidad=5):
        """Devuelve una lista de objetos Recomendacion ordenada."""


class RecomendadorPorContenido(Recomendador):
    """Recomendación basada en contenido (content-based filtering).

    La similitud entre dos juegos combina tres señales:
    - Géneros compartidos      (similitud de Jaccard)
    - Plataformas compartidas  (similitud de Jaccard)
    - Cercanía de puntuación

    Los pesos se pueden ajustar al construir el objeto, lo que hace fácil
    experimentar con distintas configuraciones del algoritmo. """

    ESCALA_PUNTUACION = 10.0

    def __init__(self, peso_generos=0.55, peso_plataformas=0.25, peso_puntuacion=0.20):
        total = peso_generos + peso_plataformas + peso_puntuacion
        if abs(total - 1.0) > 0.001:
            raise ValueError("Los pesos del recomendador deben sumar 1.0")
        self._peso_generos = peso_generos
        self._peso_plataformas = peso_plataformas
        self._peso_puntuacion = peso_puntuacion

    # ---------------- Cálculos internos ---------------------------------

    @staticmethod
    def _jaccard(conjunto_a, conjunto_b):
        """Intersección sobre unión: 0 = nada en común, 1 = idénticos."""
        union = conjunto_a | conjunto_b
        if not union:
            return 0.0
        return len(conjunto_a & conjunto_b) / len(union)

    def _similitud_puntuacion(self, juego_a, juego_b):
        diferencia = abs(juego_a.puntuacion - juego_b.puntuacion)
        return max(0.0, 1 - diferencia / self.ESCALA_PUNTUACION)

    def similitud(self, juego_a, juego_b):
        """Porcentaje de similitud (0 a 100) entre dos videojuegos."""
        valor = (
            self._jaccard(juego_a.generos, juego_b.generos) * self._peso_generos
            + self._jaccard(juego_a.plataformas, juego_b.plataformas) * self._peso_plataformas
            + self._similitud_puntuacion(juego_a, juego_b) * self._peso_puntuacion
        )
        return round(valor * 100, 1)

    # ---------------- Interfaz pública -----------------------------------

    def recomendar(self, usuario, catalogo, cantidad=5):
        """
        Compara cada juego no favorito contra todos los favoritos del
        usuario y devuelve los más similares, de mayor a menor.

        Si el usuario calificó bajo alguno de sus favoritos, ese favorito
        pesa menos a la hora de recomendar (le gustó menos).
        """
        favoritos = usuario.favoritos
        if not favoritos:
            return []

        candidatos = [j for j in catalogo if not usuario.es_favorito(j)]
        recomendaciones = []

        for candidato in candidatos:
            puntajes = []
            mejor_favorito = None
            mejor_valor = -1

            for favorito in favoritos:
                valor = self.similitud(candidato, favorito)

                calificacion = usuario.calificacion_de(favorito)
                if calificacion is not None:
                    # Nunca se anula del todo: mínimo 30% de influencia.
                    valor *= max(0.3, calificacion / 10)

                puntajes.append(valor)
                if valor > mejor_valor:
                    mejor_valor = valor
                    mejor_favorito = favorito

            promedio = sum(puntajes) / len(puntajes)
            motivo = f"parecido a '{mejor_favorito.titulo}'" if mejor_favorito else ""
            recomendaciones.append(Recomendacion(candidato, promedio, motivo))

        recomendaciones.sort(reverse=True)
        return recomendaciones[:cantidad]