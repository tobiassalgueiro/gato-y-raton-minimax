🐱 GATO VS RATÓN 🐭


import random
import copy
import time


# ─── ESTADO DEL JUEGO ──────────────────────────────────────────────────────────

def crear_tablero(tamaño=8):
    gato  = [0, 0]
    raton = [tamaño - 1, tamaño - 1]
    queso = [tamaño // 4, tamaño // 4]
    paredes = generar_paredes(tamaño, gato, raton, queso)
    return {
        "tamaño":     tamaño,
        "gato":       gato,
        "raton":      raton,
        "queso":      queso,
        "tiene_queso": False,
        "turno":      0,
        "max_turnos": 30,
        "paredes":    paredes,
        "historial":  [],
    }


def generar_paredes(tamaño, gato, raton, queso):
    paredes = []
    for _ in range(50):
        if len(paredes) >= 3:
            break
        pos = [random.randint(0, tamaño - 1), random.randint(0, tamaño - 1)]
        if pos not in [gato, raton, queso] + paredes:
            paredes.append(pos)
    return paredes


# ─── VISUALIZACIÓN ─────────────────────────────────────────────────────────────

def mostrar(t):
    print(f"\n{'='*50}\nTurno: {t['turno']}/{t['max_turnos']}\n{'='*50}")
    for f in range(t["tamaño"]):
        linea = ""
        for c in range(t["tamaño"]):
            pos = [f, c]
            if pos == t["raton"] and pos == t["queso"]:
                linea += "🐭🧀"
            elif pos == t["gato"]:
                linea += "🐱 "
            elif pos == t["raton"]:
                linea += "🐭 "
            elif pos == t["queso"] and not t["tiene_queso"]:
                linea += "🧀 "
            elif pos in t["paredes"]:
                linea += "🧱 "
            else:
                linea += "·  "
        print(linea)


# ─── LÓGICA DEL TABLERO ────────────────────────────────────────────────────────

def movimientos_validos(t, pos, es_gato):
    dirs = [[-1, 0], [1, 0], [0, -1], [0, 1]]
    if not es_gato:
        dirs += [[-1, -1], [-1, 1], [1, -1], [1, 1]]

    movs = []
    for d in dirs:
        nueva = [pos[0] + d[0], pos[1] + d[1]]
        if (0 <= nueva[0] < t["tamaño"] and
                0 <= nueva[1] < t["tamaño"] and
                nueva not in t["paredes"]):
            if not (es_gato and nueva == t["queso"] and not t["tiene_queso"]):
                movs.append(nueva)
    return movs


def distancia(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def terminado(t):
    return t["gato"] == t["raton"] or t["tiene_queso"] or t["turno"] >= t["max_turnos"]


def verificar_queso(t):
    if t["raton"] == t["queso"] and not t["tiene_queso"]:
        t["tiene_queso"] = True
        return True
    return False


# ─── IA / MINIMAX ──────────────────────────────────────────────────────────────

def evaluar(t):
    if t["gato"] == t["raton"]:
        return -1000
    if t["tiene_queso"]:
        return 1000

    d_gato_raton = distancia(t["gato"], t["raton"])
    d_raton_queso = distancia(t["raton"], t["queso"])

    ev = 0
    ev += d_gato_raton * (20 if d_gato_raton <= 3 else 5)
    peso_queso = 25 if d_gato_raton > 4 else (15 if d_gato_raton > 2 else 10)
    ev -= d_raton_queso * peso_queso
    ev -= t["historial"].count(t["raton"]) * 30
    return ev


def minimax(t, prof, es_max):
    if prof == 0 or terminado(t):
        return evaluar(t), None

    if es_max:  # Ratón
        mejor_eval = float('-inf')
        mejor_mov  = None
        for mov in movimientos_validos(t, t["raton"], False):
            copia = copy.deepcopy(t)
            copia["raton"]    = mov
            copia["historial"] = t["historial"][-3:] + [mov]
            verificar_queso(copia)
            ev, _ = minimax(copia, prof - 1, False)
            if ev > mejor_eval:
                mejor_eval, mejor_mov = ev, mov
        return mejor_eval, mejor_mov
    else:  # Gato
        mejor_eval = float('inf')
        mejor_mov  = None
        for mov in movimientos_validos(t, t["gato"], True):
            copia = copy.deepcopy(t)
            copia["gato"]  = mov
            copia["turno"] += 1
            ev, _ = minimax(copia, prof - 1, True)
            if ev < mejor_eval:
                mejor_eval, mejor_mov = ev, mov
        return mejor_eval, mejor_mov


def mover_ia(t, prof, es_raton):
    _, mov = minimax(t, prof, es_raton)
    if mov:
        if es_raton:
            t["historial"].append(t["raton"][:])
            if len(t["historial"]) > 4:
                t["historial"].pop(0)
            t["raton"] = mov
            print("🐭 Ratón se mueve")
        else:
            t["gato"] = mov
            print("🐱 Gato persigue")


# ─── ENTRADA DEL JUGADOR ───────────────────────────────────────────────────────

def mover_jugador(t, es_raton):
    print(f"\n🎮 TU TURNO ({'Ratón 🐭' if es_raton else 'Gato 🐱'})")
    pos_actual = t["raton"] if es_raton else t["gato"]
    movs = movimientos_validos(t, pos_actual, not es_raton)

    if not movs:
        print("❌ Sin movimientos")
        return

    print(f"📍 Posición: {pos_actual}")
    for i, m in enumerate(movs, 1):
        print(f"  {i}. {m}")

    try:
        idx = int(input(f"Elige (1-{len(movs)}): ")) - 1
        if 0 <= idx < len(movs):
            if es_raton:
                t["raton"] = movs[idx]
            else:
                t["gato"] = movs[idx]
            print(f"✅ Moviste a {movs[idx]}")
    except Exception:
        print("❌ Entrada inválida")


# ─── MODOS DE JUEGO ────────────────────────────────────────────────────────────

def mostrar_resultado(t):
    if t["gato"] == t["raton"]:
        print("🏆 GATO GANÓ")
    elif t["tiene_queso"]:
        print("🏆 RATÓN GANÓ (queso)")
    else:
        print("🏆 RATÓN GANÓ (tiempo)")


def jugar_ia_vs_ia(prof=4, vel=1):
    t = crear_tablero()
    print("\n🎮 IA VS IA")
    while not terminado(t):
        mostrar(t)
        mover_ia(t, prof, True)
        if verificar_queso(t):
            print("🎉 ¡Ratón encontró el queso!")
            break
        if terminado(t):
            break
        mover_ia(t, prof, False)
        t["turno"] += 1
        time.sleep(vel) if vel > 0 else input("Enter...")

    mostrar(t)
    mostrar_resultado(t)


def jugar_vs_ia(jugador_es_raton, prof=4):
    t = crear_tablero()
    print(f"\n🎮 TÚ ({'RATÓN 🐭' if jugador_es_raton else 'GATO 🐱'}) vs IA")
    while not terminado(t):
        mostrar(t)

        if jugador_es_raton:
            mover_jugador(t, True)
            if verificar_queso(t):
                print("🎉 ¡GANASTE!")
                break
            if terminado(t):
                break
            mover_ia(t, prof, False)
        else:
            mover_ia(t, prof, True)
            if verificar_queso(t):
                print("💔 PERDISTE")
                break
            if terminado(t):
                break
            mover_jugador(t, False)

        t["turno"] += 1

    mostrar(t)
    if t["gato"] == t["raton"]:
        print("🏆 GANASTE" if not jugador_es_raton else "💔 PERDISTE")
    elif t["tiene_queso"]:
        print("🏆 GANASTE" if jugador_es_raton else "💔 PERDISTE")


# ─── MENÚ ──────────────────────────────────────────────────────────────────────

def menu():
    print("\n" + "=" * 50)
    print("🐱  GATO VS RATÓN  🐭")
    print("=" * 50)
    print("1. IA vs IA")
    print("2. Jugador (Ratón) vs IA")
    print("3. Jugador (Gato) vs IA")
    print("4. Salir")

    op = input("\nOpción (1-4): ")

    if op == "1":
        vel = float(input("Velocidad (0=manual, 0.5=rápido, 1=normal): ") or "1")
        jugar_ia_vs_ia(vel=vel)
    elif op == "2":
        dif = int(input("Dificultad (2=fácil, 4=normal, 5=difícil): ") or "4")
        jugar_vs_ia(True, prof=dif)
    elif op == "3":
        dif = int(input("Dificultad (2=fácil, 4=normal, 5=difícil): ") or "4")
        jugar_vs_ia(False, prof=dif)
    elif op == "4":
        print("¡Adiós! 👋")
        return

    if input("\n¿Otra partida? (s/n): ").lower() == 's':
        menu()


if __name__ == "__main__":
    menu()
        menu()


if __name__ == "__main__":
    menu()
