#!/usr/bin/env python3
"""
PALACIO — cuatro años al mando
Versión de consola (Python) de la simulación política.
Mismo motor de decisiones y finales que la versión web (index.html + game.js);
pensada para jugar en terminal o para testear la lógica de balance del juego.
"""

"""
PALACIO — cuatro años al mando
Motor del juego: todo el contenido (24 decisiones, 4 años) y las reglas de
finales. No depende de Flask ni de nada web: lo importan tanto la app web
(app.py) como la versión de consola (cli.py).
"""

class StatMeta:
    """Pequeño contenedor con atributos .key/.label, para poder escribir
    m.key / m.label tanto en Python como en las plantillas Jinja."""
    __slots__ = ("key", "label")

    def __init__(self, key, label):
        self.key = key
        self.label = label


STATS_META = [
    StatMeta("pop", "Popularidad"),
    StatMeta("eco", "Economía"),
    StatMeta("seg", "Seguridad"),
    StatMeta("rel", "Relaciones internacionales"),
    StatMeta("est", "Estabilidad institucional"),
]


def clamp(v):
    return max(0, min(100, round(v)))


def fresh_state():
    return {
        "year": 1,
        "day": 1,
        "stats": {"pop": 55, "eco": 52, "seg": 48, "rel": 55, "est": 55},
        "flags": {},
        "log": [],
    }


def apply_effects(state, effects):
    for k, v in (effects or {}).items():
        if k in state["stats"]:
            state["stats"][k] = clamp(state["stats"][k] + v)


def set_flags(state, flags):
    state["flags"].update(flags or {})


def worst_stat(state, keys):
    return min(keys, key=lambda k: state["stats"][k])


# ============================================================
# CONTENIDO: 24 decisiones (4 años x 6), con ramificación por flags
# ============================================================

def year1_decisions():
    def d1(s):
        return {
            "tag": "Gabinete", "title": "El primer nombramiento",
            "text": ["Juraste el cargo hace apenas una semana. Tu primera decisión de peso: a quién nombrás Primer Ministro."],
            "options": [
                {"label": "Un técnico sin partido", "effects": {"est": 8, "eco": 4, "pop": -3}, "flags": {"pm": "tecnocrata"}},
                {"label": "Un dirigente de tu propio espacio político", "effects": {"pop": 5, "est": -5}, "flags": {"pm": "aliado"}},
                {"label": "Un general retirado", "effects": {"seg": 8, "rel": -4, "est": -6}, "flags": {"pm": "militar"}},
            ],
        }

    def d2(s):
        return {
            "tag": "Seguridad", "title": "Las pandillas de la capital",
            "text": ["Grupos armados controlan barrios enteros y bloquean la ruta al puerto."],
            "options": [
                {"label": "Negociar una tregua", "effects": {"seg": 9, "pop": -4, "est": -6}, "flags": {"gang": "trato"}},
                {"label": "Operativo policial de gran escala", "effects": {"pop": 6, "eco": -4, "seg": -3}, "flags": {"gang": "operativo"}},
                {"label": "Pedir apoyo militar internacional", "effects": {"rel": 8, "seg": 4, "pop": -6}, "flags": {"gang": "ayuda_externa"}},
            ],
        }

    def d3(s):
        return {
            "tag": "Economía", "title": "El subsidio a los combustibles",
            "text": ["El fondo que sostiene el precio del combustible está por agotarse."],
            "options": [
                {"label": "Eliminar el subsidio de una vez", "effects": {"eco": 11, "pop": -14}, "flags": {"fuel": "shock"}},
                {"label": "Mantener el subsidio como está", "effects": {"eco": -10, "pop": 6}, "flags": {"fuel": "mantenido"}},
                {"label": "Reducirlo a la mitad y compensar", "effects": {"eco": 3, "pop": -4, "est": 3}, "flags": {"fuel": "parcial"}},
            ],
        }

    def d4(s):
        return {
            "tag": "Relaciones internacionales", "title": "La oferta de Naciones Unidas",
            "text": ["Una misión de la ONU ofrece tropas de estabilización y financiamiento atado a reformas."],
            "options": [
                {"label": "Aceptar tropas de estabilización", "effects": {"seg": 9, "rel": 7, "pop": -8}, "flags": {"un": "tropas"}},
                {"label": "Aceptar solo ayuda económica", "effects": {"eco": 8, "rel": 3}, "flags": {"un": "solo_ayuda"}},
                {"label": "Rechazar toda intervención extranjera", "effects": {"pop": 10, "rel": -12, "est": -3}, "flags": {"un": "rechazo"}},
            ],
        }

    def d5(s):
        return {
            "tag": "Institucional", "title": "El desvío de fondos",
            "text": ["Dinero de un programa de Obras Públicas no llegó a destino. Todavía no es público."],
            "options": [
                {"label": "Denunciarlo públicamente y destituir", "effects": {"est": 7, "rel": 3, "pop": 6}, "flags": {"corrupcion": "expuesta"}},
                {"label": "Taparlo para no debilitar al gobierno", "effects": {"est": -3}, "flags": {"corrupcion": "tapada"}},
                {"label": "Despedir en silencio a los implicados", "effects": {"est": 2, "pop": -2}, "flags": {"corrupcion": "silenciosa"}},
            ],
        }

    def d6(s):
        return {
            "tag": "Emergencia", "title": "El huracán",
            "text": ["Un huracán golpea el sur del país. Hay pueblos incomunicados."],
            "options": [
                {"label": "Movilizar todos los recursos del Estado", "effects": {"pop": 10, "eco": -9, "seg": 2}, "flags": {"huracan": "propio"}},
                {"label": "Pedir ayuda internacional de inmediato", "effects": {"rel": 6, "pop": 4, "eco": 2}, "flags": {"huracan": "ayuda"}},
                {"label": "Responder con lo mínimo", "effects": {"pop": -12, "eco": 2}, "flags": {"huracan": "lento"}},
            ],
        }

    return [d1, d2, d3, d4, d5, d6]


