"""
interfaz.py
-----------
Capa de presentación: toda la interacción por terminal vive acá.

`Consola` agrupa las utilidades de entrada/salida validada (es decir, la
parte que evita que el programa se caiga por una entrada incorrecta).
`AplicacionTerminal` es el controlador: conecta al usuario con el catálogo
y el recomendador, sin que esas clases sepan nada de print() ni input().
"""

ANCHO = 42


class Consola:
    """Utilidades estáticas de entrada/salida para la terminal."""

    @staticmethod
    def titulo(texto, subtitulo=None):
        print("=" * ANCHO)
        print(texto.center(ANCHO))
        if subtitulo:
            print(subtitulo.center(ANCHO))
        print("=" * ANCHO)

    @staticmethod
    def separador():
        print("-" * ANCHO)

    @staticmethod
    def entero(mensaje, minimo=None, maximo=None, permitir_vacio=False):
        """
        Pide un entero validado. Con permitir_vacio=True, un ENTER vacío
        devuelve None (útil para filtros opcionales).
        """
        while True:
            entrada = input(mensaje).strip()
            if not entrada and permitir_vacio:
                return None
            try:
                valor = int(entrada)
            except ValueError:
                print("  → Ingresá un número entero válido.")
                continue
            if minimo is not None and valor < minimo:
                print(f"  → El valor mínimo es {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  → El valor máximo es {maximo}.")
                continue
            return valor

    @staticmethod
    def decimal(mensaje, minimo=None, maximo=None, permitir_vacio=False):
        while True:
            entrada = input(mensaje).strip().replace(",", ".")
            if not entrada and permitir_vacio:
                return None
            try:
                valor = float(entrada)
            except ValueError:
                print("  → Ingresá un número válido (ej: 8.5).")
                continue
            if minimo is not None and valor < minimo:
                print(f"  → El valor mínimo es {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  → El valor máximo es {maximo}.")
                continue
            return valor

    @staticmethod
    def texto(mensaje, permitir_vacio=False):
        while True:
            entrada = input(mensaje).strip()
            if entrada or permitir_vacio:
                return entrada
            print("  → La entrada no puede estar vacía.")

    @staticmethod
    def opcion(mensaje, validas):
        opciones = "/".join(str(o) for o in sorted(validas))
        while True:
            valor = Consola.entero(mensaje)
            if valor in validas:
                return valor
            print(f"  → Opción inválida. Elegí entre: {opciones}")

    @staticmethod
    def pausa():
        input("\nPresioná ENTER para continuar...")

    @staticmethod
    def mostrar_juegos(juegos, detallado=True):
        if not juegos:
            print("No se encontraron videojuegos con esos criterios.")
            return
        for juego in juegos:
            print(juego.ficha() if detallado else f"  • {juego!r}")
            if detallado:
                print()


