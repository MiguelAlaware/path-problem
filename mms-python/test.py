import API
import sys
import numpy as np
from collections import deque

def log(string):
    sys.stderr.write("{}\n".format(string))
    sys.stderr.flush()

maze_size = 16
# Cria as matrizes globais
walls = np.zeros((maze_size, maze_size), dtype=int)
flood = np.full((maze_size, maze_size), -1, dtype=int)

def flood_update():
    # 1. Limpa o flood antigo
    flood.fill(-1)
    queue = deque()

    # 2. Define o alvo (centro)
    for r in range(7, 9):
        for c in range(7, 9):
            flood[r, c] = 0
            queue.append((r, c))

    # Norte, Leste, Sul, Oeste
    path = [(1, 1, 0), (2, 0, 1), (4, -1, 0), (8, 0, -1)]
    
    # 3. Processa a fila
    while queue:
        r, c = queue.popleft()
        dist = flood[r, c]

        for bit, dr, dc in path:
            nr, nc = r + dr, c + dc

            if 0 <= nr < maze_size and 0 <= nc < maze_size:
                # Se NÃO tem parede E ainda NÃO foi visitado
                if (walls[r, c] & bit) == 0:
                    if flood[nr, nc] == -1:
                        flood[nr, nc] = dist + 1
                        queue.append((nr, nc))


def set_wall(x, y, direction):
    """
    Marca a parede na célula (x,y) na direção dada
    E também marca a parede oposta na célula vizinha.
    """
    # Direções: 0=N, 1=E, 2=S, 3=W
    # Bits: 1, 2, 4, 8
    
    # 1. Marca na célula atual
    walls[y, x] |= (1 << direction)
    
    # 2. Calcula o vizinho
    nx, ny = x, y
    if direction == 0: ny += 1
    if direction == 1: nx += 1
    if direction == 2: ny -= 1
    if direction == 3: nx -= 1

    # 3. Marca na célula vizinha (se ela existir)
    if 0 <= nx < maze_size and 0 <= ny < maze_size:
        # A direção oposta é (direction + 2) % 4
        # Ex: Se direction é 0 (Norte), oposta é 2 (Sul)
        opposite_dir = (direction + 2) % 4
        walls[ny, nx] |= (1 << opposite_dir)








def main():
    log("Iniciando...")
    API.setColor(0, 0, "G")
    API.setText(0, 0, "S")
    
    x = 0
    y = 0
    orient = 0 # 0:N, 1:E, 2:S, 3:W

    # Roda o flood inicial para saber os primeiros valores
    flood_update()

    while True:
        # --- 1. LER PAREDES ---
        new_wall = False 
        
        # Frente
        if API.wallFront():
            real_dir = orient
            if (walls[y, x] & (1 << real_dir)) == 0:
                set_wall(x, y, real_dir) 
                new_wall = True 
                API.setWall(x, y, "nesw"[real_dir])
        
        # Direita
        if API.wallRight():
            real_dir = (orient + 1) % 4
            set_wall(x, y, real_dir)
            if (walls[y, x] & (1 << real_dir)) == 0:
                set_wall(x, y, real_dir)
                new_wall = True
                API.setWall(x, y, "nesw"[real_dir])
        
        # Esquerda
        if API.wallLeft():
            real_dir = (orient - 1) % 4
            bit = (1 << real_dir)
            if (walls[y, x] & (1 << real_dir)) == 0:
                set_wall(x, y, real_dir)
                new_wall = True
                API.setWall(x, y, "nesw"[real_dir])

        # --- 2. ATUALIZAR MAPA SE NECESSÁRIO ---
        if new_wall:
            flood_update()

        # Mostra o valor da distância na célula atual para debug
        API.setText(x, y, str(flood[y, x]))

        # --- 3. DECIDIR PARA ONDE IR ---
        best_dir = -1
        lowest_value = 9999
        
        # Verifica os 4 vizinhos
        for d in range(4):
            # Verifica se tem parede na direção 'd' na matriz 'walls'
            if (walls[y, x] & (1 << d)) != 0:
                continue

            # Calcula coordenada do vizinho
            nx, ny = x, y
            if d == 0: ny += 1
            if d == 1: nx += 1
            if d == 2: ny -= 1
            if d == 3: nx -= 1

            # Se está dentro do labirinto
            if 0 <= nx < maze_size and 0 <= ny < maze_size:
                val = flood[ny, nx]
                # Se achou um valor menor, esse é o caminho
                if val != -1 and val < lowest_value:
                    lowest_value = val
                    best_dir = d

        # --- 4. EXECUTAR MOVIMENTO ---
        if best_dir != -1:
            diff = best_dir - orient

            # Corrige a rotação (Lógica de virar)
            if diff == 1 or diff == -3:
                API.turnRight()
            elif diff == -1 or diff == 3:
                API.turnLeft()
            elif diff == 2 or diff == -2:
                API.turnRight()
                API.turnRight()
            
            API.moveForward()

            # Atualiza a posição virtual do robô
            orient = best_dir
            if orient == 0: y += 1
            if orient == 1: x += 1
            if orient == 2: y -= 1
            if orient == 3: x -= 1
            
        else:
            # Se não achou caminho (best_dir continua -1)
            log("Preso ou Cheguei!")
            # Se a distância for 0, é porque chegou no centro
            if flood[y, x] == 0:
                 API.setColor(x, y, "B") # Pinta de Azul
                 log("FIM!")
                 break # Encerra o programa
            else:
                 # Se está preso mas não é o centro, algo deu errado no FloodFill
                 break

if __name__ == "__main__":                        
     main()