def year2_decisions():
    def d1(s):
        f = s["flags"].get("fuel")
        if f == "shock":
            return {
                "tag": "Calle", "title": "La calle no lo olvidó",
                "text": ["El aumento de combustibles sigue doliendo. Sindicatos anuncian un paro nacional."],
                "options": [
                    {"label": "Reprimir el paro y sostener la medida", "effects": {"seg": 3, "pop": -11, "est": 2}, "flags": {"paro": "reprimido"}},
                    {"label": "Dar marcha atrás parcial en el precio", "effects": {"eco": -6, "pop": 8}, "flags": {"paro": "cedido"}},
                    {"label": "Abrir una mesa de diálogo", "effects": {"est": 4, "pop": 3, "eco": -2}, "flags": {"paro": "dialogo"}},
                ],
            }
        if f == "mantenido":
            return {
                "tag": "Economía", "title": "La factura del subsidio",
                "text": ["Las reservas están en nivel crítico. Un organismo internacional ofrece un préstamo con condiciones duras."],
                "options": [
                    {"label": "Tomar el préstamo y aceptar condiciones", "effects": {"eco": 10, "pop": -9, "rel": 3}, "flags": {"deuda": "aceptada"}},
                    {"label": "Rechazar el préstamo y recortar gasto", "effects": {"eco": 2, "pop": -5, "est": -2}, "flags": {"deuda": "rechazada"}},
                    {"label": "Empezar ahora a bajar el subsidio gradualmente", "effects": {"eco": 5, "pop": -6}, "flags": {"fuel": "shock"}},
                ],
            }
        return {
            "tag": "Economía", "title": "El ajuste a mitad de camino",
            "text": ["La reducción parcial del subsidio compró tiempo, pero no resolvió el déficit."],
            "options": [
                {"label": "Completar el ajuste este año", "effects": {"eco": 8, "pop": -9}, "flags": {"fuel": "shock"}},
                {"label": "Volver a subsidiar por completo", "effects": {"pop": 6, "eco": -6}, "flags": {"fuel": "mantenido"}},
                {"label": "Mantener el esquema mixto", "effects": {"est": 2}, "flags": {}},
            ],
        }

    def d2(s):
        g = s["flags"].get("gang")
        if g == "trato":
            return {
                "tag": "Seguridad", "title": "La tregua se queda corta",
                "text": ["Los grupos armados piden ahora control formal sobre un tramo clave de ruta."],
                "options": [
                    {"label": "Ceder el tramo pedido", "effects": {"seg": 4, "est": -9, "pop": -6}, "flags": {"gang": "trato_ampliado"}},
                    {"label": "Cortar la negociación y lanzar un operativo", "effects": {"seg": -6, "pop": 5, "est": 2}, "flags": {"gang": "operativo"}},
                    {"label": "Llamar a mediadores comunitarios", "effects": {"est": 3, "seg": 1}, "flags": {"gang": "mediado"}},
                ],
            }
        if g == "operativo":
            seg_ok = s["stats"]["seg"] >= 55
            return {
                "tag": "Seguridad", "title": "Represalia",
                "text": ["Tras el operativo del año pasado, un grupo armado ataca una comisaría como represalia."],
                "options": [
                    {"label": "Responder con una ofensiva mayor", "effects": {"seg": 10 if seg_ok else -10, "pop": 4}, "flags": {"gang": "ofensiva"}},
                    {"label": "Reforzar solo la protección de comisarías", "effects": {"seg": 3, "est": 2}, "flags": {"gang": "defensivo"}},
                    {"label": "Abrir un canal de negociación pese a todo", "effects": {"seg": 5, "pop": -5, "est": -3}, "flags": {"gang": "trato"}},
                ],
            }
        return {
            "tag": "Seguridad", "title": "El incidente de la misión internacional",
            "text": ["Personal de la misión internacional se ve envuelto en un altercado con civiles."],
            "options": [
                {"label": "Exigir una investigación independiente", "effects": {"pop": 5, "rel": -6, "est": 3}, "flags": {"un": "tension"}},
                {"label": "Respaldar a la misión y pedir discreción", "effects": {"rel": 4, "pop": -7}, "flags": {"un": "respaldada"}},
                {"label": "Pedir que se reduzca el despliegue", "effects": {"rel": -2, "pop": 2, "seg": -2}, "flags": {"un": "reduccion"}},
            ],
        }

    def d3(s):
        return {
            "tag": "Defensa", "title": "Reconstituir las Fuerzas Armadas",
            "text": ["Un sector de tu gobierno propone recrear un ejército propio como contrapeso a los grupos armados."],
            "options": [
                {"label": "Recrear las Fuerzas Armadas desde cero", "effects": {"seg": 8, "rel": -3, "est": -6}, "flags": {"ejercito": "restaurado"}},
                {"label": "Fortalecer solo a la Policía Nacional", "effects": {"seg": 4, "est": 2}, "flags": {"ejercito": "no"}},
                {"label": "No invertir en fuerza; priorizar lo social", "effects": {"pop": 6, "seg": -6, "eco": -2}, "flags": {"ejercito": "no"}},
            ],
        }

    def d4(s):
        return {
            "tag": "Economía", "title": "La diáspora",
            "text": ["Las remesas sostienen a cientos de miles de familias. ¿Cómo tratarlas?"],
            "options": [
                {"label": "Incentivos fiscales para inversión de la diáspora", "effects": {"eco": 7, "pop": 2}, "flags": {"diaspora": "incentivo"}},
                {"label": "Impuesto a las remesas", "effects": {"eco": 6, "pop": -10}, "flags": {"diaspora": "impuesto"}},
                {"label": "Un programa mixto y moderado", "effects": {"eco": 3, "pop": 1}, "flags": {"diaspora": "mixto"}},
            ],
        }

    def d5(s):
        return {
            "tag": "Institucional", "title": "Elecciones legislativas de medio término",
            "text": ["Las encuestas internas no te favorecen del todo."],
            "options": [
                {"label": "Garantizar elecciones limpias", "effects": {"est": 9, "rel": 4, "pop": 3}, "flags": {"elecciones_medio": "limpias"}},
                {"label": "Inclinar la balanza a tu favor", "effects": {"pop": -3, "est": -9}, "flags": {"elecciones_medio": "fraude"}},
                {"label": "Posponer la elección", "effects": {"est": -6, "rel": -6, "pop": 2}, "flags": {"elecciones_medio": "postergadas"}},
            ],
        }

    def d6(s):
        return {
            "tag": "Emergencia", "title": "Hambre en el valle agrícola",
            "text": ["Una sequía prolongada golpea la principal región agrícola del país."],
            "options": [
                {"label": "Declarar emergencia y pedir ayuda internacional", "effects": {"rel": 4, "pop": 6, "eco": -2}, "flags": {"hambruna": "ayuda_externa"}},
                {"label": "Usar reservas estratégicas del Estado", "effects": {"eco": -9, "pop": 8, "est": 2}, "flags": {"hambruna": "reservas"}},
                {"label": "Delegar la respuesta en ONGs", "effects": {"pop": -8, "eco": 2}, "flags": {"hambruna": "delegada"}},
            ],
        }

    return [d1, d2, d3, d4, d5, d6]