class AplicacionTerminal:
    """
    Controlador principal. Recibe por constructor sus dependencias
    (catálogo, usuario y recomendador), de modo que se pueden intercambiar
    sin modificar esta clase.
    """

    def __init__(self, catalogo, usuario, recomendador):
        self._catalogo = catalogo
        self._usuario = usuario
        self._recomendador = recomendador
        self._activa = True

    # ---------------- Bucle principal -------------------------------------

    def ejecutar(self):
        while self._activa:
            self._mostrar_menu()
            opcion = Consola.opcion("\nSeleccione una opción: ", set(range(1, 8)))
            self._despachar(opcion)

    def _mostrar_menu(self):
        Consola.titulo("GAME RADAR", "Tu próxima aventura")
        print("1. Buscar videojuegos")
        print("2. Listar catálogo")
        print("3. Filtrar videojuegos")
        print("4. Calificar videojuego")
        print("5. Gestionar favoritos")
        print("6. Obtener recomendaciones")
        print("7. Salir")

    def _despachar(self, opcion):
        """Mapea cada opción del menú a su método correspondiente."""
        acciones = {
            1: self.buscar,
            2: self.listar,
            3: self.filtrar,
            4: self.calificar,
            5: self.gestionar_favoritos,
            6: self.recomendar,
            7: self.salir,
        }
        acciones[opcion]()

    # ---------------- Operación 1: BUSCAR ----------------------------------

    def buscar(self):
        Consola.titulo("BUSCAR VIDEOJUEGOS")
        texto = Consola.texto("Título (o parte del título): ")
        resultados = self._catalogo.buscar(texto)

        print()
        Consola.mostrar_juegos(resultados)
        self._usuario.registrar(f"Buscaste '{texto}' ({len(resultados)} resultado/s)")
        Consola.pausa()

    # ---------------- Operación 2: LISTAR ----------------------------------

    def listar(self):
        Consola.titulo("LISTAR CATÁLOGO")
        print("1. Por título (A-Z)")
        print("2. Por puntuación (mayor a menor)")
        print("3. Por año (más nuevos primero)")

        opcion = Consola.opcion("\nOrdenar: ", {1, 2, 3})
        orden = {1: "titulo", 2: "puntuacion", 3: "anio"}[opcion]
        juegos = self._catalogo.listar(orden=orden)

        print(f"\n{len(juegos)} videojuegos en el catálogo:\n")
        Consola.mostrar_juegos(juegos, detallado=False)
        self._usuario.registrar(f"Listaste el catálogo ordenado por {orden}")
        Consola.pausa()

    # ---------------- Operación 3: FILTRAR ---------------------------------

    def filtrar(self):
        Consola.titulo("FILTRAR VIDEOJUEGOS")
        print("Dejá vacío cualquier criterio que no quieras aplicar.\n")

        print("Géneros:", ", ".join(self._catalogo.generos_disponibles()))
        genero = Consola.texto("Género: ", permitir_vacio=True)

        print("\nPlataformas:", ", ".join(self._catalogo.plataformas_disponibles()))
        plataforma = Consola.texto("Plataforma: ", permitir_vacio=True)

        anio = Consola.entero("\nAño: ", minimo=1970, maximo=2100, permitir_vacio=True)
        minima = Consola.decimal(
            "Puntuación mínima (0-10): ", minimo=0, maximo=10, permitir_vacio=True
        )

        resultados = self._catalogo.filtrar(
            genero=genero or None,
            plataforma=plataforma or None,
            anio=anio,
            puntuacion_minima=minima,
        )

        print()
        Consola.mostrar_juegos(resultados)
        self._usuario.registrar(f"Aplicaste filtros ({len(resultados)} resultado/s)")
        Consola.pausa()

    # ---------------- Operación 4: CALIFICAR --------------------------------

    def calificar(self):
        Consola.titulo("CALIFICAR VIDEOJUEGO")
        juego = self._seleccionar_juego()
        if juego is None:
            return

        puntuacion = Consola.entero(
            f"Puntuación para '{juego.titulo}' (1-10): ", minimo=1, maximo=10
        )
        try:
            self._usuario.calificar(juego, puntuacion)
            print(f"\n✔ Calificaste '{juego.titulo}' con {puntuacion}/10.")
        except ValueError as error:
            print(f"\n✖ {error}")

        Consola.pausa()

    # ---------------- Operación 5: FAVORITOS ---------------------------------

    def gestionar_favoritos(self):
        while True:
            Consola.titulo("GESTIONAR FAVORITOS")
            print("1. Agregar a favoritos")
            print("2. Quitar de favoritos")
            print("3. Ver favoritos")
            print("4. Ver historial")
            print("5. Volver")

            opcion = Consola.opcion("\nSeleccione una opción: ", {1, 2, 3, 4, 5})

            if opcion == 5:
                return

            if opcion == 3:
                print()
                favoritos = self._usuario.favoritos
                if not favoritos:
                    print("Todavía no agregaste ningún videojuego a favoritos.")
                else:
                    for juego in favoritos:
                        print(f"  • {juego!r}")
                Consola.pausa()
                continue

            if opcion == 4:
                print()
                interacciones = self._usuario.ultimas_interacciones(15)
                if not interacciones:
                    print("Todavía no hay interacciones en esta sesión.")
                else:
                    for linea in interacciones:
                        print(linea)
                Consola.pausa()
                continue

            juego = self._seleccionar_juego()
            if juego is None:
                continue

            if opcion == 1:
                exito = self._usuario.agregar_favorito(juego)
                print(f"\n{'✔ Agregado' if exito else '• Ya estaba'}: {juego.titulo}")
            else:
                exito = self._usuario.quitar_favorito(juego)
                print(f"\n{'✔ Eliminado' if exito else '• No estaba'}: {juego.titulo}")

            Consola.pausa()

    # ---------------- Operación 6: RECOMENDAR ---------------------------------

    def recomendar(self):
        Consola.titulo("RECOMENDACIONES")

        if not self._usuario.favoritos:
            print("\nTodavía no tenés favoritos.")
            print("Agregá al menos uno para que el radar pueda orientarse.")
            Consola.pausa()
            return

        recomendaciones = self._recomendador.recomendar(
            self._usuario, self._catalogo, cantidad=5
        )

        print("\nBasándonos en tus preferencias:\n")
        for posicion, recomendacion in enumerate(recomendaciones, start=1):
            juego = recomendacion.juego
            print(f"{posicion}. {juego.titulo}")
            print(f"   Género: {juego.generos_como_texto(' / ')}")
            print(f"   Similitud: {recomendacion.similitud}%")
            print(f"   Motivo: {recomendacion.motivo}")
            print()

        print("=" * ANCHO)
        self._usuario.registrar(f"Recibiste {len(recomendaciones)} recomendaciones")
        Consola.pausa()

    # ---------------- Operación 7: SALIR ---------------------------------------

    def salir(self):
        self._activa = False
        print(f"\n¡Gracias por usar Game Radar, {self._usuario.nombre}!")

    # ---------------- Apoyo -----------------------------------------------------

    def _seleccionar_juego(self):
        """
        Pide un título, resuelve ambigüedades si hay varias coincidencias
        y devuelve el Videojuego elegido (o None si se cancela).
        """
        texto = Consola.texto("Título (o parte del título): ")
        coincidencias = self._catalogo.buscar(texto)

        if not coincidencias:
            print("No se encontró ningún videojuego con ese título.")
            Consola.pausa()
            return None

        if len(coincidencias) == 1:
            return coincidencias[0]

        print(f"\nSe encontraron {len(coincidencias)} coincidencias:\n")
        for juego in coincidencias:
            print(f"  [{juego.id:>3}] {juego.titulo} ({juego.anio})")

        ids_validos = {j.id for j in coincidencias}
        elegido = Consola.entero("\nID del videojuego (0 para cancelar): ", minimo=0)

        if elegido == 0:
            return None
        if elegido not in ids_validos:
            print("Ese ID no está entre las coincidencias.")
            Consola.pausa()
            return None

        return self._catalogo.obtener_por_id(elegido)