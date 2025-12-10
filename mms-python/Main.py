import API
import sys
import numpy as np
from collections import deque

# GLOBAL CONFIGURATION
maze_size = 16
# Matrix representation of the map
walls = np.zeros((maze_size, maze_size), dtype=int)
# Flood Fill Matrix
flood = np.full((maze_size, maze_size), -1, dtype=int)

def log(string):
    sys.stderr.write("{}\n".format(string))
    sys.stderr.flush()

def set_wall(x: int, y: int, direction: int):
    """
    Marks the wall in the current cell and the symmetrical wall in the neighbor cell.
    direction: 0=N, 1=E, 2=S, 3=W
    """
    # 1. Bitwise operation for marking the cells 
    walls[y, x] |= (1 << direction)
    
    # 2. Calculates the neighbors
    nx, ny = x, y
    if direction == 0: ny += 1
    if direction == 1: nx += 1
    if direction == 2: ny -= 1
    if direction == 3: nx -= 1

    # 3. Marks the neighbor cell (if valid)
    if 0 <= nx < maze_size and 0 <= ny < maze_size:
        # The opposite direction is (direction + 2) % 4
        opposite_dir = (direction + 2) % 4
        walls[ny, nx] |= (1 << opposite_dir)

def flood_update():
    """
    Updates the distance values in the flood matrix.
    """

    # Fills the matrix with -1, making it unknown
    flood.fill(-1)
    # Creates queue Q for processing the cells 
    queue = deque()

    # Definition of the G set (the goal of the robot)
    for r in range(7, 9):
        for c in range(7, 9):
            flood[r, c] = 0
            queue.append((r, c))

    # Mapping: (Wall Bit, Line change, Column change) for N, E, S, W
    path = [(1, 1, 0), (2, 0, 1), (4, -1, 0), (8, 0, -1)]

    # Verify the cells in the matrix  
    while queue:
        r, c = queue.popleft()
        dist = flood[r, c]

        for bit, dr, dc in path:
            nr, nc = r + dr, c + dc
            # Verifies the cell's existence within the matrix
            if 0 <= nr < maze_size and 0 <= nc < maze_size:
                # Verifies the existence of a wall in the next cell 
                if (walls[r, c] & bit) == 0:
                    if flood[nr, nc] == -1:
                        flood[nr, nc] = dist + 1
                        queue.append((nr, nc))



def main():
    log("Running...")
    API.setColor(0, 0, "G")
    API.setText(0, 0, "Start")
   
    # Robot Variables
    x = 0
    y = 0
    orient = 0 # 0:N, 1:E, 2:S, 3:W

    # Initial map calculations 
    flood_update()

    while True:
        # Wall detection and decision making
        new_wall = False 
        
        # Wall ahead 
        if API.wallFront():
            real_dir = orient
            # Updates wall if it's not already marked
            if (walls[y, x] & (1 << real_dir)) == 0:
                set_wall(x, y, real_dir)
                new_wall = True 
                API.setWall(x, y, "nesw"[real_dir])
        
        # Wall to the right 
        if API.wallRight():
            real_dir = (orient + 1) % 4
            if (walls[y, x] & (1 << real_dir)) == 0:
                set_wall(x, y, real_dir)
                new_wall = True
                API.setWall(x, y, "nesw"[real_dir])
        
        # Wall to the left 
        if API.wallLeft():
            real_dir = (orient - 1) % 4
            if (walls[y, x] & (1 << real_dir)) == 0:
                set_wall(x, y, real_dir)
                new_wall = True
                API.setWall(x, y, "nesw"[real_dir])

        # Map update based on new walls
        if new_wall:
            flood_update()

        # Debug: Show distance in the cell
        API.setText(x, y, str(flood[y, x]))

        # Checks if the goal has been reached
        if flood[y, x] == 0:
            log("ARRIVED AT THE CENTER!")
            API.setColor(x, y, "B") # Paints it Blue
            # If you want to continue exploring, do not break here.
            # If you want to stop:
            break

        # Deciside where to go 
        best_dir = -1
        lowest_value = 9999
        
        # Checks the 4 neighbors (N, E, S, W)
        for d in range(4):
            # If there is a wall in this direction, ignore
            if (walls[y, x] & (1 << d)) != 0:
                continue

            # Calculates neighbor coordinates
            nx, ny = x, y
            if d == 0: ny += 1
            if d == 1: nx += 1
            if d == 2: ny -= 1
            if d == 3: nx -= 1

            # Checks limits and Flood Fill value
            if 0 <= nx < maze_size and 0 <= ny < maze_size:
                val = flood[ny, nx]
                # We want to go to a value LOWER than the current one
                if val != -1 and val < lowest_value:
                    lowest_value = val
                    best_dir = d

        # Movement Execution
        if best_dir != -1:
            diff = best_dir - orient

            # Minimum rotation logic
            if diff == 1 or diff == -3:
                API.turnRight()
            elif diff == -1 or diff == 3:
                API.turnLeft()
            elif diff == 2 or diff == -2:
                API.turnRight()
                API.turnRight()
            
            API.moveForward()

            # Updates virtual position and orientation
            orient = best_dir
            if orient == 0: y += 1
            if orient == 1: x += 1
            if orient == 2: y -= 1
            if orient == 3: x -= 1
        else:
            # If no path was found 
            # Happens if stuck in a dead-end
            log("Stuck! Something went wrong.")
            break

if __name__ == "__main__":                        
     main()
