*This project has been created as part of the 42 curriculum by lajen-li, cscaroni.*

# A-Maze-ing

## Descripción

A-Maze-ing es un generador de laberintos escrito en Python. A partir de
un sencillo archivo de configuración, genera un laberinto, lo muestra
visualmente en la terminal con colores, y lo escribe en un archivo de
salida usando una codificación hexadecimal de paredes.

El generador admite dos modos:

- **Laberinto perfecto** (`PERFECT=True`): existe exactamente un camino
  entre la entrada y la salida, sin bucles.
- **Tablero Pac-Man** (`PERFECT=False`, el valor por defecto): un tablero
  totalmente conectado con varias rutas independientes y sin callejones
  sin salida, jugable por un juego tipo Pac-Man.

Los laberintos incluyen un **patrón "42"** integrado en el centro, el cual se activa automáticamente siempre que las dimensiones del laberinto permitan su correcta visualización (mínimo 14x11). El programa cuenta con un menú interactivo que permite al usuario regenerar el diseño, visualizar u ocultar la solución óptima, alternar entre diversos temas de colores y exportar el resultado a archivos de texto.

- **Nota técnica:**  Para garantizar el funcionamiento correcto, el programa valida las dimensiones al inicio; si los valores introducidos están fuera del rango permitido (WIDTH = 5-52, HEIGHT= 5-24), el sistema lanzará un ValueError impidiendo la generación.


## Instrucciones

El proyecto requiere **Python 3.10 o superior**.

Instala las dependencias y ejecuta el programa usando el `Makefile`
incluido:

```
make install      # crea un entorno virtual e instala las dependencias
make run          # ejecuta el programa con config.txt
```

También puedes ejecutarlo directamente:

```
python3 a_maze_ing.py config.txt
```

Otras reglas útiles del Makefile:

```
make lint         # ejecuta flake8 y mypy
make debug        # ejecuta el programa con pdb
make clean        # elimina __pycache__ y .mypy_cache
make fclean       # elimina también el entorno virtual y el ejecutable
make re           # reconstruye desde cero
```

## Recursos
- Peer-to-peer: consultas y revisión con compañeros de 42. 
- Más información en la sección **Uso de IA**


## Formato del archivo de configuración

El archivo de configuración contiene un par `CLAVE=VALOR` por línea. Las
líneas en blanco y las que empiezan por `#` se ignoran.

Claves obligatorias:

| Clave       | Descripción                       | Ejemplo                |
|-------------|-----------------------------------|------------------------|
| WIDTH       | Ancho del laberinto (nº de celdas)| WIDTH=20               |
| HEIGHT      | Alto del laberinto (nº de celdas) | HEIGHT=12              |
| ENTRY       | Coordenadas de entrada (x,y)      | ENTRY=0,0              |
| EXIT        | Coordenadas de salida (x,y)       | EXIT=19,11             |
| OUTPUT_FILE | Nombre del archivo de salida      | OUTPUT_FILE=maze.txt   |
| PERFECT     | True para un laberinto perfecto   | PERFECT=False          |

Clave opcional:

| Clave | Descripción                                | Ejemplo |
|-------|--------------------------------------------|---------|
| SEED  | Semilla entera para laberintos reproducibles | SEED=7  |

Restricciones: WIDTH debe estar entre 5 y 52, HEIGHT entre 5 y 24. ENTRY
y EXIT deben estar dentro del laberinto, ser distintas entre sí, y no
solaparse con el patrón "42".

## Algoritmo de generación del laberinto

El laberinto se construye usando el algoritmo **Recursive Backtracker**
(una búsqueda en profundidad aleatorizada). Partiendo de la celda
superior izquierda, el generador se mueve repetidamente a un vecino no
visitado al azar, abriendo la pared entre ambos, y retrocede con una
pila cuando llega a una celda sin vecinos no visitados. Esto continúa
hasta que todas las celdas alcanzables han sido visitadas, produciendo
un laberinto perfecto.

Para el modo Pac-Man (`PERFECT=False`), se ejecutan dos pasadas
adicionales tras la construcción:

- `add_loops` abre alrededor del 10% de las paredes restantes para crear
  rutas independientes, sin generar nunca un área 3x3 completamente
  abierta.
- `braid` elimina los callejones sin salida abriendo una pared adicional
  por cada celda que tiene un único vecino abierto, dando como resultado
  un tablero totalmente trenzado sin callejones.

