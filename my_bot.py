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

def agent(obs, config=None):
    moves = []

    is_dict = isinstance(obs, dict)
    player = obs.get("player", 0) if is_dict else obs.player
    raw_planets = obs.get("planets", []) if is_dict else obs.planets

    planets = {p[0]: Planet(*p) for p in raw_planets}
    my_planets = [p for p in planets.values() if p.owner == player]
    targets = [p for p in planets.values() if p.owner != player]

    if not targets: return moves

    my_planets.sort(key=lambda p: p.ships, reverse=True)

    targeted_this_tick = set()

    for mine in my_planets:
        valid_targets = []
        for t in targets:
            if t.id in targeted_this_tick:
                continue

            if not intercepts_sun(mine.x, mine.y, t.x, t.y):
                valid_targets.append(t)

        if not valid_targets:
            continue

        def target_priority(t):
            dist = math.hypot(mine.x - t.x, mine.y - t.y)
            # Prioritize planets we can afford to attack.
            ships_needed = t.ships + 1
            if t.owner != -1:
                ships_needed += int(t.production * (dist / 6.0))

            can_afford = mine.ships >= ships_needed

            # 0: can afford and neutral
            # 1: can afford and enemy
            # 2: can't afford and neutral
            # 3: can't afford and enemy
            category = 0
            if not can_afford: category += 2
            if t.owner != -1: category += 1

            # tie break with dist / production
            return (category, dist / (t.production + 0.1))

        valid_targets.sort(key=target_priority)
        best_target = valid_targets[0]

        ships_needed = best_target.ships + 1

        if best_target.owner != -1:
            dist = math.hypot(mine.x - best_target.x, mine.y - best_target.y)
            ships_needed += int(best_target.production * (dist / 6.0))

        if mine.ships >= ships_needed:
            angle = math.atan2(best_target.y - mine.y, best_target.x - mine.x)
            moves.append([mine.id, angle, ships_needed])
            targeted_this_tick.add(best_target.id)

    return moves
