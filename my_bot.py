import math

def agent(observation, configuration):
    maxSpeed = configuration.shipSpeed
    angular_velocity = observation.angular_velocity
    me = observation.player
    my_planets = [p for p in observation.planets if p[1] == me]
    target_planets = [p for p in observation.planets if p[1] != me]
    enemy_fleets = [f for f in observation.fleets if f[1] != me]
    my_fleets = [f for f in observation.fleets if f[1] == me]

    actions = []

    reserved_ships = {p[0]: 0 for p in my_planets}

    # FIX 1: Point-to-line distance for fleet collision
    def distance_point_to_segment(px, py, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        length_sq = dx**2 + dy**2
        if length_sq == 0:
            return math.hypot(px - x1, py - y1)
        t = ((px - x1) * dx + (py - y1) * dy) / length_sq
        if t < 0:
            return math.hypot(px - x1, py - y1)
        elif t > 1:
            return math.hypot(px - x2, py - y2)
        else:
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            return math.hypot(px - proj_x, py - proj_y)

    for f in enemy_fleets:
        fx, fy = f[2], f[3]
        f_angle = f[4]
        f_ships = f[6]

        ray_x = fx + 150.0 * math.cos(f_angle)
        ray_y = fy + 150.0 * math.sin(f_angle)

        for p in my_planets:
            px, py = p[2], p[3]
            planet_radius = p[4]

            dist = distance_point_to_segment(px, py, fx, fy, ray_x, ray_y)

            if dist <= planet_radius:
                speed = 1.0 + (maxSpeed - 1.0) * ((math.log(max(1, f_ships)) / math.log(1000)) ** 1.5)
                eta = math.hypot(px - fx, py - fy) / speed

                future_garrison = p[5] + p[6] * int(eta)
                if future_garrison < f_ships:
                    reserved_ships[p[0]] += f_ships
                else:
                    reserved_ships[p[0]] = max(reserved_ships[p[0]], int(f_ships - p[6] * eta))

    def predict_position(planet, dt):
        x, y = planet[2], planet[3]
        radius = math.hypot(x - 50, y - 50)
        if radius + planet[4] < 50:
            angle = math.atan2(y - 50, x - 50)
            angle += angular_velocity * dt
            return 50 + radius * math.cos(angle), 50 + radius * math.sin(angle)
        return x, y

    def compute_intercept(p, t, ships):
        speed = 1.0 + (maxSpeed - 1.0) * ((math.log(max(1, ships)) / math.log(1000)) ** 1.5)
        dt = 0
        for _ in range(10):
            tx, ty = predict_position(t, dt)
            dist = math.hypot(tx - p[2], ty - p[3])
            dt = dist / speed
        tx, ty = predict_position(t, dt)
        return math.atan2(ty - p[3], tx - p[2]), dt

    # FIX 3: Safety Buffer to the Sun
    def path_intersects_sun(px, py, tx, ty):
        dx = tx - px
        dy = ty - py
        length = math.hypot(dx, dy)
        if length == 0: return False
        t = ((50 - px) * dx + (50 - py) * dy) / (length * length)
        if t < 0 or t > 1:
            dist1 = math.hypot(px - 50, py - 50)
            dist2 = math.hypot(tx - 50, ty - 50)
            return min(dist1, dist2) < 10.5
        else:
            cx = px + t * dx
            cy = py + t * dy
            return math.hypot(cx - 50, cy - 50) < 10.5

    comet_ids = set(observation.get("comet_planet_ids", []))

    target_incoming = {t[0]: 0 for t in target_planets}
    for f in my_fleets:
        fx, fy = f[2], f[3]
        f_angle = f[4]
        ray_x = fx + 150.0 * math.cos(f_angle)
        ray_y = fy + 150.0 * math.sin(f_angle)
        for t in target_planets:
            tx, ty = t[2], t[3]
            dist = distance_point_to_segment(tx, ty, fx, fy, ray_x, ray_y)
            if dist <= t[4]:
                target_incoming[t[0]] += f[6]
                break

    for p in my_planets:
        available_ships = p[5] - reserved_ships[p[0]]
        available_ships = max(0, available_ships)

        while available_ships > 10:
            best_target = None
            best_score = -99999
            best_angle = 0
            best_ships = 0

            for t in target_planets:
                is_comet = t[0] in comet_ids

                # Let's revert back completely to the logic that beat adv_bot, BUT with the fixes included!
                # Earlier, tracking incoming fleets and subtracting them caused us to beat adv_bot.
                for fraction in [1.0, 0.75, 0.5, 0.25]:
                    ships_to_send = int(available_ships * fraction)
                    if ships_to_send <= 0: continue

                    angle, dt = compute_intercept(p, t, ships_to_send)
                    tx, ty = predict_position(t, dt)

                    if is_comet and math.hypot(tx - 50, ty - 50) > 50.0:
                        continue

                    if path_intersects_sun(p[2], p[3], tx, ty):
                        continue

                    future_garrison = t[5]
                    if t[1] != -1:
                        future_garrison += t[6] * int(dt)

                    future_garrison -= target_incoming[t[0]]

                    if ships_to_send > future_garrison + 5:

                        enemy_bonus = 2.0 if (t[1] != -1 and t[1] != me) else 1.0
                        if is_comet:
                            enemy_bonus = 5.0

                        score = (t[6] * enemy_bonus) / max(1, dt)

                        score -= fraction * 0.0001
                        score -= dt * 0.00001

                        if score > best_score:
                            best_score = score
                            best_target = t
                            best_angle = angle
                            # Let's just always send ships_to_send to ensure speed.
                            best_ships = ships_to_send

            if best_target:
                actions.append([p[0], best_angle, best_ships])
                reserved_ships[p[0]] += best_ships
                available_ships -= best_ships
                target_incoming[best_target[0]] += best_ships
            else:
                break

    return actions