El camino más corto de la entrada a la salida se calcula después con una
**búsqueda en anchura (BFS)**.

### Por qué este algoritmo

Se eligió el Recursive Backtracker porque es sencillo de implementar de
forma iterativa, garantiza un laberinto perfecto (un árbol de expansión
de la cuadrícula), y produce pasillos largos y sinuosos que quedan bien
visualmente. Su salida perfecta es además el punto de partida ideal para
el modo Pac-Man: los bucles y el trenzado se añaden después en pasos
controlados y separados, lo que mantiene cada etapa fácil de razonar y
de verificar.
La elección del Recursive Backtracker permite una generación eficiente con una complejidad temporal de $O(N)$ siendo N el número de celdas, lo cual es óptimo para las dimensiones requeridas.

Se eligió el algoritmo BFS (Búsqueda en Anchura) para la resolución del laberinto debido a su propiedad fundamental de optimalidad en grafos no ponderados: **Garantía del camino más corto.** 

A diferencia de las búsquedas en profundidad (como el propio Recursive Backtracker), que pueden encontrar caminos serpenteantes e ineficientes, el **BFS** explora el laberinto por niveles de distancia desde la entrada. Esto asegura matemáticamente que **el primer camino hallado hacia la salida sea el más corto posible**.

Eficiencia algorítmica: BFS tiene una complejidad temporal de $O(V + E)$ (donde $V$ son las celdas y $E$ las conexiones entre ellas). Dado que en nuestro laberinto el número de celdas y conexiones es lineal respecto al área, el rendimiento es óptimo incluso en las dimensiones máximas permitidas.Independencia de la estructura: El BFS es agnóstico a la topología del laberinto; **funciona con la misma eficacia tanto en laberintos perfectos (árboles) como en los laberintos de modo Pac-Man** que contienen ciclos, garantizando siempre una solución óptima.

## Módulo reutilizable

La lógica de generación del laberinto vive en un módulo independiente,
`maze_generator.py` (con su ayudante `cell.py`), que puede instalarse con
pip e importarse en un proyecto futuro.

### Uso básico

```python
from maze_generator import MazeGenerator

config = {
    "WIDTH": 20,
    "HEIGHT": 12,
    "ENTRY": (0, 0),
    "EXIT": (19, 11),
    "OUTPUT_FILE": "maze.txt",
    "PERFECT": True,
}
generator = MazeGenerator(config, seed=42)
generator.stamp_42()
generator.generate()
generator.display()
```

Para el modo Pac-Man (`PERFECT=False`), llama también a
`generator.add_loops()` y `generator.braid()` después de `generate()`.

### Parámetros personalizados

El constructor es `MazeGenerator(data, seed=None)`:

- `data`: un diccionario con las claves WIDTH, HEIGHT, ENTRY, EXIT,
  OUTPUT_FILE, PERFECT y, opcionalmente, SEED.
- `seed`: un entero opcional para reproducibilidad. La misma semilla
  produce siempre el mismo laberinto. Si es `None`, se usa la SEED del
  `data`, o una aleatoria si tampoco está.

### Acceso a la estructura y a una solución

```python
generator.matrix      # lista 2D de objetos Cell (la cuadrícula)
generator.seed        # la semilla realmente usada
generator.width       # ancho del laberinto
generator.height      # alto del laberinto

solution = generator.find_path()   # p.ej. "SSEEN..." de entrada a salida
generator.path_cells               # lista de objetos Cell del camino
```

Cada `Cell` expone `.north`, `.south`, `.east`, `.west`
(`True` = pared cerrada) y sus coordenadas `.x`, `.y`. La estructura en
memoria no está necesariamente en el mismo formato que el archivo de
salida.

### Construir el paquete

El módulo reutilizable se empaqueta con `pyproject.toml`. Para
construirlo:

```
pip install build
python3 -m build
```

Esto genera `mazegen-1.0.0-py3-none-any.whl` y `mazegen-1.0.0.tar.gz` en
la carpeta `dist/`.

## Formato del archivo de salida

Cada celda se escribe como un dígito hexadecimal en minúscula que
codifica sus paredes cerradas (Norte=1, Este=2, Sur=4, Oeste=8), una fila
por línea. Tras una línea en blanco, siguen tres líneas: las coordenadas
de entrada, las de salida y el camino más corto de entrada a salida
(usando las letras N, E, S, W).