def year3_decisions():
    def d1(s):
        c = s["flags"].get("corrupcion")
        if c == "tapada":
            return {
                "tag": "Escándalo", "title": "Lo que tapaste, salió",
                "text": ["Se publican documentos sobre el desvío de fondos que decidiste tapar hace dos años."],
                "options": [
                    {"label": "Reconocer el error y remover responsables", "effects": {"pop": -6, "est": 6}, "flags": {"escandalo": "reconocido"}},
                    {"label": "Negar todo", "effects": {"pop": -14, "est": -8}, "flags": {"escandalo": "negado"}},
                    {"label": "Culpar a un ex funcionario", "effects": {"pop": -8, "est": -2}, "flags": {"escandalo": "derivado"}},
                ],
            }
        if c == "expuesta":
            return {
                "tag": "Institucional", "title": "El juicio",
                "text": ["El caso que denunciaste hace dos años llegó a juicio y compromete a gente cercana a vos."],
                "options": [
                    {"label": "Garantizar acceso total a los documentos", "effects": {"est": 8, "pop": 5}, "flags": {"justicia": "independiente"}},
                    {"label": "Frenar la entrega de documentos", "effects": {"est": -8, "pop": -3}, "flags": {"justicia": "obstruida"}},
                ],
            }
        return {
            "tag": "Escándalo", "title": "Una nueva denuncia",
            "text": ["Un informe periodístico revela contratos públicos sin licitación."],
            "options": [
                {"label": "Pedir una auditoría externa", "effects": {"est": 6, "pop": 2}, "flags": {"escandalo": "auditado"}},
                {"label": "Minimizar el informe", "effects": {"pop": -6, "est": -2}, "flags": {"escandalo": "ignorado"}},
            ],
        }

    def d2(s):
        riesgo = s["flags"].get("ejercito") == "restaurado" or s["stats"]["est"] < 40
        return {
            "tag": "Institucional",
            "title": "Rumores de conspiración" if riesgo else "Tensión en los cuarteles",
            "text": ["Reuniones no autorizadas entre oficiales de alto rango." if riesgo else "Malestar en las fuerzas de seguridad por salarios atrasados."],
            "options": [
                {"label": "Purgar preventivamente a los sospechosos", "effects": {"est": 5, "seg": -4, "pop": -2}, "flags": {"conspiracion": "purga"}},
                {"label": "Negociar directamente con la cúpula", "effects": {"est": 3, "seg": 2, "eco": -3}, "flags": {"conspiracion": "negociada"}},
                {"label": "No hacer nada visible", "effects": {"est": -10 if riesgo else -1}, "flags": {"conspiracion": "ignorada"}},
            ],
        }

    def d3(s):
        return {
            "tag": "Relaciones internacionales", "title": "Tensión en la frontera",
            "text": ["El país vecino endurece controles migratorios; hay deportaciones masivas."],
            "options": [
                {"label": "Postura firme en defensa de los migrantes", "effects": {"pop": 8, "rel": -8}, "flags": {"frontera": "firme"}},
                {"label": "Buscar un acuerdo migratorio conciliador", "effects": {"rel": 8, "pop": -6}, "flags": {"frontera": "conciliador"}},
                {"label": "Endurecer también los controles propios", "effects": {"seg": 2, "pop": -3, "rel": -2}, "flags": {"frontera": "espejo"}},
            ],
        }

    def d4(s):
        return {
            "tag": "Economía", "title": "La zona franca",
            "text": ["Un consorcio extranjero ofrece una gran zona franca textil si se flexibilizan condiciones laborales."],
            "options": [
                {"label": "Aceptar con condiciones laborales mínimas", "effects": {"eco": 12, "pop": -6}, "flags": {"zona_franca": "flexible"}},
                {"label": "Exigir estándares laborales altos", "effects": {"eco": 3, "pop": 6}, "flags": {"zona_franca": "exigente"}},
                {"label": "Rechazar el proyecto", "effects": {"eco": -6, "rel": -4, "pop": 2}, "flags": {"zona_franca": "rechazada"}},
            ],
        }

    def d5(s):
        return {
            "tag": "Salud", "title": "Brote sanitario",
            "text": ["Se confirma un brote de cólera en varios departamentos."],
            "options": [
                {"label": "Declarar emergencia y campaña sanitaria estricta", "effects": {"pop": 3, "eco": -6, "seg": 1}, "flags": {"epidemia": "declarada"}},
                {"label": "Pedir ayuda médica internacional urgente", "effects": {"rel": 6, "pop": 4, "eco": -2}, "flags": {"epidemia": "ayuda_externa"}},
                {"label": "Minimizar el brote públicamente", "effects": {"eco": 2, "pop": -14}, "flags": {"epidemia": "oculta"}},
            ],
        }

    def d6(s):
        seg_baja = s["stats"]["seg"] < 40
        return {
            "tag": "Seguridad", "title": "Disputa por el puerto y el aeropuerto",
            "text": ["Grupos armados presionan por el control de los accesos al puerto y a una pista del aeropuerto."],
            "options": [
                {
                    "label": "Enfrentamiento total por la fuerza",
                    "effects": {"seg": -14, "est": -8, "pop": -4} if seg_baja else {"seg": 10, "pop": 6},
                    "flags": {"puerto": "fallido" if seg_baja else "recuperado"},
                },
                {"label": "Ceder el control de facto", "effects": {"seg": 4, "est": -9, "pop": -10}, "flags": {"puerto": "cedido"}},
                {"label": "Pedir intervención militar extranjera de emergencia", "effects": {"rel": 5, "seg": 7, "pop": -12}, "flags": {"puerto": "intervencion"}},
            ],
        }

    return [d1, d2, d3, d4, d5, d6]


