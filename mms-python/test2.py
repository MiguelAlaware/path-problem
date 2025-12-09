import API
import sys
import numpy as np
from collections import deque

# GLOBAL CONFIGURATION 
maze_size = 16
# Matrix representantion of the map 
walls = np.zeros((maze_size, maze_size), dtype=int)
# Matriz (Flood Fill)
flood = np.full((maze_size, maze_size), -1, dtype=int)

def log(string):
    sys.stderr.write("{}\n".format(string))
    sys.stderr.flush()

def set_wall(x:int, y:int, direction:int):
    """
    Marca a parede na célula atual e a parede simétrica na célula vizinha.
    direction: 0=N, 1=E, 2=S, 3=W
    """
    # 1. Bitwise operation for marking the cells 
    walls[y, x] |= (1 << direction)
    
    # 2. Calcula o vizinho
    nx, ny = x, y
    if direction == 0: ny += 1
    if direction == 1: nx += 1
    if direction == 2: ny -= 1
    if direction == 3: nx -= 1

    # 3. Marca na célula vizinha (se válida)
    if 0 <= nx < maze_size and 0 <= ny < maze_size:
        # A direção oposta é (direction + 2) % 4
        opposite_dir = (direction + 2) % 4
        walls[ny, nx] |= (1 << opposite_dir)

def flood_update():
    """
    Recalcula todas as distâncias do labirinto baseadas nas paredes conhecidas.
    """
    flood.fill(-1)
    queue = deque()

    # Define o alvo (Centro do labirinto 16x16 são as células 7,7; 7,8; 8,7; 8,8)
    for r in range(7, 9):
        for c in range(7, 9):
            flood[r, c] = 0
            queue.append((r, c))

    # Mapeamento: (Bit da parede, dy, dx) para N, E, S, W
    path = [(1, 1, 0), (2, 0, 1), (4, -1, 0), (8, 0, -1)]
    
    while queue:
        r, c = queue.popleft()
        dist = flood[r, c]

        for bit, dr, dc in path:
            nr, nc = r + dr, c + dc

            if 0 <= nr < maze_size and 0 <= nc < maze_size:
                # Se NÃO tem parede bloqueando E a célula não foi visitada
                if (walls[r, c] & bit) == 0:
                    if flood[nr, nc] == -1:
                        flood[nr, nc] = dist + 1
                        queue.append((nr, nc))

def main():
    log("Running...")
    API.setColor(0, 0, "G")
    API.setText(0, 0, "Start")
    
    x = 0
    y = 0
    orient = 0 # 0:N, 1:E, 2:S, 3:W

    # Primeiro cálculo do mapa (assumindo labirinto vazio)
    flood_update()

    while True:
        # --- 1. LER SENSORES E ATUALIZAR PAREDES ---
        new_wall = False 
        
        # Parede na Frente
        if API.wallFront():
            real_dir = orient
            # Só atualiza se a parede ainda não foi marcada
            if (walls[y, x] & (1 << real_dir)) == 0:
                set_wall(x, y, real_dir)
                new_wall = True 
                API.setWall(x, y, "nesw"[real_dir])
        
        # Parede à Direita
        if API.wallRight():
            real_dir = (orient + 1) % 4
            if (walls[y, x] & (1 << real_dir)) == 0:
                set_wall(x, y, real_dir)
                new_wall = True
                API.setWall(x, y, "nesw"[real_dir])
        
        # Parede à Esquerda
        if API.wallLeft():
            real_dir = (orient - 1) % 4
            if (walls[y, x] & (1 << real_dir)) == 0:
                set_wall(x, y, real_dir)
                new_wall = True
                API.setWall(x, y, "nesw"[real_dir])

        # --- 2. RECALCULAR CAMINHO SE NECESSÁRIO ---
        if new_wall:
            flood_update()

        # Debug: Mostrar a distância na célula
        API.setText(x, y, str(flood[y, x]))

        # Verifica se chegou no objetivo
        if flood[y, x] == 0:
            log("CHEGUEI NO CENTRO!")
            API.setColor(x, y, "B") # Pinta de Azul
            # Se quiser continuar explorando, não dê break aqui.
            # Se quiser parar:
            break

        # --- 3. DECIDIR PARA ONDE IR ---
        best_dir = -1
        lowest_value = 9999
        
        # Verifica os 4 vizinhos (N, E, S, W)
        for d in range(4):
            # Se tem parede nessa direção, ignora
            if (walls[y, x] & (1 << d)) != 0:
                continue

            # Calcula coordenadas do vizinho
            nx, ny = x, y
            if d == 0: ny += 1
            if d == 1: nx += 1
            if d == 2: ny -= 1
            if d == 3: nx -= 1

            # Verifica limites e valor do Flood Fill
            if 0 <= nx < maze_size and 0 <= ny < maze_size:
                val = flood[ny, nx]
                # Queremos ir para um valor MENOR que o atual
                if val != -1 and val < lowest_value:
                    lowest_value = val
                    best_dir = d

        # --- 4. EXECUTAR MOVIMENTO ---
        if best_dir != -1:
            diff = best_dir - orient

            # Lógica de rotação mínima
            if diff == 1 or diff == -3:
                API.turnRight()
            elif diff == -1 or diff == 3:
                API.turnLeft()
            elif diff == 2 or diff == -2:
                API.turnRight()
                API.turnRight()
            
            API.moveForward()

            # Atualiza posição virtual e orientação
            orient = best_dir
            if orient == 0: y += 1
            if orient == 1: x += 1
            if orient == 2: y -= 1
            if orient == 3: x -= 1
        else:
            # Se não encontrou caminho (best_dir = -1)
            # Isso só acontece se estiver preso em um lugar sem saída (impossível no Flood Fill correto)
            # ou se já estiver no centro (tratado acima).
            log("Preso! Algo deu errado.")
            break

if __name__ == "__main__":                        
     main()
