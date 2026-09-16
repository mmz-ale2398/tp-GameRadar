#TP sistema de recomendación de videojuegos

Materia: Estructura de Datos
Grupo: 23
comision: 2 

alumnos:
-Federico Rodríguez Santos 
-Mauro Bordón DNI: 44968633
-Alejandro Mollo DNI: 44709610

Profesor: Maximiliano zorzoli

# Game Radar

Sistema de recomendación de videojuegos que funciona íntegramente desde la
terminal. Permite buscar, listar y filtrar un catálogo cargado desde un
archivo de texto, calificar títulos, armar una lista de favoritos y recibir
recomendaciones personalizadas calculadas con un algoritmo de similitud
basado en contenido.

Escrito en Python 3, con diseño orientado a objetos y sin dependencias
externas.

---

## Requisitos

- Python 3.8 o superior
- Una terminal con soporte UTF-8 (para los acentos y simbolos)

No hace falta instalar nada: el proyecto usa únicamente la biblioteca
estándar de Python.

Para verificar la versión instalada:

```bash
python3 --version
```

---

## Instalación

1. Descomprimí el proyecto en la carpeta que prefieras.
2. Verificá que la estructura sea la siguiente:

```
GameRadar/
│
├── main.py              # Punto de entrada
├── modelos.py           # Clases del dominio
├── catalogo.py          # Carga y consulta de datos
├── recomendador.py      # Motor de recomendaciones
├── interfaz.py          # Interfaz de terminal
│
└── datos/
    └── videojuegos.txt  # Dataset
```

La carpeta `datos/` con el archivo `videojuegos.txt` es obligatoria: sin ella
el programa avisa del error y termina de forma controlada.

---

## Ejecución

Desde la carpeta raíz del proyecto:

```bash
cd GameRadar
python3 main.py
```

En Windows, según cómo esté instalado Python:

```bash
python main.py
```

Al iniciar, el programa informa cuántos videojuegos cargó, pide un nombre de
usuario (podés dejarlo vacío) y muestra el menú principal:

```
==========================================
                GAME RADAR
           Tu próxima aventura
==========================================
1. Buscar videojuegos
2. Listar catálogo
3. Filtrar videojuegos
4. Calificar videojuego
5. Gestionar favoritos
6. Obtener recomendaciones
7. Salir
```

Para salir, elegí la opción 7 o presioná `Ctrl + C`.

---

## Guía de uso

### 1. Buscar videojuegos

Busca por coincidencia parcial en el título, sin distinguir mayúsculas.
Escribir `witcher` encuentra *The Witcher 3*.

### 2. Listar catálogo

Muestra todos los videojuegos ordenados por título (A-Z), por puntuación
(de mayor a menor) o por año (más nuevos primero).

### 3. Filtrar videojuegos

Combina hasta cuatro criterios: género, plataforma, año y puntuación mínima.
Cualquier criterio que dejes vacío con `ENTER` no se aplica, así que podés
usar uno solo o los cuatro juntos. Antes de pedir el dato, el programa lista
los géneros y plataformas disponibles en el dataset.

### 4. Calificar videojuego

Asigna una puntuación del 1 al 10. Si el texto ingresado coincide con varios
títulos, el programa los lista con su ID y te pide elegir uno (`0` cancela).
Las calificaciones influyen en las recomendaciones.

### 5. Gestionar favoritos

Permite agregar y quitar favoritos, ver la lista actual y consultar el
historial de interacciones de la sesión.

### 6. Obtener recomendaciones

Requiere al menos un favorito. Devuelve los cinco videojuegos más afines,
con su porcentaje de similitud y el favorito que motivó cada sugerencia:

```
Basándonos en tus preferencias:

1. Horizon Zero Dawn
   Género: Acción / Aventura / RPG
   Similitud: 68.8%
   Motivo: parecido a 'The Witcher 3'
```

Los videojuegos que ya están en favoritos nunca se recomiendan.

> Los favoritos, las calificaciones y el historial viven en memoria mientras
> el programa está abierto y se pierden al cerrarlo. El dataset, en cambio,
> es permanente.

---

## El dataset

`datos/videojuegos.txt` usa un campo por columna separado por `|`:

```
ID|Nombre|Géneros|Plataformas|Año|Puntuación
```

Ejemplo:

```
1|The Witcher 3|RPG,Acción,Aventura|PC,PS4,Xbox One,Switch|2015|9.2
```

Detalles del formato:

- Los géneros y las plataformas se separan entre sí con comas.
- El ID y el año son números enteros; la puntuación es decimal (0 a 10).
- Las líneas vacías y las que empiezan con `#` se ignoran, así que podés
  dejar comentarios dentro del archivo.

### Agregar videojuegos

Abrí el archivo con cualquier editor de texto, agregá una línea al final
respetando el formato y guardá en codificación UTF-8. No hace falta tocar
el código: el catálogo se recarga en el próximo arranque.

Si una línea está mal formada, el programa la informa con un aviso y sigue
cargando el resto en lugar de cortarse.

---

## Arquitectura

El sistema se divide en cuatro capas, cada una con una responsabilidad clara.

| Módulo | Rol | Clases principales |
|---|---|---|
| `modelos.py` | Dominio | `Etiqueta`, `Genero`, `Plataforma`, `Videojuego`, `Usuario` |
| `catalogo.py` | Datos | `FuenteDeDatos`, `FuenteTXT`, `Catalogo` |
| `recomendador.py` | Lógica | `Recomendador`, `RecomendadorPorContenido`, `Recomendacion` |
| `interfaz.py` | Presentación | `Consola`, `AplicacionTerminal` |

`main.py` arma las piezas e inyecta las dependencias:

```
FuenteTXT ──> Catalogo ──────┐
Usuario ─────────────────────┼──> AplicacionTerminal
RecomendadorPorContenido ────┘
```

### Encapsulamiento

Los atributos son protegidos (`_atributo`) o privados (`__atributo`) y se
exponen mediante *properties* de solo lectura. Las colecciones internas se
devuelven como copias, de modo que modificar el resultado no altera el
objeto original:

```python
juego.titulo = "Otro"      # AttributeError
generos = juego.generos    # copia: mutarla no afecta al videojuego
```

Las validaciones viven en los constructores y en los métodos que modifican
estado, así que un objeto inválido nunca llega a existir.

### Interfaces

Dos clases abstractas marcan las fronteras entre capas:

- **`FuenteDeDatos`** — cualquier origen de datos que sepa devolver objetos
  `Videojuego`. El sistema usa `FuenteTXT`.
- **`Recomendador`** — cualquier motor que sepa producir recomendaciones a
  partir de un usuario y un catálogo.

Ni la terminal ni el recomendador saben de qué tipo de archivo vinieron los
datos.

---

## Personalización


### Ajustar el algoritmo

La similitud entre dos videojuegos combina tres señales, cada una con su
peso configurable:

| Señal | Cálculo | Peso por defecto |
|---|---|---|
| Géneros compartidos | Índice de Jaccard | 0.55 |
| Plataformas compartidas | Índice de Jaccard | 0.25 |
| Cercanía de puntuación | Diferencia normalizada | 0.20 |

El índice de Jaccard divide los elementos en común por el total de elementos
distintos entre ambos juegos: dos títulos con los mismos tres géneros dan 1,
y dos sin nada en común dan 0.

Para probar otra configuración, pasá los pesos al construir el recomendador
(deben sumar 1.0):

```python
recomendador = RecomendadorPorContenido(
    peso_generos=0.70,
    peso_plataformas=0.10,
    peso_puntuacion=0.20,
)
```

Cuando el usuario califica un favorito, ese favorito pesa proporcionalmente
menos al recomendar, con un piso del 30%: una nota baja reduce su influencia
pero no la elimina, porque el hecho de que esté en favoritos sigue diciendo
algo sobre el gusto del usuario.

---

## Manejo de errores

El programa está pensado para no cerrarse ante entradas incorrectas:

- Las entradas numéricas se validan y se vuelven a pedir si no son válidas.
- Las opciones de menú fuera de rango se rechazan con un aviso.
- Si falta el dataset o no se puede leer, se informa el problema y el
  programa termina de forma controlada.
- Las líneas mal formadas del `.txt` se saltean con un aviso.
- `Ctrl + C` cierra el programa con un mensaje de despedida.

---

## Problemas frecuentes

**`No se encontró el archivo 'datos/videojuegos.txt'`**
Estás ejecutando desde otra carpeta. Hacé `cd` a la raíz del proyecto antes
de correr `python3 main.py`.

**`ModuleNotFoundError: No module named 'modelos'`**
Los cinco archivos `.py` tienen que estar en la misma carpeta que `main.py`.

**Los acentos se ven mal en Windows**
Ejecutá `chcp 65001` en la terminal antes de iniciar el programa para
activar UTF-8.

**No aparecen recomendaciones**
El motor necesita al menos un favorito. Agregá uno desde la opción 5.
