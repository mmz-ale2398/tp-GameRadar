"""
modelos.py
----------
Clases principales del dominio de Game Radar.

Todas las clases aplican encapsulamiento: los atributos se guardan como
protegidos (_atributo) y se exponen mediante properties de solo lectura,
salvo donde tiene sentido permitir modificación controlada.

Jerarquía de clases:

    Etiqueta (base abstracta)
        ├── Genero
        └── Plataforma

    Videojuego
    Usuario
"""

from abc import ABC, abstractmethod


class Etiqueta(ABC):
    """
    Clase base para las características categóricas de un videojuego
    (géneros y plataformas). Define el comportamiento común: normalizar
    el nombre, compararse e insertarse en conjuntos sin duplicados.
    """

    def __init__(self, nombre):
        nombre = str(nombre).strip()
        if not nombre:
            raise ValueError("El nombre de la etiqueta no puede estar vacío.")
        self._nombre = nombre

    @property
    def nombre(self):
        """Getter de solo lectura del nombre original."""
        return self._nombre

    @property
    def clave(self):
        """Clave normalizada, usada para comparar sin importar mayúsculas."""
        return self._nombre.lower()

    @abstractmethod
    def tipo(self):
        """Cada subclase indica qué tipo de etiqueta representa."""

    # Estos dos métodos permiten usar las etiquetas dentro de set()
    # y comparar 'RPG' con 'rpg' como si fueran la misma etiqueta.
    def __eq__(self, otro):
        return isinstance(otro, Etiqueta) and self.clave == otro.clave

    def __hash__(self):
        return hash(self.clave)

    def __repr__(self):
        return self._nombre


class Genero(Etiqueta):
    """Género de un videojuego (RPG, Acción, Aventura, ...)."""

    def tipo(self):
        return "género"


class Plataforma(Etiqueta):
    """Plataforma en la que está disponible un videojuego (PC, PS4, ...)."""

    def tipo(self):
        return "plataforma"


class Videojuego:
    """
    Representa un videojuego del catálogo.

    Los atributos son protegidos y se acceden mediante properties, de modo
    que desde fuera nadie pueda corromper el estado del objeto (por
    ejemplo, asignarle una puntuación de 500).
    """

    def __init__(self, id_juego, titulo, generos, plataformas, anio, puntuacion):
        self._id = int(id_juego)
        self._titulo = str(titulo).strip()
        # Se guardan como conjuntos para evitar duplicados y facilitar
        # las operaciones de intersección/unión del recomendador.
        self._generos = {g if isinstance(g, Genero) else Genero(g) for g in generos}
        self._plataformas = {
            p if isinstance(p, Plataforma) else Plataforma(p) for p in plataformas
        }
        self._anio = int(anio)
        self._puntuacion = float(puntuacion)

        if not self._titulo:
            raise ValueError("El título del videojuego no puede estar vacío.")
        if not 0 <= self._puntuacion <= 10:
            raise ValueError(f"Puntuación fuera de rango en '{self._titulo}'.")

    # ---------------- Getters (properties de solo lectura) -------------

    @property
    def id(self):
        return self._id

    @property
    def titulo(self):
        return self._titulo

    @property
    def generos(self):
        """Devuelve una copia para que nadie modifique el set interno."""
        return set(self._generos)

    @property
    def plataformas(self):
        return set(self._plataformas)

    @property
    def anio(self):
        return self._anio

    @property
    def puntuacion(self):
        return self._puntuacion

    # ---------------- Métodos de consulta ------------------------------

    def tiene_genero(self, nombre_genero):
        return Genero(nombre_genero) in self._generos

    def tiene_plataforma(self, nombre_plataforma):
        return Plataforma(nombre_plataforma) in self._plataformas

    def coincide_titulo(self, texto):
        """Búsqueda parcial, insensible a mayúsculas."""
        return str(texto).strip().lower() in self._titulo.lower()

    def generos_como_texto(self, separador=", "):
        return separador.join(sorted(g.nombre for g in self._generos))

    def plataformas_como_texto(self, separador=", "):
        return separador.join(sorted(p.nombre for p in self._plataformas))

    def ficha(self):
        """Devuelve la ficha completa del juego como texto multilínea."""
        return (
            f"[{self._id:>3}] {self._titulo}\n"
            f"      Género(s):     {self.generos_como_texto()}\n"
            f"      Plataforma(s): {self.plataformas_como_texto()}\n"
            f"      Año:           {self._anio}\n"
            f"      Puntuación:    {self._puntuacion}/10"
        )

    # ---------------- Representación e igualdad ------------------------

    def __repr__(self):
        return f"{self._titulo} ({self.generos_como_texto(' / ')}) {self._puntuacion}"

    def __eq__(self, otro):
        return isinstance(otro, Videojuego) and self._id == otro._id

    def __hash__(self):
        return hash(self._id)