def year4_decisions():
    def d1(s):
        return {
            "tag": "Institucional", "title": "Preparar las elecciones",
            "text": ["Se acerca el fin de tu mandato. Todo el país mira hacia la próxima elección."],
            "options": [
                {"label": "Comprometerte con elecciones libres y observadas", "effects": {"est": 10, "pop": 4}, "flags": {"elecciones_final": "libres"}},
                {"label": "Impulsar una reforma para reelegirte", "effects": {"pop": -8, "est": -14}, "flags": {"elecciones_final": "reeleccion"}},
                {"label": "Elegir un sucesor y controlar el proceso", "effects": {"est": -5, "pop": -2}, "flags": {"elecciones_final": "sucesor"}},
            ],
        }

    def d2(s):
        return {
            "tag": "Institucional", "title": "Últimas negociaciones con la oposición",
            "text": ["La oposición ofrece negociar las reglas de la transición."],
            "options": [
                {"label": "Diálogo nacional amplio, cediendo poder", "effects": {"est": 8, "pop": 4}, "flags": {"oposicion": "dialogo"}},
                {"label": "Aislar y debilitar a la oposición", "effects": {"est": -8, "pop": 2}, "flags": {"oposicion": "aislada"}},
                {"label": "Ignorarla y gobernar en soledad", "effects": {"est": -4, "pop": -2}, "flags": {"oposicion": "ignorada"}},
            ],
        }

    def d3(s):
        worst = worst_stat(s, ["eco", "seg", "rel", "est"])
        if worst == "seg":
            seg_ok = s["stats"]["seg"] >= 45
            return {
                "tag": "Crisis", "title": "Ofensiva armada en la capital",
                "text": ["Grupos armados lanzan una ofensiva coordinada sobre Puerto Príncipe."],
                "options": [
                    {"label": "Responder con todo el peso del Estado",
                     "effects": {"seg": 14, "pop": 8} if seg_ok else {"seg": -18, "est": -12, "pop": -10},
                     "flags": {"crisis_final": "seguridad_enfrentada"}},
                    {"label": "Estado de excepción + tropas extranjeras", "effects": {"seg": 8, "rel": 4, "pop": -12, "est": -3}, "flags": {"crisis_final": "intervencion_urgente"}},
                    {"label": "Negociar un alto el fuego de emergencia", "effects": {"seg": 3, "est": -12, "pop": -8}, "flags": {"crisis_final": "alto_el_fuego"}},
                ],
            }
        if worst == "eco":
            return {
                "tag": "Crisis", "title": "Colapso de la moneda",
                "text": ["La moneda nacional se desploma en cuestión de días."],
                "options": [
                    {"label": "Ajuste de shock: recorte drástico de gasto", "effects": {"eco": 12, "pop": -14}, "flags": {"crisis_final": "ajuste_shock"}},
                    {"label": "Rescate financiero de emergencia", "effects": {"eco": 10, "rel": 3, "pop": -6, "est": -2}, "flags": {"crisis_final": "rescate"}},
                    {"label": "Imprimir dinero para sostener el gasto", "effects": {"eco": -16, "pop": 4}, "flags": {"crisis_final": "emision"}},
                ],
            }
        if worst == "rel":
            return {
                "tag": "Crisis", "title": "Aislamiento internacional",
                "text": ["Varios países y organismos suspenden cooperación y créditos."],
                "options": [
                    {"label": "Misión diplomática de emergencia", "effects": {"rel": 10, "pop": -2}, "flags": {"crisis_final": "diplomacia"}},
                    {"label": "Girar hacia otros socios menos exigentes", "effects": {"rel": 5, "eco": 3, "est": -3}, "flags": {"crisis_final": "giro"}},
                    {"label": "Redoblar el discurso soberanista", "effects": {"pop": 6, "rel": -10, "eco": -6}, "flags": {"crisis_final": "soberanista"}},
                ],
            }
        pop_ok = s["stats"]["pop"] >= 50
        return {
            "tag": "Crisis", "title": "El gobierno se fractura",
            "text": ["Varios ministros renuncian el mismo día."],
            "options": [
                {"label": "Gabinete de unidad con otros sectores", "effects": {"est": 10, "pop": 3}, "flags": {"crisis_final": "unidad"}},
                {"label": "Sostener a tu círculo cercano pase lo que pase", "effects": {"est": -10, "pop": -4}, "flags": {"crisis_final": "cerrado"}},
                {"label": "Convocar una consulta popular urgente",
                 "effects": {"est": 8, "pop": 6} if pop_ok else {"est": -8, "pop": -8},
                 "flags": {"crisis_final": "consulta"}},
            ],
        }

    def d4(s):
        return {
            "tag": "Legado", "title": "El legado",
            "text": ["Faltan semanas para el final formal de tu mandato."],
            "options": [
                {"label": "Preparar una transición pacífica del poder", "effects": {"est": 10, "pop": 5}, "flags": {"legado": "transicion"}},
                {"label": "Aferrarte al poder por cualquier medio", "effects": {"pop": -15, "est": -15}, "flags": {"legado": "aferrado"}},
                {"label": "Proponer una gran reforma de último minuto",
                 "effects": {"pop": 3, "eco": -4 if s["stats"]["eco"] < 45 else 4}, "flags": {"legado": "reforma_final"}},
            ],
        }

    def d5(s):
        eco_baja = s["stats"]["eco"] < 40
        return {
            "tag": "Economía", "title": "El pedido de auxilio final",
            "text": ["A pocos días de cerrar el mandato, hay margen para una última jugada económica."],
            "options": [
                {"label": "Préstamo de emergencia con condiciones duras", "effects": {"eco": 14, "pop": -6}, "flags": {"auxilio": "prestamo"}},
                {"label": "Ayuda solo de países aliados y diáspora", "effects": {"eco": 6, "rel": 4}, "flags": {"auxilio": "aliados"}},
                {"label": "No pedir nada más", "effects": {"eco": -8 if eco_baja else 2, "pop": 4}, "flags": {"auxilio": "ninguno"}},
            ],
        }

    def d6(s):
        return {
            "tag": "Cierre", "title": "El discurso final",
            "text": ["Tu último acto público relevante antes del cierre formal del mandato."],
            "options": [
                {"label": "Discurso de unidad, con autocrítica", "effects": {"pop": 6, "est": 4}, "flags": {"discurso": "unidad"}},
                {"label": "Discurso triunfalista, sin reconocer errores", "effects": {"pop": -6, "est": -2}, "flags": {"discurso": "triunfalista"}},
                {"label": "No dar discurso", "effects": {"pop": -2}, "flags": {"discurso": "silencio"}},
            ],
        }

    return [d1, d2, d3, d4, d5, d6]


