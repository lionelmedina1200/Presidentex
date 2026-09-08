"""
PRESIDENTEX — cuatro años al mando
App web en Flask. Todo el juego corre en Python: esta app arma el estado,
decide qué mostrar y procesa cada elección del jugador. El HTML es solo
la plantilla de salida (Jinja), sin JavaScript de juego.

Cómo se guarda el progreso: en vez de una base de datos, la sesión de Flask
(una cookie firmada) guarda el nombre del jugador y la lista de índices
elegidos hasta el momento, por ejemplo [0, 2, 1, ...]. Cada vez que hace
falta saber el estado actual (estadísticas, banderas, qué decisión toca),
se reconstruye desde cero con game_engine.replay(choices). Así no hace
falta ningún almacenamiento en el servidor, lo cual encaja perfecto con un
despliegue serverless como Vercel.

Nota de velocidad: cada elección se resuelve en una sola respuesta (la
propia pantalla siguiente), sin pasar por un redirect intermedio. Eso evita
un viaje de ida y vuelta al servidor por cada clic.
"""

import os

from flask import Flask, redirect, render_template, request, send_from_directory, session, url_for

import game_engine as ge

app = Flask(__name__)
# En producción, definí SECRET_KEY como variable de entorno en Vercel.
# El juego no maneja datos sensibles, así que un valor por defecto es
# aceptable para jugar, pero cambiarlo evita que alguien arme una sesión
# falsa a mano.
app.secret_key = os.environ.get("SECRET_KEY", "presidentex-clave-de-desarrollo-cambiar-en-produccion")

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")


def get_choices():
    return session.get("choices", [])


def get_nombre():
    return session.get("nombre", "")


@app.route("/style.css")
def style_css():
    # En Vercel, todo lo que está en /public/ ya se sirve directo por su CDN
    # sin pasar por esta función. Esta ruta es un respaldo para que el CSS
    # también funcione al correr `python index.py` en local.
    return send_from_directory(PUBLIC_DIR, "style.css", mimetype="text/css")


def render_decision_page(result):
    decision = ge.decision_at(result["year"], result["day"], result["state"])
    day_number = (result["year"] - 1) * 6 + result["day"]  # 1..24
    return render_template(
        "decision.html",
        decision=decision,
        stats=result["state"]["stats"],
        stats_meta=ge.STATS_META,
        year=result["year"],
        day=result["day"],
        year_title=ge.YEAR_TITLES[result["year"] - 1],
        day_number=day_number,
        total=ge.TOTAL_DECISIONS,
        nombre=get_nombre(),
    )


def render_final_page(result):
    ending_type, title, body = ge.compute_ending(result["state"])
    return render_template(
        "final.html",
        ending_type=ending_type,
        title=title,
        body=body,
        stats=result["state"]["stats"],
        stats_meta=ge.STATS_META,
        log=result["log"],
        nombre=get_nombre(),
    )


@app.route("/")
def index():
    en_curso = len(get_choices())
    return render_template("intro.html", en_curso=en_curso, total=ge.TOTAL_DECISIONS, nombre=get_nombre())


@app.route("/empezar", methods=["POST"])
def empezar():
    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    nombre_completo = f"{nombre} {apellido}".strip()
    session["nombre"] = nombre_completo if nombre_completo else "Presidente/a"
    session["choices"] = []
    result = ge.replay([])
    return render_decision_page(result)


@app.route("/juego")
def juego():
    choices = get_choices()
    if not get_nombre():
        return redirect(url_for("index"))
    result = ge.replay(choices)
    if result["done"]:
        return render_final_page(result)
    return render_decision_page(result)


@app.route("/elegir", methods=["POST"])
def elegir():
    choices = get_choices()
    if not get_nombre():
        return redirect(url_for("index"))

    result = ge.replay(choices)
    if result["done"]:
        return render_final_page(result)

    decision = ge.decision_at(result["year"], result["day"], result["state"])
    try:
        idx = int(request.form.get("idx", "-1"))
    except ValueError:
        idx = -1

    if idx < 0 or idx >= len(decision["options"]):
        # Elección inválida (formulario manipulado o doble clic raro):
        # volvemos a mostrar la misma decisión, sin registrar nada.
        return render_decision_page(result)

    choices.append(idx)
    session["choices"] = choices

    result2 = ge.replay(choices)
    if result2["done"]:
        return render_final_page(result2)
    return render_decision_page(result2)


@app.route("/final")
def final():
    choices = get_choices()
    result = ge.replay(choices)
    if not result["done"]:
        return render_decision_page(result) if get_nombre() else redirect(url_for("index"))
    return render_final_page(result)


@app.route("/reiniciar", methods=["POST"])
def reiniciar():
    session.pop("choices", None)
    session.pop("nombre", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Solo para correr en local con `python index.py`.
    # En Vercel, la propia plataforma importa `app` y lo sirve.
    app.run(debug=True, port=5000)
