import random
import copy
import time


def crear_tablero(tamaño=8):
    return {
        "tamaño":      tamaño,
        "gato":        [0, 0],
        "raton":       [tamaño - 1, tamaño - 1],
        "queso":       [tamaño // 4, tamaño // 4],
        "tiene_queso": False,
        "turno":       0,
        "max_turnos":  30,
        "paredes":     generar_paredes(tamaño),
        "historial_r": [],
        "historial_g": [],
    }

def generar_paredes(tamaño):
    ocupadas = [[0,0], [tamaño-1, tamaño-1], [tamaño//4, tamaño//4]]
    paredes = []
    while len(paredes) < 3:
        pos = [random.randint(0, tamaño-1), random.randint(0, tamaño-1)]
        if pos not in ocupadas + paredes:
            paredes.append(pos)
    return paredes

# visualización

def mostrar(t):
    print(f"\nTurno {t['turno']}/{t['max_turnos']}")
    for f in range(t["tamaño"]):
        linea = ""
        for c in range(t["tamaño"]):
            pos = [f, c]
            if   pos == t["gato"]:                           linea += "🐱 "
            elif pos == t["raton"] and pos == t["queso"]:    linea += "🐭🧀"
            elif pos == t["raton"]:                          linea += "🐭 "
            elif pos == t["queso"] and not t["tiene_queso"]: linea += "🧀 "
            elif pos in t["paredes"]:                        linea += "🧱 "
            else:                                            linea += "·  "
        print(linea)

# logica del juego

def movimientos_validos(t, pos, es_gato):
    dirs = [[-1,0],[1,0],[0,-1],[0,1]]
    if not es_gato:
        dirs += [[-1,-1],[-1,1],[1,-1],[1,1]]
    return [
        [pos[0]+d[0], pos[1]+d[1]]
        for d in dirs
        if (0 <= pos[0]+d[0] < t["tamaño"] and
            0 <= pos[1]+d[1] < t["tamaño"] and
            [pos[0]+d[0], pos[1]+d[1]] not in t["paredes"] and
            not (es_gato and [pos[0]+d[0], pos[1]+d[1]] == t["queso"]))
    ]

def distancia(p1, p2):
    return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])

def terminado(t):
    return t["gato"] == t["raton"] or t["tiene_queso"] or t["turno"] >= t["max_turnos"]

def verificar_queso(t):
    if t["raton"] == t["queso"] and not t["tiene_queso"]:
        t["tiene_queso"] = True

# ia, evaluacion minimax

def evaluar(t):
    if t["gato"] == t["raton"]: return -1000
    if t["tiene_queso"]:        return  1000
    d_gr = distancia(t["gato"], t["raton"])
    d_rq = distancia(t["raton"], t["queso"])
    return d_gr * 15 - d_rq * 10

def minimax(t, prof, es_max, visitados_g=None, visitados_r=None):
    """
    visitados_g / visitados_r: tuplas con posiciones
    ya recorridas en esta rama del árbol
    si un movimiento lleva a una posición ya visitada en la misma rama
    se le aplica una penalización para que el algoritmo lo evite
    """
    if visitados_g is None: visitados_g = set()
    if visitados_r is None: visitados_r = set()

    if prof == 0 or terminado(t):
        ev = evaluar(t)
        # penalizacion por repetir posiciones
        if tuple(t["gato"])  in visitados_g: ev += 40   # malo para ratón si gato repite
        if tuple(t["raton"]) in visitados_r: ev -= 40
        return ev, None

    if es_max:   # raotn maximiza
        mejor = (float('-inf'), None)
        for mov in movimientos_validos(t, t["raton"], False):
            copia = copy.deepcopy(t)
            copia["raton"] = mov
            verificar_queso(copia)
            pen = -40 if tuple(mov) in visitados_r else 0
            ev, _ = minimax(copia, prof-1, False,
                            visitados_g,
                            visitados_r | {tuple(t["raton"])})
            ev += pen
            if ev > mejor[0]:
                mejor = (ev, mov)

    else:        # gato minimiza
        mejor = (float('inf'), None)
        for mov in movimientos_validos(t, t["gato"], True):
            copia = copy.deepcopy(t)
            copia["gato"]  = mov
            copia["turno"] += 1
            pen = 40 if tuple(mov) in visitados_g else 0
            ev, _ = minimax(copia, prof-1, True,
                            visitados_g | {tuple(t["gato"])},
                            visitados_r)
            ev += pen
            if ev < mejor[0]:
                mejor = (ev, mov)

    return mejor

# movimientos

def mover_ia(t, prof, es_raton):
    # historias de mov para evitar ciclos etc
    vis_g = {tuple(p) for p in t["historial_g"]}
    vis_r = {tuple(p) for p in t["historial_r"]}
    _, mov = minimax(t, prof, es_raton, vis_g, vis_r)
    if not mov:
        return
    if es_raton:
        t["historial_r"] = (t["historial_r"] + [t["raton"][:]])[-6:] # guardamos solo las últimas 6 posiciones para evitar ciclos infi
        t["raton"] = mov
        print("🐭 Ratón se mueve")
    else:
        t["historial_g"] = (t["historial_g"] + [t["gato"][:]])[-6:]
        t["gato"] = mov
        print("🐱 Gato persigue")

def direccion(origen, destino):
    df = destino[0] - origen[0]
    dc = destino[1] - origen[1]
    tabla = {
        (-1,  0): "↑",
        ( 1,  0): "↓",
        ( 0, -1): "←",
        ( 0,  1): "→",
        (-1, -1): "↖",
        (-1,  1): "↗",
        ( 1, -1): "↙",
        ( 1,  1): "↘",
    }
    return tabla.get((df, dc), str(destino))

def mover_jugador(t, es_raton):
    pos  = t["raton"] if es_raton else t["gato"]
    movs = movimientos_validos(t, pos, not es_raton)
    if not movs:
        print("❌ Sin movimientos"); return

    print(f"\n🎮 TU TURNO — posición actual: {pos}")
    for i, m in enumerate(movs, 1):
        print(f"  {i}. {direccion(pos, m)}")
    try:
        idx = int(input(f"Elige (1-{len(movs)}): ")) - 1
        if 0 <= idx < len(movs):
            if es_raton: t["raton"] = movs[idx]
            else:        t["gato"]  = movs[idx]
    except Exception:
        print("❌ Entrada inválida")

# bucle principal

def turno(t, prof, jugador_es_raton=None):
    if jugador_es_raton is True: mover_jugador(t, True)
    else:                        mover_ia(t, prof, True)

    verificar_queso(t)
    if terminado(t): return

    if jugador_es_raton is False: mover_jugador(t, False)
    else:                         mover_ia(t, prof, False)

    t["turno"] += 1

def resultado(t):
    if   t["gato"] == t["raton"]: print("🏆 GATO GANÓ — el ratón fue atrapado")
    elif t["tiene_queso"]:        print("🏆 RATÓN GANÓ — llegó al queso")
    else:                         print("🏆 RATÓN GANÓ — sobrevivió el tiempo límite")

def jugar(prof=4, jugador_es_raton=None):
    t = crear_tablero()
    while not terminado(t):
        mostrar(t)
        turno(t, prof, jugador_es_raton)
        time.sleep(1)
    mostrar(t)
    resultado(t)

# menu

def menu():
    print("\n🐱  GATO VS RATÓN  🐭")
    print("1. IA vs IA")
    print("2. Tú (Ratón) vs IA")
    print("3. Tú (Gato) vs IA")
    print("4. Salir")

    op = input("\nOpción: ").strip() 

    if op == "1":
        jugar()
    elif op == "2":
        jugar(jugador_es_raton=True)
    elif op == "3":
        jugar(jugador_es_raton=False)
    elif op == "4":
        print("¡Adiós! 👋"); return

    if input("\n¿Otra partida? (s/n): ").lower() == "s":
        menu()

if __name__ == "__main__":
    menu()
