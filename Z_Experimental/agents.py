import random
import time
import os
import string

digits = string.digits + string.ascii_lowercase

class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# Settings
GRID_SIZE = 20
AGENTS = {"A": {"pos": (0, 0)}, "B": {"pos": (GRID_SIZE - 1, GRID_SIZE - 1)}}
EMPTY_TILE = " "
SLEEP_TIME = 0.2  # seconds between turns

RESULTS = {"A": 0, "B": 0, "A-Loss": 0, "B-Loss": 0}

# Initialize grid
grid = [[EMPTY_TILE for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Unit structure: (agent, x, y)
START_UNITS = []
START_POSITIONS = {}

# Spawn initial units
for agent, data in AGENTS.items():
    x, y = data["pos"]
    START_UNITS.append({"agent": agent, "x": x, "y": y})
    START_POSITIONS[(x, y)] = (agent, 1)
    grid[y][x] = agent


# Display function
def display_grid(grid):
    os.system("cls" if os.name == "nt" else "clear")
    for row in reversed(grid):
        print(" ".join(row))
    print()


# Get adjacent tiles
def get_adjacent(x, y):
    adj = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx, ny = x + dx, y + dy
            if (dx != 0 or dy != 0) and 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                adj.append((nx, ny))
    return adj


def score_tile(tile, tile_x, tile_y, unit, positions):
    current_x = unit["x"]
    current_y = unit["y"]
    agent_on_tile = (
        positions[(tile_x, tile_y)][0] if (tile_x, tile_y) in positions else EMPTY_TILE
    )
    value_on_tile = (
        positions[(tile_x, tile_y)][1] if (tile_x, tile_y) in positions else 0
    )
    value_on_current_tile = (
        positions[(current_x, current_y)][1]
        if (current_x, current_y) in positions
        else 0
    )
    is_enemy = (tile != EMPTY_TILE) and (agent_on_tile != unit["agent"])
    is_friendly = (tile != EMPTY_TILE) and (agent_on_tile == unit["agent"])
    
    if tile == EMPTY_TILE:
        home_x = AGENTS[unit["agent"]]["pos"][0]
        home_y = AGENTS[unit["agent"]]["pos"][1]
        current_distance_from_home = abs(home_x - current_x) + abs(home_y - current_y)
        new_distance_from_home = abs(home_x - tile_x) + abs(home_y - tile_y)
        return new_distance_from_home - current_distance_from_home
    else:
        if is_enemy:
            return 10 + (value_on_current_tile - value_on_tile)
        if is_friendly:
            return -10 - value_on_tile
        return -1 


# Unit decision-making heuristic
def move_units(grid, units, start_positions, turn_count):
    new_positions = {}
    intent_moves = {}
    random.shuffle(units)

    # Phase 1: Determine movement intentions
    for unit in units:
        x, y, agent = unit["x"], unit["y"], unit["agent"]
        adj_tiles = get_adjacent(x, y)

        best_move = (x, y)
        best_score = -3
        for nx, ny in adj_tiles:
            tile = grid[ny][nx]
            score = score_tile(tile, nx, ny, unit, start_positions)
            if score > best_score:
                best_move = (nx, ny)
                best_score = score

        intent_moves[(x, y)] = (unit, best_move)

    # Phase 2: Detect and resolve swaps
    final_moves = {}
    occupied_targets = {}
    for src, (unit, target) in intent_moves.items():
        occupied_targets.setdefault(target, []).append((src, unit))

    resolved_sources = set()

    for target, movers in occupied_targets.items():
        if len(movers) == 1:
            src, unit = movers[0]
            # Check for swap scenario explicitly
            if target in intent_moves and intent_moves[target][1] == src:
                # Swap detected, resolve conflict randomly
                other_unit = intent_moves[target][0]
                winner, loser = random.choice([(unit, other_unit), (other_unit, unit)])
                final_moves[target] = winner
                RESULTS[loser['agent'] + "-Loss"] += 1
                resolved_sources.add((src, target))
                resolved_sources.add((target, src))
            else:
                final_moves[target] = unit
                resolved_sources.add((src, target))
        else:
            # Conflict: multiple units want same tile, pick randomly weighted by count
            chosen_src, winner = random.choice(movers)
            final_moves[target] = winner
            for losing_src, loser in movers:
                if loser != winner:
                    RESULTS[loser['agent'] + "-Loss"] += 1
                resolved_sources.add((losing_src, target))

    # Update the grid and unit positions
    grid = [[EMPTY_TILE for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    new_units = START_UNITS[:] if turn_count <= 100 else []

    final_positions = {}

    for pos, unit in final_moves.items():
        nx, ny = pos
        final_positions[(nx, ny)] = (unit["agent"], 1)
        agent = unit["agent"]

        value = digits[1]  # Only one unit per tile due to resolved conflicts

        color = bcolors.OKGREEN if agent == "A" else bcolors.FAIL
        grid[ny][nx] = color + value + bcolors.ENDC

        new_units.append({"agent": agent, "x": nx, "y": ny})

    return new_units, grid, final_positions



# Main simulation loop
TURN_LIMIT = 100
units = START_UNITS
positions = START_POSITIONS
for turn in range(TURN_LIMIT):
    units, grid, positions = move_units(grid, units, positions, turn)
    display_grid(grid)
    time.sleep(SLEEP_TIME)

print("Simulation Complete.")

for unit in units:
    RESULTS[unit["agent"]] += 1
print(RESULTS)
print(positions)