class Usuario:
    """
    Representa al usuario de la sesión: sus favoritos, sus calificaciones
    y su historial de interacciones.

    Las colecciones internas son privadas y solo se exponen como copias,
    para que la única forma de modificarlas sean los métodos de la clase.
    """

    PUNTUACION_MINIMA = 1
    PUNTUACION_MAXIMA = 10
    MAX_HISTORIAL = 100

    def __init__(self, nombre="Jugador"):
        self._nombre = str(nombre).strip() or "Jugador"
        self.__favoritos = set()        # conjunto de objetos Videojuego
        self.__calificaciones = {}      # id_juego -> puntuación
        self.__historial = []           # lista de strings

    @property
    def nombre(self):
        return self._nombre

    @property
    def favoritos(self):
        """Copia ordenada por título de los favoritos actuales."""
        return sorted(self.__favoritos, key=lambda j: j.titulo)

    @property
    def calificaciones(self):
        return dict(self.__calificaciones)

    @property
    def historial(self):
        return list(self.__historial)

    # ---------------- Favoritos ----------------------------------------

    def agregar_favorito(self, juego):
        """Devuelve True si se agregó, False si ya estaba en la lista."""
        if juego in self.__favoritos:
            return False
        self.__favoritos.add(juego)
        self.registrar(f"Agregaste '{juego.titulo}' a favoritos")
        return True

    def quitar_favorito(self, juego):
        """Devuelve True si se quitó, False si no estaba en la lista."""
        if juego not in self.__favoritos:
            return False
        self.__favoritos.discard(juego)
        self.registrar(f"Quitaste '{juego.titulo}' de favoritos")
        return True

    def es_favorito(self, juego):
        return juego in self.__favoritos

    # ---------------- Calificaciones ------------------------------------

    def calificar(self, juego, puntuacion):
        """
        Guarda o actualiza la calificación del usuario para un juego.
        Valida el rango permitido y lanza ValueError si no corresponde.
        """
        puntuacion = int(puntuacion)
        if not self.PUNTUACION_MINIMA <= puntuacion <= self.PUNTUACION_MAXIMA:
            raise ValueError(
                f"La puntuación debe estar entre {self.PUNTUACION_MINIMA} "
                f"y {self.PUNTUACION_MAXIMA}."
            )
        self.__calificaciones[juego.id] = puntuacion
        self.registrar(f"Calificaste '{juego.titulo}' con {puntuacion}/10")
        return puntuacion

    def calificacion_de(self, juego):
        """Devuelve la calificación dada a un juego, o None si no lo calificó."""
        return self.__calificaciones.get(juego.id)

    # ---------------- Historial ------------------------------------------

    def registrar(self, descripcion):
        """Agrega una interacción al historial (recortado a MAX_HISTORIAL)."""
        from datetime import datetime
        marca = datetime.now().strftime("%H:%M:%S")
        self.__historial.append(f"[{marca}] {descripcion}")
        if len(self.__historial) > self.MAX_HISTORIAL:
            self.__historial.pop(0)

    def ultimas_interacciones(self, cantidad=10):
        return self.__historial[-cantidad:]

    def __repr__(self):
        return (
            f"Usuario({self._nombre}, favoritos={len(self.__favoritos)}, "
            f"calificaciones={len(self.__calificaciones)})"
        )
