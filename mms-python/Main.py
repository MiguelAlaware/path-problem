import API
import sys
import numpy as np
from collections import deque

def log(string):
    sys.stderr.write("{}\n".format(string))
    sys.stderr.flush()

maze_size = 16
walls = np.zeros((maze_size, maze_size), dtype=int)
flood = np.full((maze_size, maze_size), -1, dtype=int)


def flood_update():
    flood.fill(-1)
    queue = deque()

    for r in range(7,9):
        for c in range(7, 9):
            flood[r, c] = 0
            queue.append((r,c))

    
    while queue:
        r, c = queue.popleft()
        dist = flood[r, c]
    
        path = [(1, 1, 0), (2, 0, 1), (4, -1, 0), (8, 0, -1)]

        for bit, dr, dc in path:
            nr, nc = r + dr, c + dc

        if 0 <= nr < maze_size and 0 <= nc < maze_size:
            if (walls[r, c] & bit) == 0:
                if flood[nr, nc] == -1:
                   flood[nr, nc] = dist + 1
                   queue.append((nr, nc))

def main():
    log("Running...")
    API.setColor(0, 0, "G")
    API.setText(0, 0, "abc")
    x = 0
    y = 0
    orient = 0
    
    flood_update()

    while True:
       new_wall = False 

       if API.wallFront():
            real_dir = orient
            bit = (1 << real_dir)
            if (walls[y, x] & bit) == 0:
                walls[y, x] |= bit
                new_wall = True 
                API.setWall(x, y, "nesw"[real_dir])
       if API.wallRight():
            real_dir = (orient + 1) % 4
            bit = (1 << real_dir)
            if (walls[y, x] & bit) == 0:
                walls[y, x] |= bit
                new_wall = True
                API.setWall(x, y, "nesw"[real_dir])
       if API.wallLeft():
            real_dir = (orient - 1) % 4
            bit = (1 << real_dir)
            if (walls[y, x] & bit) == 0:
                walls[y, x] |= bit
                new_wall = True
                API.setWall(x, y, "nesw"[real_dir])

    if new_wall:
           flood_update()

    API.setText(x, y, str(flood[x, y]))

    best_dir = -1
    lowest_value = 9999
    
    ndistance = flood[y, x]
    
    for d in range(4):
        if (walls[y, x] & (1 << d)) != 0:
            continue
        
        nx, ny = x, y 
        if d == 0: ny += 1
        if d == 1: nx += 1
        if d == 2: ny -= 1
        if d == 3: nx -= 1

        if 0 <= nx < maze_size and 0 <= ny < maze_size:
            val = flood[ny, nx]
            if val < lowest_value:
              lowest_value = val
              best_dir = d

        if best_dir != -1:
            diff = best_dir - orient

            if diff == 1 or diff == -3:
               API.turnRight()
            elif diff == -1 or diff == 3:
               API.turnLeft()
            elif diff == 2 or diff == -2:
              API.turnRight()
              API.turnRight()
            
            API.moveForward()

            orient = best_dir
            if orient == 0: y += 1
            if orient == 1: x += 1
            if orient == 2: y -= 1
            if orient == 3: x -= 1
        else:
            log("Preso")
            if flood[y, x] == 0:
                log("Arrived")
                API.setColor(x, y, "B")
                break
            
if __name__ == "__main__":                        
     main()