## Funciones avanzadas

- **Temas de colores**: varias paletas de colores seleccionables para la
  visualización del laberinto (Default, Cyberpunk, Barbie, Oasis, Nebula,
  Arctic).
- **Animación de generación**: el laberinto puede dibujarse paso a paso a
  medida que se genera.
- **Exportar captura**: el laberinto actual puede guardarse como arte
  ANSI en color en un archivo de texto.
- **Tablero totalmente trenzado (bonus)**: en modo Pac-Man el tablero mayormente no tiene ningún callejón sin salida.

## Uso de IA
- **Debugging:**
	Apoyo en la identificación de errores lógicos y de ejecución, incluyendo la depuración de conflictos en la gestión de dependencias y el refinamiento de la estructura de las clases para cumplir con estándares de calidad.

- **Aclaración de conceptos:**
	Consulta técnica sobre estructuras de datos (colas para BFS, pilas para el Backtracker) y principios de diseño de software (como el principio DRY - Don't Repeat Yourself), permitiendo una implementación más sólida y eficiente.

- **Asistencia sobre el desarrollo de funcionalidades que escapaban a nuestro nivel actual:**
	Soporte técnico para la implementación de algoritmos de post-procesamiento (add_loops y braid), superando retos algorítmicos que excedían nuestra experiencia previa y facilitando la transición de un laberinto perfecto a uno braided.

- **Generación de documentación:**
	Asistencia en la redacción técnica de este documento y la creación de archivos de configuración (LICENSE.md), asegurando la claridad, el tono profesional y la correcta atribución legal del software.

- **Guía para la creación del proyecto y aclaración de ambigüedades en el pdf:**
	Soporte para interpretar requisitos específicos de la documentación técnica del proyecto (PDF), ayudando a desglosar las tareas y estructurar el Makefile y la jerarquía de directorios.

- **Generación del `pyproject.toml`:**
	Automatización en la creación y validación de archivos de configuración de herramientas (tooling), específicamente en la generación del pyproject.toml para estandarizar el uso de flake8 y mypy, garantizando la calidad del código mediante la integración continua de linters.


## Equipo y gestión del proyecto

- **Roles**: La implementación, pruebas y validación final del comportamiento del programa fueron realizadas de forma colaborativa por el equipo. Adoptamos un modelo de trabajo integrado donde las miembros participaron activamente en todas las fases del ciclo de vida del programa, asegurando que el conocimiento técnico fuera compartido y consistente entre nosotras.

- **Planificación y cómo evolucionó**: Inicialmente, establecimos una planificación basada en las funcionalidades básicas exigidas. Sin embargo, a medida que avanzamos, la complejidad de los algoritmos (especialmente el paso de laberintos perfectos a laberintos braided) y el cambio del subject a mitad de la realización del proyecto, nos obligó a adoptar un enfoque de desarrollo iterativo. Ajustamos nuestra hoja de ruta para priorizar la estabilidad del núcleo antes de implementar las interfaces interactivas, lo que nos permitió gestionar mejor los riesgos técnicos y las ambigüedades del enunciado conforme detectábamos retos imprevistos.

- **Qué funcionó bien**: La comunicación constante y la revisión cruzada de código (code review) fueron clave para mantener un estándar de calidad homogéneo. El uso de un entorno virtual común y herramientas de linting (Flake8, Mypy) desde el principio evitó fricciones al integrar el trabajo de ambas. 

- **Qué se podría mejorar**: La gestión de la documentación técnica inicial podría haber sido más rigurosa. En futuras ocasiones, dedicaríamos más tiempo en la fase de diseño previo teniendo en cuenta los bonus y dando prioridad al código para definir la arquitectura de las clases, lo que habría reducido la necesidad de refactorizar componentes ya construidos.

- **Herramientas específicas usadas**:

	- ***Control de versiones***: Git para la gestión del repositorio y el historial de cambios.

	- ***Calidad de código***: Flake8 para asegurar el cumplimiento de PEP 8 y Mypy para la verificación de tipado estático.

	- ***Entorno***: Python 3.13 con gestión de dependencias mediante venv y automatización de tareas a través de Makefile.

	- ***Asistencia estratégica***: Inteligencia Artificial para el debugging, aclaración de conceptos algorítmicos, asistencia en la configuración del entorno (pyproject.toml) y redacción técnica de documentación.
