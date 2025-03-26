import random
import time
import os
import string
import uuid

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
EMPTY_TILE_UNIT = {"agent": EMPTY_TILE, "x": -1, "y": -1, "count": 0}
SLEEP_TIME = 0.2  # seconds between turns

RESULTS = {"A": 0, "B": 0, "A-Loss": 0, "B-Loss": 0}
ACTIONS = []

UNITS = {}

VERBOSE = False

# Initialize grid
grid = [[EMPTY_TILE for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Unit structure: (agent, x, y)
START_UNITS = []
START_POSITIONS = {}


def generate_id():
    return uuid.uuid4()


# Spawn initial units
for agent, data in AGENTS.items():
    x, y = data["pos"]
    _id = generate_id()
    unit = {"agent": agent, "x": x, "y": y, "count": 1}
    START_UNITS.append(_id)
    START_POSITIONS[(x, y)] = _id
    UNITS[_id] = unit
    grid[y][x] = agent


def get_new_units():
    new_units = []
    for agent, data in AGENTS.items():
        x, y = data["pos"]
        _id = generate_id()
        unit = {"agent": agent, "x": x, "y": y, "count": 1}
        new_units.append(_id)
        UNITS[_id] = unit
    return new_units


# Display function
def display_grid(grid, units):
    os.system("cls" if os.name == "nt" else "clear")
    for row in reversed(grid):
        print(" ".join(row))
    print()
    print(f"Units on field: {len(units)}")
    # print(UNITS)
    if VERBOSE:
        print(units)
    for action in ACTIONS:
        print(action)


# Get adjacent tiles
def get_adjacent(x, y):
    adj = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx, ny = x + dx, y + dy
            if (dx != 0 or dy != 0) and 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                adj.append((nx, ny))
    return adj


def get_unit(unit_id):
    if unit := UNITS.get(unit_id):
        return unit
    return EMPTY_TILE_UNIT


def score_tile(tile, tile_x, tile_y, unit_id, positions):
    return random.randint(0, 10)
    unit = get_unit(unit_id)
    current_x = unit["x"]
    current_y = unit["y"]
    unit_on_tile = get_unit(
        positions[(tile_x, tile_y)] if (tile_x, tile_y) in positions else -1
    )
    agent_on_tile = unit_on_tile["agent"]
    value_on_tile = unit_on_tile["count"]
    value_on_current_tile = (
        get_unit(positions[(current_x, current_y)]).get("count", 1)
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
            return 1
        return -1  # ?


def fight(unit_attacker_id, unit_defender_id, positions):
    unit_attacker = get_unit(unit_attacker_id)
    unit_defender = get_unit(unit_defender_id)
    if unit_defender.get("count") == 0:
        return

    fighters = [unit_attacker.get("agent"), unit_defender.get("agent")]
    weights = [unit_attacker.get("count", 0), unit_defender.get("count", 0)]
    winner = random.choices(fighters, weights=weights, k=1)[0]
    loser_unit = (
        unit_attacker if winner == unit_defender.get("agent") else unit_defender
    )
    winner_unit = (
        unit_attacker if winner == unit_attacker.get("agent") else unit_defender
    )
    loser_count = loser_unit["count"]
    RESULTS[loser_unit["agent"] + "-Loss"] += loser_count
    loser_unit_id = (
        unit_attacker_id if winner == unit_defender.get("agent") else unit_defender_id
    )
    winner_unit_id = (
        unit_attacker_id if winner == unit_attacker.get("agent") else unit_defender_id
    )
    UNITS.pop(loser_unit_id, None)
    # remove dead unit
    positions.pop((loser_unit["x"], loser_unit["y"]), None)

    if positions.get((winner_unit["x"], winner_unit["y"])) != winner_unit_id:
        ACTIONS.append("winner must move")
        # winner was split, but there's already a unit where it is. must move to new tile
        positions[(loser_unit["x"], loser_unit["y"])] = winner_unit_id

    if VERBOSE:
        ACTIONS.append(
            f"{(winner_unit['agent'], winner_unit_id, winner_unit['count'])} fought {(loser_unit['agent'], loser_unit_id, loser_count)} and won"
        )


def merge(unit_from_id, unit_to_id, positions):
    unit_from = get_unit(unit_from_id)
    unit_to = get_unit(unit_to_id)

    if unit_from["count"] == 0 or unit_to["count"] == 0:
        return

    if unit_from_id == unit_to_id:
        return  # can't merge with self

    UNITS[unit_to_id]["count"] += unit_from["count"]

    positions.pop((unit_from["x"], unit_from["y"]), None)
    UNITS.pop(unit_from_id, None)

    if VERBOSE:
        ACTIONS.append(
            f"{unit_to['agent']} merged to become {UNITS[unit_to_id]['count']} at {(unit_to['x'], unit_to['y'])}"
        )


def create_new_unit(agent, x, y, count=1):
    _id = generate_id()
    unit = {"agent": agent, "x": x, "y": y, "count": count}
    UNITS[_id] = unit
    return _id


def add_unit(positions, unit_id):
    # check if there's a unit already there
    unit = get_unit(unit_id)
    if unit_on_tile_id := positions.get((unit["x"], unit["y"])):
        unit_on_tile = get_unit(unit_on_tile_id)
        if unit_on_tile["agent"] == unit["agent"]:
            UNITS[unit_on_tile_id]["count"] += unit["count"]
            if VERBOSE:
                ACTIONS.append(
                    f"{unit['agent']} merged to become {UNITS[unit_on_tile_id]['count']} at {(unit['x'], unit['y'])}"
                )
            UNITS.pop(unit_id, None)
        else:
            fight(unit_id, unit_on_tile_id, positions)
            if VERBOSE:
                ACTIONS.append(
                    f"{unit['agent']} fought {unit_on_tile['agent']} at {(unit['x'], unit['y'])}"
                )
    else:
        positions[(unit["x"], unit["y"])] = unit_id


def calculate_best_move(unit_id, positions, can_stay=True):
    unit = get_unit(unit_id)
    x, y = unit["x"], unit["y"]
    adj_tiles = get_adjacent(x, y)
    if can_stay:
        adj_tiles.append((x, y))  # include stay option

    best_score = 0
    best_move = (x, y) if can_stay else adj_tiles[0]
    options = {}
    for tile in adj_tiles:
        score = score_tile(grid[tile[1]][tile[0]], tile[0], tile[1], unit_id, positions)
        options[tile] = score
        if score > best_score:
            best_score = score
            best_move = tile

    return best_move, options


def perform_action(positions, unit_id, can_stay=True, verbose=False):
    unit = get_unit(unit_id)
    x, y, agent, count = unit["x"], unit["y"], unit["agent"], unit["count"]
    if count == 0:
        return

    best_move, options = calculate_best_move(unit_id, positions, can_stay)

    if VERBOSE or verbose:
        ACTIONS.append(
            f"{unit['agent']} at {(x, y)} picked {best_move} | {can_stay} |  scoring: {options}"
        )

    if unit_on_tile_id := positions.get(best_move):
        if (best_move != (x, y)) and (unit_on_tile_id != unit_id):
            unit_on_tile = get_unit(unit_on_tile_id)
            if unit_on_tile.get("agent") != agent:
                fight(unit_id, unit_on_tile_id, positions)
                # if split unit wins, it stays, but there's already a unit where it is.
            else:
                merge(unit_id, unit_on_tile_id, positions)
    else:
        positions[best_move] = unit_id
        positions.pop((x, y), None)
        UNITS[unit_id]["x"] = best_move[0]
        UNITS[unit_id]["y"] = best_move[1]
        # ACTIONS.append(f"{agent} moved from {(x, y)} to {best_move}")


def handle_split(unit_id, positions):
    if unit := UNITS.get(unit_id):
        x, y, agent, count = (
            unit["x"],
            unit["y"],
            unit["agent"],
            unit.get("count", 1),
        )

        if count == 0:
            return  # they died

        if count > 1 and random.choice([True, False]):
            # Do split (only two groups to prevent explosion)
            split_amount = random.randint(1, count - 1)
            stay_count = count - split_amount
            UNITS[unit_id]["count"] = stay_count

            new_unit_id = create_new_unit(agent=agent, x=x, y=y, count=split_amount)

            if VERBOSE:
                ACTIONS.append(
                    f"{agent} split at {(x, y)} to become {split_amount} and {stay_count} from {count}"
                )

            # only new group move, old group stays
            perform_action(positions, new_unit_id, can_stay=False)
            current_location = positions.get((x, y))
            if current_location is not None and current_location != unit_id:
                ACTIONS.append(f"WTF just happened? {current_location} != {unit_id}")
                
            positions[(x, y)] = unit_id

            if VERBOSE:
                if new_unit := UNITS.get(new_unit_id):
                    new_unit_coords = (new_unit["x"], new_unit["y"])
                    current_unit_coords = (UNITS[unit_id]["x"], UNITS[unit_id]["y"])

                    ACTIONS.append(
                        f"{agent} split at {(x, y)} to become {(split_amount, new_unit_id)} at {new_unit_coords} and {stay_count} to remain at {current_unit_coords} from {count}"
                    )
                    ACTIONS.append(
                        [
                            positions.get(new_unit_coords) == new_unit_id,
                            positions.get(current_unit_coords) == unit_id,
                            (x, y),
                            current_unit_coords,
                            positions.get(current_unit_coords),
                        ]
                    )
                else:
                    ACTIONS.append(f"split unit merged to adjacent unit")
        else:
            perform_action(positions, unit_id)


def move_units(grid, unit_ids, positions, turn_count):
    random.shuffle(unit_ids)

    for unit_id in unit_ids:
        handle_split(unit_id, positions)

    # Update grid and new unit positions
    grid = [[EMPTY_TILE for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    if turn_count < 100:
        new_units = get_new_units()
        for unit in new_units:
            add_unit(positions, unit)
    else:
        new_units = []

    new_units = []

    for (nx, ny), unit_id in positions.items():
        unit = get_unit(unit_id)
        count = unit["count"]
        agent = unit["agent"]

        if count == 0:
            continue

        value = digits[min(count, 35)]

        color = bcolors.OKGREEN if agent == "A" else bcolors.FAIL
        grid[ny][nx] = color + value + bcolors.ENDC

        UNITS[unit_id]["x"] = nx
        UNITS[unit_id]["y"] = ny

        new_units.append(unit_id)

    return new_units, grid, positions


# Main simulation loop
TURN_LIMIT = 100
unit_ids = START_UNITS
positions = START_POSITIONS
for turn in range(TURN_LIMIT):
    unit_ids, grid, positions = move_units(grid, unit_ids, positions, turn)
    display_grid(grid, unit_ids)
    time.sleep(SLEEP_TIME)

print("Simulation Complete.")

for unit_id in unit_ids:
    unit = get_unit(unit_id)
    RESULTS[unit["agent"]] += unit["count"]
print(RESULTS)
# print(positions)
# print(UNITS)
