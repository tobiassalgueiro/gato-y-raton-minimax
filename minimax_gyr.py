"""
🐱 GATO VS RATÓN 🐭
Versión simplificada con Minimax
"""

import random
import copy
import time

class Tablero:
    def __init__(self, tamaño=8):
        self.tamaño = tamaño
        self.gato = [0, 0]
        self.raton = [tamaño-1, tamaño-1]
        self.queso = [tamaño//4, tamaño//4]
        self.tiene_queso = False
        self.turno = 0
        self.max_turnos = 30
        self.paredes = self._generar_paredes()
        self.historial = []
        
    def _generar_paredes(self):
        paredes = []
        for _ in range(50):
            if len(paredes) >= 3:
                break
            pos = [random.randint(0, self.tamaño-1), random.randint(0, self.tamaño-1)]
            if pos not in [self.gato, self.raton, self.queso] + paredes:
                paredes.append(pos)
        return paredes
    
    def mostrar(self):
        print(f"\n{'='*50}\nTurno: {self.turno}/{self.max_turnos}\n{'='*50}")
        for f in range(self.tamaño):
            linea = ""
            for c in range(self.tamaño):
                pos = [f, c]
                if pos == self.raton and pos == self.queso:
                    linea += "🐭🧀"
                elif pos == self.gato:
                    linea += "🐱 "
                elif pos == self.raton:
                    linea += "🐭 "
                elif pos == self.queso and not self.tiene_queso:
                    linea += "🧀 "
                elif pos in self.paredes:
                    linea += "🧱 "
                else:
                    linea += "·  "
            print(linea)
    
    def movimientos_validos(self, pos, es_gato):
        dirs = [[-1,0], [1,0], [0,-1], [0,1]]
        if not es_gato:  # Ratón tiene diagonales
            dirs += [[-1,-1], [-1,1], [1,-1], [1,1]]
        
        movs = []
        for d in dirs:
            nueva = [pos[0] + d[0], pos[1] + d[1]]
            if (0 <= nueva[0] < self.tamaño and 
                0 <= nueva[1] < self.tamaño and
                nueva not in self.paredes):
                if not (es_gato and nueva == self.queso and not self.tiene_queso):
                    movs.append(nueva)
        return movs
    
    def distancia(self, p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    
    def terminado(self):
        return self.gato == self.raton or self.tiene_queso or self.turno >= self.max_turnos
    
    def verificar_queso(self):
        if self.raton == self.queso and not self.tiene_queso:
            self.tiene_queso = True
            return True
        return False


class Juego:
    def __init__(self, tamaño=8, prof=4):
        self.tablero = Tablero(tamaño)
        self.prof = prof
    
    def evaluar(self, t):
        if t.gato == t.raton:
            return -1000
        if t.tiene_queso:
            return 1000
        
        d_gato_raton = t.distancia(t.gato, t.raton)
        d_raton_queso = t.distancia(t.raton, t.queso)
        
        eval = 0
        eval += d_gato_raton * (20 if d_gato_raton <= 3 else 5)
        peso_queso = 25 if d_gato_raton > 4 else (15 if d_gato_raton > 2 else 10)
        eval -= d_raton_queso * peso_queso
        eval -= t.historial.count(t.raton) * 30
        
        return eval
    
    def minimax(self, t, prof, es_max):
        if prof == 0 or t.terminado():
            return self.evaluar(t), None
        
        if es_max:  # Ratón
            mejor_eval = float('-inf')
            mejor_mov = None
            for mov in t.movimientos_validos(t.raton, False):
                copia = copy.deepcopy(t)
                copia.raton = mov
                copia.historial = t.historial[-3:] + [mov]
                copia.verificar_queso()
                eval, _ = self.minimax(copia, prof-1, False)
                if eval > mejor_eval:
                    mejor_eval, mejor_mov = eval, mov
            return mejor_eval, mejor_mov
        else:  # Gato
            mejor_eval = float('inf')
            mejor_mov = None
            for mov in t.movimientos_validos(t.gato, True):
                copia = copy.deepcopy(t)
                copia.gato = mov
                copia.turno += 1
                eval, _ = self.minimax(copia, prof-1, True)
                if eval < mejor_eval:
                    mejor_eval, mejor_mov = eval, mov
            return mejor_eval, mejor_mov
    
    def mover_ia(self, es_raton):
        _, mov = self.minimax(self.tablero, self.prof, es_raton)
        if mov:
            if es_raton:
                self.tablero.historial.append(self.tablero.raton[:])
                if len(self.tablero.historial) > 4:
                    self.tablero.historial.pop(0)
                self.tablero.raton = mov
                print("🐭 Ratón se mueve")
            else:
                self.tablero.gato = mov
                print("🐱 Gato persigue")
    
    def mover_jugador(self, es_raton):
        print(f"\n🎮 TU TURNO ({'Ratón 🐭' if es_raton else 'Gato 🐱'})")
        pos_actual = self.tablero.raton if es_raton else self.tablero.gato
        movs = self.tablero.movimientos_validos(pos_actual, not es_raton)
        
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
                    self.tablero.raton = movs[idx]
                else:
                    self.tablero.gato = movs[idx]
                print(f"✅ Moviste a {movs[idx]}")
        except:
            print("❌ Entrada inválida")
    
    def jugar_ia_vs_ia(self, vel=1):
        print("\n🎮 IA VS IA")
        while not self.tablero.terminado():
            self.tablero.mostrar()
            self.mover_ia(True)
            if self.tablero.verificar_queso():
                print("🎉 ¡Ratón encontró el queso!")
                break
            if self.tablero.terminado():
                break
            self.mover_ia(False)
            self.tablero.turno += 1
            time.sleep(vel) if vel > 0 else input("Enter...")
        
        self.tablero.mostrar()
        if self.tablero.gato == self.tablero.raton:
            print("🏆 GATO GANÓ")
        elif self.tablero.tiene_queso:
            print("🏆 RATÓN GANÓ (queso)")
        else:
            print("🏆 RATÓN GANÓ (tiempo)")
    
    def jugar_vs_ia(self, jugador_es_raton):
        print(f"\n🎮 TÚ ({'RATÓN 🐭' if jugador_es_raton else 'GATO 🐱'}) vs IA")
        while not self.tablero.terminado():
            self.tablero.mostrar()
            
            if jugador_es_raton:
                self.mover_jugador(True)
                if self.tablero.verificar_queso():
                    print("🎉 ¡GANASTE!")
                    break
                if self.tablero.terminado():
                    break
                self.mover_ia(False)
            else:
                self.mover_ia(True)
                if self.tablero.verificar_queso():
                    print("💔 PERDISTE")
                    break
                if self.tablero.terminado():
                    break
                self.mover_jugador(False)
            
            self.tablero.turno += 1
        
        self.tablero.mostrar()
        if self.tablero.gato == self.tablero.raton:
            print("🏆 GANASTE" if not jugador_es_raton else "💔 PERDISTE")
        elif self.tablero.tiene_queso:
            print("🏆 GANASTE" if jugador_es_raton else "💔 PERDISTE")


def menu():
    print("\n" + "="*50)
    print("🐱  GATO VS RATÓN  🐭")
    print("="*50)
    print("1. IA vs IA")
    print("2. Jugador (Ratón) vs IA")
    print("3. Jugador (Gato) vs IA")
    print("4. Salir")
    
    op = input("\nOpción (1-4): ")
    
    if op == "1":
        vel = float(input("Velocidad (0=manual, 0.5=rápido, 1=normal): ") or "1")
        Juego().jugar_ia_vs_ia(vel)
    elif op == "2":
        dif = int(input("Dificultad (2=fácil, 4=normal, 5=difícil): ") or "4")
        Juego(prof=dif).jugar_vs_ia(True)
    elif op == "3":
        dif = int(input("Dificultad (2=fácil, 4=normal, 5=difícil): ") or "4")
        Juego(prof=dif).jugar_vs_ia(False)
    elif op == "4":
        print("¡Adiós! 👋")
        return
    
    if input("\n¿Otra partida? (s/n): ").lower() == 's':
        menu()


if __name__ == "__main__":
    menu()