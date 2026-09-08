"""
PALACIO — cuatro años al mando
App web en Flask. Todo el juego corre en Python: esta app arma el estado,
decide qué mostrar y procesa cada elección del jugador. El HTML es solo
la plantilla de salida (Jinja), sin JavaScript de juego.

Cómo se guarda el progreso: en vez de una base de datos, la sesión de Flask
(una cookie firmada) guarda únicamente la lista de índices elegidos hasta
el momento, por ejemplo [0, 2, 1, ...]. Cada vez que hace falta saber el
estado actual (estadísticas, banderas, qué decisión toca), se reconstruye
desde cero con game_engine.replay(choices). Así no hace falta ningún
almacenamiento en el servidor, lo cual encaja perfecto con un despliegue
serverless como Vercel.
"""

import os

from flask import Flask, redirect, render_template, request, send_from_directory, session, url_for

import game_engine as ge

app = Flask(__name__)
# En producción, definí SECRET_KEY como variable de entorno en Vercel.
# El juego no maneja datos sensibles, así que un valor por defecto es
# aceptable para jugar, pero cambiarlo evita que alguien arme una sesión
# falsa a mano.
app.secret_key = os.environ.get("SECRET_KEY", "palacio-clave-de-desarrollo-cambiar-en-produccion")


PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")


def get_choices():
    return session.get("choices", [])


@app.route("/style.css")
def style_css():
    # En Vercel, todo lo que está en /public/ ya se sirve directo por su CDN
    # sin pasar por esta función. Esta ruta es un respaldo para que el CSS
    # también funcione al correr `python app.py` en local.
    return send_from_directory(PUBLIC_DIR, "style.css", mimetype="text/css")


@app.route("/")
def index():
    en_curso = len(get_choices())
    return render_template("intro.html", en_curso=en_curso, total=ge.TOTAL_DECISIONS)


@app.route("/empezar", methods=["POST"])
def empezar():
    session["choices"] = []
    return redirect(url_for("juego"))


@app.route("/juego")
def juego():
    choices = get_choices()
    result = ge.replay(choices)
    if result["done"]:
        return redirect(url_for("final"))

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
    )


@app.route("/elegir", methods=["POST"])
def elegir():
    choices = get_choices()
    result = ge.replay(choices)
    if result["done"]:
        return redirect(url_for("final"))

    decision = ge.decision_at(result["year"], result["day"], result["state"])
    try:
        idx = int(request.form.get("idx", "-1"))
    except ValueError:
        idx = -1
    if idx < 0 or idx >= len(decision["options"]):
        # Elección inválida (formulario manipulado o doble clic raro):
        # simplemente volvemos a mostrar la misma decisión, sin registrar nada.
        return redirect(url_for("juego"))

    choices.append(idx)
    session["choices"] = choices
    return redirect(url_for("juego"))


@app.route("/final")
def final():
    choices = get_choices()
    result = ge.replay(choices)
    if not result["done"]:
        return redirect(url_for("juego"))

    ending_type, title, body = ge.compute_ending(result["state"])
    return render_template(
        "final.html",
        ending_type=ending_type,
        title=title,
        body=body,
        stats=result["state"]["stats"],
        stats_meta=ge.STATS_META,
        log=result["log"],
    )


@app.route("/reiniciar", methods=["POST"])
def reiniciar():
    session.pop("choices", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Solo para correr en local con `python app.py`.
    # En Vercel, la propia plataforma importa `app` y lo sirve.
    app.run(debug=True, port=5000)
