# Palacio — cuatro años al mando (versión Flask)

Simulación política de decisiones, **hecha enteramente en Python** con
[Flask](https://flask.palletsprojects.com/). No hay JavaScript de juego: cada
pantalla la arma y decide el servidor (Python), el navegador solo la muestra.

Gobernás durante 4 años (1 período), con **6 decisiones por año (24 en
total)**. Cada decisión mueve cinco indicadores —Popularidad, Economía,
Seguridad, Relaciones internacionales y Estabilidad institucional— y varias
reaparecen, transformadas, en los años siguientes según lo que elegiste antes.

Si tu gestión sostiene apoyo popular y estabilidad, terminás el mandato y
podés ganar la reelección. Si la seguridad, la economía o el apoyo político
se derrumban del todo, el final puede ser mucho más abrupto: una salida de
emergencia en avión, un conflicto armado interno, un colapso económico o una
caída forzada por movilización popular.

Es ficción política genérica: no representa a ningún país, gobierno ni
persona real en particular.

## Cómo está armado

```
palacio-web/
├── app.py             → la app Flask: rutas, sesión, arma cada pantalla
├── game_engine.py      → todo el contenido (24 decisiones) y las reglas de finales
├── cli.py               → la misma simulación jugable por terminal
├── requirements.txt
├── .python-version
├── templates/           → las páginas HTML (Jinja2), sin lógica de juego
│   ├── base.html
│   ├── intro.html
│   ├── decision.html
│   └── final.html
└── public/
    └── style.css        → estilos, servidos como estático
```

**Cómo se guarda el progreso, sin base de datos:** la sesión de Flask (una
cookie firmada) guarda únicamente la lista de opciones que elegiste, por
ejemplo `[0, 2, 1, 0, ...]`. Cada vez que hace falta saber en qué estado
está la partida, `game_engine.replay()` reconstruye todo desde cero: vuelve
a calcular estadísticas, banderas y el historial completo a partir de esa
lista. Es puro Python, no necesita ningún almacenamiento en el servidor —
por eso funciona bien en un entorno serverless como Vercel.

## Jugar en local

**Versión web (Flask):**
```bash
cd palacio-web
python3 -m venv .venv && source .venv/bin/activate   # opcional pero recomendado
pip install -r requirements.txt
python app.py
# abrir http://127.0.0.1:5000
```

**Versión de consola (sin dependencias):**
```bash
cd palacio-web
python3 cli.py
```

Las dos comparten el mismo `game_engine.py`, así que el contenido y los
finales son exactamente los mismos en ambas.

## Subir a Vercel

Hoy Vercel detecta Flask automáticamente y lo despliega **sin ningún
archivo de configuración** (no hace falta `vercel.json`): solo necesita
encontrar una instancia Flask llamada `app` en `app.py` en la raíz del
proyecto, y un `requirements.txt` con las dependencias. Esta carpeta ya
está armada así.

### Opción A — CLI de Vercel (la más rápida)
```bash
npm i -g vercel        # si no la tenés instalada
cd palacio-web
vercel                 # crea un deploy de prueba (preview)
vercel --prod          # lo publica en la URL definitiva
```

### Opción B — Conectar un repo de GitHub
1. Subí la carpeta `palacio-web` a un repositorio de GitHub.
2. En https://vercel.com/new, importá el repo.
3. Vercel detecta Flask solo — no toques el "build command" ni el "output
   directory", dejalos como están.
4. Cada `git push` a la rama principal despliega una nueva versión sola.

### Opción C — Arrastrar la carpeta
También podés arrastrar la carpeta `palacio-web` directo en
https://vercel.com/new sin pasar por Git, aunque la opción con Git es más
cómoda para seguir iterando después.

### Una recomendación de seguridad (opcional)
`app.py` usa una `SECRET_KEY` por defecto para poder correr sin configurar
nada. Como el juego no maneja datos sensibles, no es obligatorio cambiarla,
pero si querés hacerlo bien: en el dashboard de Vercel, andá a **Settings →
Environment Variables** del proyecto y agregá `SECRET_KEY` con cualquier
cadena larga al azar. La app la va a usar automáticamente sin tocar código.

## Cómo agregar o cambiar decisiones

Todo el contenido vive en `game_engine.py`, dentro de las funciones
`year1_decisions()` a `year4_decisions()`. Cada decisión es una función que
recibe el estado actual del juego (`s`, con `s["stats"]` y `s["flags"]`) y
devuelve un diccionario:

```python
def d1(s):
    return {
        "tag": "Categoría corta",
        "title": "Título de la decisión",
        "text": ["Párrafo 1.", "Párrafo 2 opcional."],
        "options": [
            {
                "label": "Lo que puede elegir el jugador",
                "effects": {"pop": -5, "eco": 3},       # suma/resta sobre 0-100
                "flags": {"alguna_bandera": "valor"},    # se puede leer en años siguientes
            },
            # ...más opciones
        ],
    }
```

Como la función recibe `s`, puede leer `s["flags"]` o `s["stats"]` y
devolver un texto o unas opciones distintas según lo que pasó antes — así es
como las decisiones "se relacionan" entre años (mirá, por ejemplo,
`year2_decisions` → `d1`, que cambia según lo que elegiste en el subsidio a
los combustibles del año 1).

Los finales se calculan en `compute_ending(state)`, más abajo en el mismo
archivo: ahí se definen los umbrales de cada desenlace (huida, colapso
económico, conflicto armado, caída popular, reelección, transición
ordenada). Ajustar esos números es la forma más rápida de hacer el juego
más fácil o más despiadado.

No hace falta tocar `app.py`, `cli.py` ni las plantillas para agregar o
cambiar decisiones — todo el contenido está aislado en `game_engine.py`.