YEARS = [year1_decisions(), year2_decisions(), year3_decisions(), year4_decisions()]

YEAR_TITLES = [
    "Los primeros cien días",
    "El peso del cargo",
    "Bajo la lupa",
    "La cuenta final",
]


# ============================================================
# FINALES
# ============================================================

def compute_ending(state):
    pop, eco, seg, rel, est = (state["stats"][k] for k in ("pop", "eco", "seg", "rel", "est"))
    f = state["flags"]

    if est <= 22 or (pop <= 22 and est <= 38):
        return ("bad", "El avión a las cinco de la mañana", [
            "Los últimos días de tu mandato no se parecen en nada a lo que imaginaste al asumir.",
            "A las cinco de la mañana, un vuelo no anunciado te saca del país con una valija y sin despedida pública.",
        ])

    if seg <= 24 and rel <= 34:
        return ("bad", "El país en armas", [
            "La violencia armada desbordó al Estado, justo cuando el aislamiento internacional te dejó sin apoyos externos.",
            "Lo que empezó como una crisis de seguridad urbana termina descrito como un conflicto armado interno.",
        ])

    if eco <= 16:
        return ("bad", "Ruinas con nombre y apellido", [
            "La moneda perdió casi todo su valor. Una parte importante de la población depende de ayuda humanitaria para comer.",
            "Terminás el mandato con un país en ruinas económicas: sin reservas, sin crédito y sin margen para el que venga después.",
        ])

    if pop <= 26:
        return ("bad", "La plaza, en tu contra", [
            "Cada decisión impopular fue restando algo que nunca se recuperó del todo.",
            "Terminás renunciando antes del final formal del mandato, en una transición apurada.",
        ])

    if pop >= 58 and est >= 48 and seg >= 38 and eco >= 38 and rel >= 38:
        titulo = "Reelegido, contra el pronóstico" if f.get("elecciones_final") == "reeleccion" else "Cuatro años, y te piden más"
        return ("good", titulo, [
            "La seguridad mejoró de forma sostenida, la economía dejó de ser una fuente diaria de malas noticias.",
            "El día de la nueva asunción, la plaza frente al Palacio está, por una vez, más cerca de la celebración que de la protesta.",
        ])

    if pop >= 42 and est >= 40:
        return ("good", "El mandato que se pudo terminar", [
            "No fue un gobierno para el aplauso unánime, pero llegaste al final con las instituciones en pie.",
            "Entregás el poder en una ceremonia formal, sin sobresaltos.",
        ])

    return ("bad", "Cuatro años, ningún rumbo claro", [
        "Ni el desastre absoluto ni la gestión ejemplar: el país sigue de pie, pero más golpeado y desconfiado.",
        "El país que recibe tu sucesor tiene, en casi todos los frentes, más problemas que soluciones heredadas.",
    ])


