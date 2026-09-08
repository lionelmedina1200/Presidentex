#!/usr/bin/env python3
"""
PRESIDENTEX — cuatro años al mando de Haití (versión de consola)
Usa el mismo motor (game_engine.py) que la app web, así que el contenido y
las reglas de los finales son exactamente las mismas en los dos lugares.
"""

import textwrap

import game_engine as ge


def wrap(text, width=78):
    return "\n".join(textwrap.wrap(text, width=width))


def print_stats(stats):
    print("\n" + "-" * 78)
    parts = [f"{m.label}: {stats[m.key]:>3}" for m in ge.STATS_META]
    print(" | ".join(parts))
    print("-" * 78)


def ask_choice(n_options):
    while True:
        raw = input(f"Elegí una opción (1-{n_options}): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= n_options:
            return int(raw) - 1
        print("Opción inválida, probá de nuevo.")


def play():
    print("=" * 78)
    print("PRESIDENTEX — cuatro años al mando de Haití")
    print("=" * 78)
    print(wrap(
        "Asumís la presidencia de Haití, un país en crisis permanente. Vas a "
        "tomar 24 decisiones desde el Palacio Nacional en Puerto Príncipe, seis "
        "por cada año de mandato. Cada una mueve tus cinco indicadores, y varias "
        "reaparecen, transformadas, en los años siguientes."
    ))
    nombre = input("\nNombre: ").strip()
    apellido = input("Apellido: ").strip()
    nombre_completo = f"{nombre} {apellido}".strip() or "Presidente/a"
    print(f"\nBienvenido/a, presidente/a {nombre_completo}.")
    input("(Enter para asumir el mandato) ")

    choices = []
    current_year_shown = 0

    while True:
        result = ge.replay(choices)
        if result["done"]:
            break

        if result["year"] != current_year_shown:
            current_year_shown = result["year"]
            print("\n" + "=" * 78)
            print(f"AÑO {result['year']} DE 4 — {ge.YEAR_TITLES[result['year'] - 1]}")
            print("=" * 78)

        decision = ge.decision_at(result["year"], result["day"], result["state"])
        print_stats(result["state"]["stats"])
        print(f"\n[{decision['tag']}] {decision['title']}")
        print(wrap(" ".join(decision["text"])))
        print()
        for i, opt in enumerate(decision["options"], start=1):
            print(f"  {i}. {opt['label']}")
        choices.append(ask_choice(len(decision["options"])))

    final_result = ge.replay(choices)
    ending_type, title, body = ge.compute_ending(final_result["state"])

    print("\n" + "=" * 78)
    print("FIN DEL MANDATO" if ending_type == "good" else "FIN ABRUPTO DEL MANDATO")
    print("=" * 78)
    print(f"\n{nombre_completo}: {title}\n")
    for p in body:
        print(wrap(p))
        print()
    print_stats(final_result["state"]["stats"])

    if input("\n¿Ver las 24 decisiones que tomaste? (s/n): ").strip().lower() == "s":
        for l in final_result["log"]:
            print(f"  Año {l['year']}, decisión {l['day']} — {l['title']}: {l['choice']}")

    print("\nGracias por jugar. Ejecutá el script de nuevo para un nuevo mandato.")


if __name__ == "__main__":
    try:
        play()
    except (KeyboardInterrupt, EOFError):
        print("\n\nMandato interrumpido.")
