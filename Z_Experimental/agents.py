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
GOALS = {
    "Charlie": (0, GRID_SIZE-1),
    "Delta": (GRID_SIZE-1, 0),
    "Echo": (GRID_SIZE // 4, GRID_SIZE // 4),
    "Foxtrot": ((GRID_SIZE * 3) // 4, (GRID_SIZE * 3) // 4),
}
REVERSE_GOALS = {pos: goal for goal,pos in GOALS.items()}
EMPTY_TILE = " "
EMPTY_TILE_UNIT = {"agent": EMPTY_TILE, "x": -1, "y": -1, "count": 0, "is_dead": True}
SLEEP_TIME = 0.2  # seconds between turns

RESULTS = {"A": 0, "B": 0, "A-Loss": 0, "B-Loss": 0, "A-Objective-Score": 0, "B-Objective-Score": 0}
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


def create_new_unit(agent, x, y, count=1):
    _id = generate_id()
    unit = {
        "agent": agent,
        "x": x,
        "y": y,
        "count": count,
        "goal": GOALS[random.choice(list(GOALS.keys()))],
        "is_dead": False,
    }
    UNITS[_id] = unit
    return _id


def remove_unit(unit_id, positions, was_killed=False):
    if unit := UNITS.get(unit_id):
        if was_killed:
            RESULTS[unit["agent"] + "-Loss"] += unit["count"]

        x, y = unit["x"], unit["y"]
        if (x, y) in positions:
            positions.pop((x, y), None)
        UNITS.pop(unit_id, None)


# Spawn initial units
for agent, data in AGENTS.items():
    x, y = data["pos"]
    _id = create_new_unit(agent=agent, x=x, y=y)

    START_UNITS.append(_id)
    START_POSITIONS[(x, y)] = _id
    grid[y][x] = agent


def get_new_units():
    new_units = []
    for agent, data in AGENTS.items():
        x, y = data["pos"]
        _id = create_new_unit(agent=agent, x=x, y=y)
        new_units.append(_id)
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
    # ACTIONS.append("unit not found")


def score_tile(tile, tile_x, tile_y, unit_id, positions):
    # return random.randint(0, 10)
    if unit := get_unit(unit_id):
        current_x = unit["x"]
        current_y = unit["y"]

        if unit_on_tile := get_unit(
            positions[(tile_x, tile_y)] if (tile_x, tile_y) in positions else -1
        ):
            agent_on_tile = unit_on_tile["agent"]
            value_on_tile = unit_on_tile["count"]
            value_on_current_tile = unit["count"]

            if agent_on_tile != unit["agent"]:
                # is enemy
                return value_on_current_tile - value_on_tile
            return 1  # is friendly

        else:
            goal_x, goal_y = unit["goal"]
            current_distance_from_goal = abs(goal_x - current_x) + abs(
                goal_y - current_y
            )
            new_distance_from_goal = abs(goal_x - tile_x) + abs(goal_y - tile_y)
            return (current_distance_from_goal - new_distance_from_goal) * 5
    return -1


def fight(unit_attacker_id, unit_defender_id, positions):
    if unit_attacker := get_unit(unit_attacker_id):
        if unit_defender := get_unit(unit_defender_id):
            if unit_defender["count"] == 0 or unit_attacker["count"] == 0:
                ACTIONS.append("Um, fight init with 0 count?")
                return

            nearby_tiles = get_adjacent(unit_defender["x"], unit_defender["y"])
            nearby_tiles.extend(get_adjacent(unit_attacker["x"], unit_attacker["y"]))
            additional_weights = {_agent: 0 for _agent in AGENTS.keys()}
            for tile in nearby_tiles:
                if unit := UNITS.get(positions.get(tile)):
                    additional_weights[unit["agent"]] += unit["count"]

            fighters = [unit_attacker["agent"], unit_defender["agent"]]
            weights = [unit_attacker["count"], unit_defender["count"]]
            winner = random.choices(fighters, weights=weights, k=1)[0]
            loser_unit = (
                unit_attacker if winner == unit_defender["agent"] else unit_defender
            )
            winner_unit = (
                unit_attacker if winner == unit_attacker["agent"] else unit_defender
            )
            loser_count = loser_unit["count"]

            loser_unit_id = (
                unit_attacker_id
                if winner == unit_defender["agent"]
                else unit_defender_id
            )
            winner_unit_id = (
                unit_attacker_id
                if winner == unit_attacker["agent"]
                else unit_defender_id
            )

            remove_unit(loser_unit_id, positions, was_killed=True)

            if positions.get((winner_unit["x"], winner_unit["y"])) != winner_unit_id:
                if VERBOSE:
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

    if not unit_from or not unit_to or unit_from["count"] == 0 or unit_to["count"] == 0:
        ACTIONS.append("Merge init with 0 count")
        return

    if unit_from_id == unit_to_id:
        return  # can't merge with self

    UNITS[unit_to_id]["count"] += unit_from["count"]

    remove_unit(unit_from_id, positions)

    if VERBOSE:
        ACTIONS.append(
            f"{unit_to['agent']} merged to become {UNITS[unit_to_id]['count']} at {(unit_to['x'], unit_to['y'])}"
        )


def add_unit(positions, unit_id):
    # check if there's a unit already there
    if unit := get_unit(unit_id):
        if unit_on_tile_id := positions.get((unit["x"], unit["y"])):
            if unit_on_tile := get_unit(unit_on_tile_id):
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
    if unit := get_unit(unit_id):
        x, y = unit["x"], unit["y"]
        adj_tiles = get_adjacent(x, y)
        if can_stay:
            adj_tiles.append((x, y))  # include stay option

        best_score = 0
        best_move = (x, y) if can_stay else adj_tiles[0]
        options = {}
        for tile in adj_tiles:
            score = score_tile(
                grid[tile[1]][tile[0]], tile[0], tile[1], unit_id, positions
            )
            options[tile] = score
            if score > best_score:
                best_score = score
                best_move = tile

        return best_move, options
    return (-1, -1), None


def perform_action(positions, unit_id, can_stay=True, verbose=False):
    if unit := get_unit(unit_id):
        x, y, agent, count = unit["x"], unit["y"], unit["agent"], unit["count"]
        if count == 0:
            ACTIONS.append("action init with 0 count")
            return

        best_move, options = calculate_best_move(unit_id, positions, can_stay)

        if VERBOSE or verbose:
            ACTIONS.append(
                f"{unit['agent']} at {(x, y)} picked {best_move} | {can_stay} |  scoring: {options}"
            )

        if unit_on_tile_id := positions.get(best_move):
            if (best_move != (x, y)) and (unit_on_tile_id != unit_id):
                if unit_on_tile := get_unit(unit_on_tile_id):
                    if unit_on_tile["agent"] != agent:
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


def move_or_split(unit_id, positions):
    if unit := UNITS.get(unit_id):
        count = unit["count"]

        if count == 0:
            ACTIONS.append("move/split init with 0 count")
            return  # they died

        if count > 1 and random.choice([True, False]):
            handle_split(unit_id, unit, positions)
        else:
            perform_action(positions, unit_id)


def handle_split(unit_id, unit, positions):
    x, y, agent, count = (
        unit["x"],
        unit["y"],
        unit["agent"],
        unit["count"],
    )
    # Do split (only two groups to prevent explosion)
    split_amount = random.randint(1, count - 1)
    stay_count = count - split_amount
    assert (stay_count + split_amount) == count
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


def move_units(grid, unit_ids, positions, turn_count):
    random.shuffle(unit_ids)

    for unit_id in unit_ids:
        move_or_split(unit_id, positions)

    # Update grid and new unit positions
    grid = [[EMPTY_TILE for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    if turn_count < 100:
        new_units = get_new_units()
        for unit in new_units:
            add_unit(positions, unit)
    else:
        new_units = []

    new_units = []

    for goal, pos in GOALS.items():
        grid[pos[0]][pos[1]] = goal[0]

    for (nx, ny), unit_id in positions.items():
        if unit := get_unit(unit_id):
            count = unit["count"]
            agent = unit["agent"]

            if count == 0:
                ACTIONS.append("move init with 0 count")
                continue

            value = digits[min(count, 35)]

            color = bcolors.OKGREEN if agent == "A" else bcolors.FAIL
            grid[ny][nx] = color + value + bcolors.ENDC

            UNITS[unit_id]["x"] = nx
            UNITS[unit_id]["y"] = ny
            
            if REVERSE_GOALS.get((nx, ny)):
                RESULTS[f"{agent}-Objective-Score"] += 1

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
    if unit := get_unit(unit_id):
        RESULTS[unit["agent"]] += unit["count"]
print(RESULTS)
A_total = RESULTS["A"] + RESULTS["A-Loss"]
B_total = RESULTS["B"] + RESULTS["B-Loss"]
print(f"A: {RESULTS['A']} / {A_total} | B: {RESULTS['B']} / {B_total}")
# print(positions)
# print(UNITS)