YEAR_TITLES = [
    "Los primeros cien días",
    "El peso del cargo",
    "Bajo la lupa",
    "La cuenta final",
]

TOTAL_DECISIONS = 24  # 4 años x 6 decisiones


def decision_at(year_1based, day_1based, state):
    """Devuelve el dict de la decisión (tag/title/text/options) para ese
    año y día, evaluado contra el estado actual (permite ramificaciones)."""
    return YEARS[year_1based - 1][day_1based - 1](state)


def replay(choices):
    """Reconstruye el estado completo del juego a partir de la lista de
    índices de opción elegidos hasta ahora (lo único que se guarda en la
    sesión). Devuelve un dict con:
      - state: {"stats": {...}, "flags": {...}}
      - log: lista de decisiones ya tomadas, con su texto y la elección hecha
      - year, day: el año/día que corresponde jugar a continuación
      - done: True si ya se jugaron las 24 decisiones
    """
    state = fresh_state()
    log = []
    idx = 0
    for year in range(1, 5):
        for day in range(1, 7):
            if idx >= len(choices):
                return {"state": state, "log": log, "year": year, "day": day, "done": False}
            decision = decision_at(year, day, state)
            chosen = choices[idx]
            if not isinstance(chosen, int) or chosen < 0 or chosen >= len(decision["options"]):
                chosen = 0  # entrada corrupta / manipulada: fallback seguro
            opt = decision["options"][chosen]
            apply_effects(state, opt["effects"])
            set_flags(state, opt.get("flags"))
            log.append({
                "year": year,
                "day": day,
                "tag": decision["tag"],
                "title": decision["title"],
                "choice": opt["label"],
            })
            idx += 1
    return {"state": state, "log": log, "year": 4, "day": 6, "done": True}
