import math
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet

def intercepts_sun(mine_x, mine_y, target_x, target_y):
    cx, cy = 50.0, 50.0
    r = 10.05
    dx = target_x - mine_x
    dy = target_y - mine_y
    l2 = dx**2 + dy**2
    if l2 == 0:
        return math.hypot(mine_x - cx, mine_y - cy) < r
    t_val = ((cx - mine_x) * dx + (cy - mine_y) * dy) / l2
    if 0 <= t_val <= 1:
        closest_x = mine_x + t_val * dx
        closest_y = mine_y + t_val * dy
        if math.hypot(closest_x - cx, closest_y - cy) < r:
            return True
    return False

def agent(obs):
    moves = []

    is_dict = isinstance(obs, dict)
    player = obs.get("player", 0) if is_dict else obs.player
    raw_planets = obs.get("planets", []) if is_dict else obs.planets

    planets = {p[0]: Planet(*p) for p in raw_planets}
    my_planets = [p for p in planets.values() if p.owner == player]
    targets = [p for p in planets.values() if p.owner != player]

    if not targets: return moves

    # We will build a pool of requests across ALL planets to ensure we don't overkill
    # But ONLY for enemies! Overkilling neutrals is fine because they become our ships.
    # Overkilling enemies just wastes ships fighting their defenses.
    # Wait, overkilling neutrals is ALSO bad because we could have used those ships to conquer ANOTHER neutral.
    # Let's track pending attacks simply by iterating over my_planets sorted by ships (largest first).

    # Sort my planets by ships descending so we attack with our biggest fleets first
    my_planets.sort(key=lambda p: p.ships, reverse=True)

    targeted_this_tick = set()

    for mine in my_planets:
        valid_targets = []
        for t in targets:
            # Don't target planets we are already targeting this tick
            if t.id in targeted_this_tick:
                continue

            if not intercepts_sun(mine.x, mine.y, t.x, t.y):
                valid_targets.append(t)

        if not valid_targets:
            continue

        nearest = min(valid_targets, key=lambda t: math.hypot(mine.x - t.x, mine.y - t.y))

        ships_needed = nearest.ships + 1

        if nearest.owner != -1:
            dist = math.hypot(mine.x - nearest.x, mine.y - nearest.y)
            ships_needed += int(nearest.production * (dist / 2.0))

        if mine.ships >= ships_needed:
            angle = math.atan2(nearest.y - mine.y, nearest.x - mine.x)
            moves.append([mine.id, angle, ships_needed])
            targeted_this_tick.add(nearest.id) # Mark as targeted

    return moves
