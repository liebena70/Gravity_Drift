import turtle
import random
import math
# ============================================================
# GRAVITY DRIFT - SPACE SHOOTER
# Enhanced Edition: Multi-phase Bosses, XP/Leveling, Mega Laser,
# Wingman Partner, and Shield Overheat Protection
# ============================================================
WIDTH = 800
HEIGHT = 700
PLAYER_SPEED = 7
BULLET_SPEED = 12
ENEMY_DROP_CHANCE = 0.16
BOSS_DROP_CHANCE = 0.30
BOSS_THRESHOLDS = [750, 2000, 4000]
BOSS_REWARDS = {1: 250, 2: 500, 3: 0}
BOSS_NAMES = {
    1: "STRIKER",
    2: "PHANTOM",
    3: "SINGULARITY"
}
# Shield balancing
SHIELD_DRAIN = 0.30
SHIELD_REGEN = 0.18
SHIELD_ENEMY_REWARD = 1.5
SHIELD_BOSS_REWARD = 12
SHIELD_GACHA_REWARD = 30
SHIELD_OVERHEAT_FRAMES = 250  # 5 detik pada 50 fps
# Enemy spawning during boss fights
BOSS_ENEMY_INTERVAL = 45
BOSS_ENEMY_CAP = 3
# Permanent upgrades (rewarded after boss 1 and boss 2)
FIRE_INTERVAL_BASE = 8
FIRE_INTERVAL_UPGRADED = 5
PERM_SHIELD_COOLDOWN = 500      # frames (~10 s at 50 fps)
# Shield Delay Settings (Nerf: 2 detik delay saat shield dimatikan)
SHIELD_DEACTIVATE_DELAY = 100    # 2 detik (100 frames @ 50 fps)
# Partner and Mega Laser Settings
PARTNER_DURATION = 1500         # 30 detik (1500 frames @ 50 fps)
PARTNER_FIRE_INTERVAL = 18       # Lebih rendah dibanding player (8 / 5)
MAX_LASER_AMMO = 5
PLAYER_LASER_WIDTH = 75         # Sekitar 3x badan pesawat (~25px lebar dasar)
PLAYER_LASER_DAMAGE = 30
# Gravity Drift Orb Settings (Tombol K - Attract)
GRAVITY_ORB_COOLDOWN = 500       # 10 detik (500 frames @ 50 fps)
GRAVITY_ORB_VORTEX_DURATION = 200 # 4 detik (200 frames @ 50 fps)
GRAVITY_ORB_PULL_RADIUS = 200    # Radius hisapan gravitasi
GRAVITY_ORB_EXPLODE_DAMAGE = 45  # Damage ledakan setelah 4 detik
# Gravity Repel Wave Settings (Tombol J - Repel)
GRAVITY_REPEL_COOLDOWN = 350     # 7 detik (350 frames @ 50 fps)
GRAVITY_REPEL_MAX_RADIUS = 240   # Radius gelombang tolak gravitasi
GRAVITY_REPEL_SPEED = 20         # Kecepatan pemuaian gelombang
# ============================================================
# SCREEN
# ============================================================
screen = turtle.Screen()
screen.setup(WIDTH, HEIGHT)
screen.title("GRAVITY DRIFT | Space Shooter - Enhanced Edition")
screen.bgcolor("#080b1c")
screen.tracer(0)
# ============================================================
# GAME STATE
# ============================================================
score = 0
lives = 3
energy = 45
max_energy = 100
# Experience Points & Player Leveling
player_level = 1
player_xp = 0
player_xp_needed = 100
level_10_bonus_awarded = False
game_over = False
paused = False
frame = 0
keys = set()
enemies = []
bullets = []
enemy_bullets = []
powerups = []
boss = None
boss_bullets = []
# Debuff States
debuff_slow_until = 0       # 10 detik (500 frames)
debuff_silence_until = 0    # 10 detik (500 frames) - blokir ability
debuff_reverse_until = 0    # 5 detik (250 frames) - reverse control
# Boss vertical laser state
laser_phase = "idle"
laser_until = 0
laser_x = 0
laser_width = 100
laser_damage = 1
laser_warning = None
laser_beam = None
# Boss horizontal laser state (Boss Terakhir / Singularity)
laser_h_phase = "idle"
laser_h_until = 0
laser_h_y = 0
laser_h_height = 80
laser_h_damage = 1
laser_h_warning = None
laser_h_beam = None
# Boss mini guards
boss_guards = []
# Player Mega Laser state
player_laser_ammo = 0
player_laser_timer = 0
player_laser_x = 0
# Gravity Drift Orb state (Attract - Tombol K)
gravity_orb_ready_at = 0
gravity_orb = None
gravity_explosion_timer = 0
gravity_explosion_pos = (0, 0)
# Gravity Repel Wave state (Repel - Tombol J)
gravity_repel_ready_at = 0
gravity_repel_active = False
gravity_repel_radius = 0
gravity_repel_x = 0
gravity_repel_y = 0
gravity_repel_pushed_enemies = set()
# Partner Wingman state
partner_until = 0
# Shield state (Overheat & Reactivation Delay Nerf)
shield_overheated_until = 0
shield_was_active = False
shield_delay_until = 0
# Temporary buffs
triple_shot_until = 0
overheat_until = 0
invincible_until = 0
boss_level = 0
next_boss_score = BOSS_THRESHOLDS[0]
# Permanent upgrades
perm_dual = False
perm_fire_rate = False
perm_shield = False
perm_shield_ready_at = 0
# Message timer
message_until = 0
# ============================================================
# DRAWING HELPERS
# ============================================================
def make_turtle(shape, color, x=0, y=0):
    obj = turtle.Turtle()
    obj.shape(shape)
    obj.color(color)
    obj.penup()
    obj.goto(x, y)
    obj.speed(0)
    return obj
def make_text(color="white", size=12, bold=False):
    obj = turtle.Turtle()
    obj.hideturtle()
    obj.penup()
    obj.color(color)
    obj.speed(0)
    return obj
def draw_text(obj, x, y, text, align="left",
              font=("Arial", 12, "normal")):
    obj.clear()
    obj.goto(x, y)
    obj.write(text, align=align, font=font)
# ============================================================
# PLAYER & PARTNER
# ============================================================
player = make_turtle("triangle", "#48e5ff", 0, -260)
player.setheading(90)
player.shapesize(1.35, 1.35)
partner_turtle = make_turtle("triangle", "#00ffea", 1200, 1200)
partner_turtle.setheading(90)
partner_turtle.shapesize(0.9, 0.9)
partner_turtle.hideturtle()
shield_visual = turtle.Turtle()
shield_visual.hideturtle()
shield_visual.speed(0)
shield_visual.penup()
shield_visual.color("#00ffff")
shield_visual.pensize(4)
shield_outer = turtle.Turtle()
shield_outer.hideturtle()
shield_outer.speed(0)
shield_outer.penup()
shield_outer.color("#ffffff")
shield_outer.pensize(2)
# Permanent (auto) shield ring
aegis_visual = turtle.Turtle()
aegis_visual.hideturtle()
aegis_visual.speed(0)
aegis_visual.penup()
aegis_visual.color("#7dff9b")
aegis_visual.pensize(2)
# Mega laser drawer
player_laser_drawer = turtle.Turtle()
player_laser_drawer.hideturtle()
player_laser_drawer.speed(0)
player_laser_drawer.penup()
# Gravity vortex drawer
gravity_vortex_pen = turtle.Turtle()
gravity_vortex_pen.hideturtle()
gravity_vortex_pen.speed(0)
gravity_vortex_pen.penup()
# Gravity repel drawer
gravity_repel_pen = turtle.Turtle()
gravity_repel_pen.hideturtle()
gravity_repel_pen.speed(0)
gravity_repel_pen.penup()
# ============================================================
# HUD ELEMENTS
# ============================================================
hud = make_text("#ffffff")
xp_text = make_text("#38ffb0")
energy_text = make_text("#52eaff")
status_text = make_text("#ffe66d")
boss_text = make_text("#ff7777")
message_text = make_text("#ffffff")
navigator_text = make_text("#dce8ff")
# Energy Bar
energy_bar_bg = make_turtle("square", "#27314d", -260, 260)
energy_bar_bg.shapesize(0.55, 5.2)
energy_bar = make_turtle("square", "#38e6c5", -260, 260)
energy_bar.shapesize(0.40, 5.0)
# XP Bar
xp_bar_bg = make_turtle("square", "#1e293b", -260, 285)
xp_bar_bg.shapesize(0.55, 5.2)
xp_bar = make_turtle("square", "#38bdf8", -260, 285)
xp_bar.shapesize(0.40, 5.0)
# Boss HP Bar
boss_bar_bg = make_turtle("square", "#49212d", 0, 225)
boss_bar_bg.shapesize(0.7, 15)
boss_bar_bg.hideturtle()
boss_bar = make_turtle("square", "#ff4757", 0, 225)
boss_bar.shapesize(0.45, 15)
boss_bar.hideturtle()
def get_player_damage():
    return 1.0 + (player_level - 1) * 0.25
def add_player_xp(amount):
    global player_xp, player_level, player_xp_needed, lives, level_10_bonus_awarded
    player_xp += amount
    leveled_up = False
    while player_xp >= player_xp_needed:
        player_xp -= player_xp_needed
        player_level += 1
        player_xp_needed = player_level * 100
        leveled_up = True
        if player_level == 10 and not level_10_bonus_awarded:
            lives += 1
            level_10_bonus_awarded = True
            show_message("★ LEVEL 10! +1 MAX HP / BONUS LIFE! ★", 195, 17, 130)
            return
    if leveled_up:
        dmg = get_player_damage()
        show_message(f"★ LEVEL UP! LV {player_level} (DMG: {dmg:.2f}) ★", 195, 15, 80)
def show_message(text, y=190, size=18, duration=90):
    global message_until
    draw_text(
        message_text, 0, y, text,
        align="center",
        font=("Arial", size, "bold")
    )
    message_until = frame + duration
def update_hud():
    hud.clear()
    xp_text.clear()
    energy_text.clear()
    status_text.clear()
    boss_text.clear()
    navigator_text.clear()
    draw_text(
        hud, -380, 310,
        f"SCORE: {score}   HP: {'♥ ' * max(0, lives)}   LVL: {player_level} (DMG x{get_player_damage():.2f})",
        font=("Arial", 12, "bold")
    )
    xp_ratio = min(1.0, max(0.0, player_xp / max(1, player_xp_needed)))
    draw_text(
        xp_text, -380, 280,
        f"EXP: {player_xp} / {player_xp_needed}",
        font=("Arial", 9, "bold")
    )
    xp_bar.goto(-260 - 100 * (1 - xp_ratio), 285)
    xp_bar.shapesize(0.40, max(0.01, 5.0 * xp_ratio))
    energy_ratio = min(1.0, max(0.0, energy / max_energy))
    draw_text(
        energy_text, -380, 255,
        f"SHIELD: {int(energy)} / {max_energy}",
        font=("Arial", 9, "bold")
    )
    energy_bar.goto(-260 - 100 * (1 - energy_ratio), 260)
    energy_bar.shapesize(0.40, max(0.01, 5.0 * energy_ratio))
    if frame < overheat_until:
        weapon = f"OVERHEATED ({(overheat_until - frame) / 50:.1f}s)"
        weapon_color = "#ff775f"
    elif frame < triple_shot_until:
        weapon = f"TRIPLE SHOT ({(triple_shot_until - frame) / 50:.1f}s)"
        weapon_color = "#54f28b"
    else:
        weapon = "AUTO FIRE"
        weapon_color = "#dce8ff"
    status_text.color(weapon_color)
    laser_boxes = "■ " * player_laser_ammo + "□ " * (MAX_LASER_AMMO - player_laser_ammo)
    laser_hud = f"MEGA LASER [L]: [{laser_boxes.strip()}]"
    if gravity_orb is not None:
        if gravity_orb["state"] == "vortex":
            grav_status = f"VORTEX ({gravity_orb['timer']/50:.1f}s)"
        else:
            grav_status = "LAUNCHED"
    elif frame >= gravity_orb_ready_at:
        grav_status = "READY"
    else:
        grav_status = f"{(gravity_orb_ready_at - frame)/50:.1f}s"
    gravity_hud = f"GRAV ORB [K]: {grav_status}"
    if gravity_repel_active:
        repel_status = "SHOCKWAVE!"
    elif frame >= gravity_repel_ready_at:
        repel_status = "READY"
    else:
        repel_status = f"{(gravity_repel_ready_at - frame)/50:.1f}s"
    repel_hud = f"GRAV WAVE [J]: {repel_status}"
    draw_text(
        status_text, 380, 312, weapon,
        align="right", font=("Arial", 11, "bold")
    )
    status_text.goto(380, 292)
    status_text.write(
        laser_hud,
        align="right", font=("Consolas", 10, "bold")
    )
    status_text.goto(380, 274)
    status_text.write(
        gravity_hud,
        align="right", font=("Consolas", 10, "bold")
    )
    status_text.goto(380, 256)
    status_text.write(
        repel_hud,
        align="right", font=("Consolas", 10, "bold")
    )
    effects = []
    if frame < triple_shot_until:
        effects.append(f"Triple Shot: {(triple_shot_until - frame) / 50:.1f}s")
    if frame < overheat_until:
        effects.append(f"Overheat: {(overheat_until - frame) / 50:.1f}s")
    if frame < partner_until:
        effects.append(f"Wingman Drone: {(partner_until - frame) / 50:.1f}s")
    if frame < debuff_slow_until:
        effects.append(f"DEBUFF Slow: {(debuff_slow_until - frame) / 50:.1f}s")
    if frame < debuff_silence_until:
        effects.append(f"DEBUFF Blocked: {(debuff_silence_until - frame) / 50:.1f}s")
    if frame < debuff_reverse_until:
        effects.append(f"DEBUFF Reverse: {(debuff_reverse_until - frame) / 50:.1f}s")
    if gravity_orb is not None:
        effects.append(f"Gravity Orb: {grav_status}")
    elif frame < gravity_orb_ready_at:
        effects.append(f"Gravity Orb CD: {(gravity_orb_ready_at - frame)/50:.1f}s")
    if gravity_repel_active:
        effects.append("Gravity Wave: ACTIVE")
    elif frame < gravity_repel_ready_at:
        effects.append(f"Gravity Wave CD: {(gravity_repel_ready_at - frame)/50:.1f}s")
    if frame < invincible_until:
        effects.append(f"Invincible: {(invincible_until - frame) / 50:.1f}s")
    if frame < shield_overheated_until:
        shield_status = f"OVERHEATED! ({(shield_overheated_until - frame) / 50:.1f}s)"
    elif frame < shield_delay_until:
        shield_status = f"RECHARGE ({(shield_delay_until - frame) / 50:.1f}s)"
    elif "space" in keys and energy > 0:
        shield_status = "ACTIVE"
    elif energy <= 0:
        shield_status = "DEPLETED"
    else:
        shield_status = "READY"
    effects.append(f"Gravity Shield: {shield_status}")
    perks = []
    if perm_dual:
        perks.append("DUAL")
    if perm_fire_rate:
        perks.append("RAPID")
    if perm_shield:
        if frame >= perm_shield_ready_at:
            perks.append("AEGIS READY")
        else:
            perks.append(f"AEGIS {(perm_shield_ready_at - frame) / 50:.1f}s")
    if perks:
        effects.append("Upgrades: " + " | ".join(perks))
    if boss is not None:
        effects.append(f"Boss: {boss['name']}")
        phase_str = f"Phase {boss['phase']}/{boss['max_phases']}"
        if boss["level"] == 3 and boss["phase"] == 3:
            phase_str += " [EVENT HORIZON]"
        effects.append(phase_str)
        effects.append(f"Boss HP: {max(0, int(boss['hp']))}/{boss['max_hp']}")
        if laser_phase == "warning":
            effects.append(f"BOSS LASER WARNING: {max(0, laser_until - frame) / 50:.1f}s")
        elif laser_phase == "active":
            effects.append(f"BOSS LASER ACTIVE: {max(0, laser_until - frame) / 50:.1f}s")
        if laser_h_phase == "warning":
            effects.append(f"H-LASER WARNING: {max(0, laser_h_until - frame) / 50:.1f}s")
        elif laser_h_phase == "active":
            effects.append(f"H-LASER ACTIVE: {max(0, laser_h_until - frame) / 50:.1f}s")
        if boss_guards:
            effects.append(f"Boss Escorts: {len(boss_guards)} ACTIVE")
    elif next_boss_score is not None:
        effects.append(f"Next Boss: Score {next_boss_score}")
    else:
        effects.append("ALL BOSSES DEFEATED")
    navigator_text.goto(-380, 50)
    navigator_text.write(
        "SYSTEM NAVIGATOR\n" + "\n".join(effects),
        align="left",
        font=("Consolas", 9, "normal")
    )
    if boss is not None:
        boss_bar_bg.showturtle()
        boss_bar.showturtle()
        ratio = max(0, boss["hp"] / boss["max_hp"])
        bar_width = max(0.01, 15 * ratio)
        boss_bar.shapesize(0.45, bar_width)
        boss_bar.goto(-150 + 150 * ratio, 225)
        draw_text(
            boss_text, 0, 245,
            f"{boss['name']}  |  PHASE {boss['phase']}/{boss['max_phases']}",
            align="center",
            font=("Arial", 12, "bold")
        )
    else:
        boss_bar_bg.hideturtle()
        boss_bar.hideturtle()
        boss_text.clear()
# ============================================================
# OBJECT MANAGEMENT
# ============================================================
def remove_object(obj, collection):
    if obj in collection:
        collection.remove(obj)
    obj.hideturtle()
    obj.goto(1200, 1200)
def clear_collection(collection):
    for obj in collection[:]:
        if isinstance(obj, dict):
            sprite = obj.get("sprite")
            if sprite is not None:
                sprite.hideturtle()
                sprite.goto(1200, 1200)
            bar = obj.get("bar")
            if bar is not None:
                bar.hideturtle()
                bar.goto(1200, 1200)
        else:
            obj.hideturtle()
            obj.goto(1200, 1200)
    collection.clear()
# ============================================================
# PLAYER INPUT
# ============================================================
def key_down(key):
    keys.add(key)
def key_up(key):
    keys.discard(key)
def activate_shield():
    if frame < debuff_silence_until:
        show_message("ABILITIES BLOCKED BY DEBUFF!", 180, 14, 30)
        return
    if energy > 0 and frame >= shield_overheated_until and frame >= shield_delay_until and not game_over:
        keys.add("space")
def deactivate_shield():
    global shield_delay_until, shield_was_active
    if "space" in keys or shield_was_active:
        shield_delay_until = max(shield_delay_until, frame + SHIELD_DEACTIVATE_DELAY)
        shield_was_active = False
    keys.discard("space")
def fire_mega_laser():
    if frame < debuff_silence_until:
        show_message("ABILITIES BLOCKED BY DEBUFF!", 180, 14, 30)
        return
    global player_laser_ammo, player_laser_timer, player_laser_x
    global boss, score
    if player_laser_ammo <= 0 or player_laser_timer > 0 or game_over:
        return
    player_laser_ammo -= 1
    player_laser_timer = 22
    player_laser_x = player.xcor()
    show_message("MEGA LASER BEAM FIRED! [30 DMG]", 180, 16, 50)
    half_width = PLAYER_LASER_WIDTH / 2
    for enemy in enemies[:]:
        sprite = enemy["sprite"]
        if abs(sprite.xcor() - player_laser_x) < (half_width + 18) and sprite.ycor() > player.ycor():
            enemy["hp"] = 0
    for eb in enemy_bullets[:]:
        sprite = eb["sprite"]
        if abs(sprite.xcor() - player_laser_x) < (half_width + 15) and sprite.ycor() > player.ycor():
            remove_object(sprite, [])
            if eb in enemy_bullets:
                enemy_bullets.remove(eb)
    if boss is not None:
        boss_sprite = boss["sprite"]
        if abs(boss_sprite.xcor() - player_laser_x) < (half_width + 35) and boss_sprite.ycor() > player.ycor():
            boss["hp"] -= PLAYER_LASER_DAMAGE
            if boss["hp"] <= 0:
                defeat_boss()
def fire_gravity_orb():
    if frame < debuff_silence_until:
        show_message("ABILITIES BLOCKED BY DEBUFF!", 180, 14, 30)
        return
    global gravity_orb, gravity_orb_ready_at
    if frame < gravity_orb_ready_at or gravity_orb is not None or game_over:
        return
    gravity_orb_ready_at = frame + GRAVITY_ORB_COOLDOWN
    x = player.xcor()
    y = player.ycor() + 25
    orb_sprite = make_turtle("circle", "#c084fc", x, y)
    orb_sprite.shapesize(1.25, 1.25)
    gravity_orb = {
        "sprite": orb_sprite,
        "state": "traveling",
        "x": x,
        "y": y,
        "dy": 6.8,
        "timer": GRAVITY_ORB_VORTEX_DURATION
    }
    show_message("GRAVITY ORB LAUNCHED! [K]", 180, 16, 45)
def fire_gravity_repel():
    if frame < debuff_silence_until:
        show_message("ABILITIES BLOCKED BY DEBUFF!", 180, 14, 30)
        return
    global gravity_repel_ready_at, gravity_repel_active, gravity_repel_radius
    global gravity_repel_x, gravity_repel_y, gravity_repel_pushed_enemies
    if frame < gravity_repel_ready_at or gravity_repel_active or game_over:
        return
    gravity_repel_ready_at = frame + GRAVITY_REPEL_COOLDOWN
    gravity_repel_active = True
    gravity_repel_radius = 25
    gravity_repel_x = player.xcor()
    gravity_repel_y = player.ycor()
    gravity_repel_pushed_enemies = set()
    show_message("GRAVITY REPEL SHOCKWAVE! [J]", 180, 16, 45)
screen.listen()
for key in ["w", "a", "s", "d", "Up", "Down", "Left", "Right"]:
    screen.onkeypress(lambda k=key: key_down(k), key)
    screen.onkeyrelease(lambda k=key: key_up(k), key)
screen.onkeypress(activate_shield, "space")
screen.onkeyrelease(deactivate_shield, "space")
screen.onkeypress(fire_mega_laser, "l")
screen.onkeypress(fire_mega_laser, "L")
screen.onkeypress(fire_gravity_orb, "k")
screen.onkeypress(fire_gravity_orb, "K")
screen.onkeypress(fire_gravity_repel, "j")
screen.onkeypress(fire_gravity_repel, "J")
# ============================================================
# PLAYER DAMAGE
# ============================================================
def damage_player(amount=1):
    global lives, invincible_until, perm_shield_ready_at
    if amount <= 0 or frame < invincible_until or game_over:
        return
    if perm_shield and frame >= perm_shield_ready_at:
        perm_shield_ready_at = frame + PERM_SHIELD_COOLDOWN
        invincible_until = frame + 30
        show_message("AEGIS SHIELD ABSORBED THE HIT!", 200, 14, 60)
        return
    lives -= amount
    invincible_until = frame + 55
    if lives <= 0:
        end_game()
# ============================================================
# PLAYER MOVEMENT AND SHIELD
# ============================================================
def draw_shield_ring(pen, x, y, radius, color, width):
    pen.clear()
    pen.color(color)
    pen.pensize(width)
    pen.penup()
    pen.goto(x, y - radius)
    pen.setheading(0)
    pen.pendown()
    pen.circle(radius)
    pen.penup()
def hide_shield():
    shield_visual.clear()
    shield_outer.clear()
def update_player():
    global energy, shield_overheated_until, shield_was_active, shield_delay_until
    dx = 0
    dy = 0
    
    speed_mult = 0.5 if frame < debuff_slow_until else 1.0
    actual_speed = PLAYER_SPEED * speed_mult
    
    left_pressed = ("a" in keys or "Left" in keys)
    right_pressed = ("d" in keys or "Right" in keys)
    up_pressed = ("w" in keys or "Up" in keys)
    down_pressed = ("s" in keys or "Down" in keys)
    
    if frame < debuff_reverse_until:
        if left_pressed: dx += actual_speed
        if right_pressed: dx -= actual_speed
        if up_pressed: dy -= actual_speed
        if down_pressed: dy += actual_speed
    else:
        if left_pressed: dx -= actual_speed
        if right_pressed: dx += actual_speed
        if up_pressed: dy += actual_speed
        if down_pressed: dy -= actual_speed

    if boss is not None and boss["level"] == 3 and boss["phase"] == 3:
        boss_x = boss["sprite"].xcor()
        dx += (boss_x - player.xcor()) * 0.02
        dy += 0.8
    player.goto(
        max(-370, min(370, player.xcor() + dx)),
        max(-315, min(180, player.ycor() + dy))
    )
    shield_allowed = (frame >= shield_overheated_until and frame >= shield_delay_until)
    shield_on = ("space" in keys and energy > 0 and shield_allowed)
    if shield_on:
        shield_was_active = True
        energy = max(0, energy - SHIELD_DRAIN)
        pulse = 48 + 4 * math.sin(frame * 0.35)
        draw_shield_ring(
            shield_visual, player.xcor(), player.ycor(),
            pulse, "#00ffff", 4
        )
        draw_shield_ring(
            shield_outer, player.xcor(), player.ycor(),
            pulse + 8, "#ffffff", 2
        )
        if energy <= 0:
            shield_overheated_until = frame + SHIELD_OVERHEAT_FRAMES
            shield_was_active = False
            keys.discard("space")
            hide_shield()
            show_message("SHIELD OVERHEATED! COOLDOWN 5 SECONDS", 200, 14, 80)
            shield_on = False
    else:
        if shield_was_active:
            shield_delay_until = max(shield_delay_until, frame + SHIELD_DEACTIVATE_DELAY)
            shield_was_active = False
        energy = min(max_energy, energy + SHIELD_REGEN)
        hide_shield()
    if perm_shield and frame >= perm_shield_ready_at and not shield_on:
        draw_shield_ring(
            aegis_visual, player.xcor(), player.ycor(),
            34, "#7dff9b", 2
        )
    else:
        aegis_visual.clear()
    if frame < invincible_until:
        player.color("#ffffff" if frame % 8 < 4 else "#48e5ff")
    else:
        player.color("#48e5ff")
    return shield_on
# ============================================================
# WINGMAN PARTNER & MEGA LASER BEAM
# ============================================================
def update_partner():
    if frame >= partner_until:
        partner_turtle.hideturtle()
        partner_turtle.goto(1200, 1200)
        return
    partner_turtle.showturtle()
    target_x = player.xcor() + 38 * math.cos(frame * 0.08)
    target_y = player.ycor() - 5 + 8 * math.sin(frame * 0.1)
    partner_turtle.goto(target_x, target_y)
    if frame % PARTNER_FIRE_INTERVAL == 0 and frame >= overheat_until:
        fire_bullet(partner_turtle.xcor(), partner_turtle.ycor() + 15, damage=get_player_damage())
        if perm_dual:
            fire_bullet(partner_turtle.xcor() + 8, partner_turtle.ycor() + 15, damage=get_player_damage())
        if frame < triple_shot_until:
            fire_bullet(partner_turtle.xcor() - 10, partner_turtle.ycor() + 15, dx=-1.5, damage=get_player_damage())
            fire_bullet(partner_turtle.xcor() + 10, partner_turtle.ycor() + 15, dx=1.5, damage=get_player_damage())
def update_player_mega_laser():
    global player_laser_timer, player_laser_drawer
    if player_laser_timer <= 0:
        player_laser_drawer.clear()
        return
    player_laser_timer -= 1
    player_laser_drawer.clear()
    start_y = player.ycor() + 20
    end_y = HEIGHT / 2 + 50
    cx = player_laser_x
    player_laser_drawer.pensize(PLAYER_LASER_WIDTH)
    player_laser_drawer.color("#00e5ff")
    player_laser_drawer.penup()
    player_laser_drawer.goto(cx, start_y)
    player_laser_drawer.pendown()
    player_laser_drawer.goto(cx, end_y)
    player_laser_drawer.penup()
    player_laser_drawer.pensize(PLAYER_LASER_WIDTH * 0.45)
    player_laser_drawer.color("#ffffff")
    player_laser_drawer.goto(cx, start_y)
    player_laser_drawer.pendown()
    player_laser_drawer.goto(cx, end_y)
    player_laser_drawer.penup()
    half_width = PLAYER_LASER_WIDTH / 2
    for enemy in enemies[:]:
        sprite = enemy["sprite"]
        if abs(sprite.xcor() - cx) < (half_width + 16) and sprite.ycor() > start_y - 20:
            enemy["hp"] = 0
    for eb in enemy_bullets[:]:
        sprite = eb["sprite"]
        if abs(sprite.xcor() - cx) < (half_width + 12) and sprite.ycor() > start_y - 20:
            remove_object(sprite, [])
            if eb in enemy_bullets:
                enemy_bullets.remove(eb)
def update_gravity_orb():
    global gravity_orb, gravity_explosion_timer, gravity_explosion_pos, score
    if gravity_explosion_timer > 0:
        gravity_explosion_timer -= 1
        gravity_vortex_pen.clear()
        ex_x, ex_y = gravity_explosion_pos
        radius = (12 - gravity_explosion_timer) * 16
        gravity_vortex_pen.penup()
        gravity_vortex_pen.goto(ex_x, ex_y - radius)
        gravity_vortex_pen.pendown()
        gravity_vortex_pen.color("#d946ef" if gravity_explosion_timer % 2 == 0 else "#ffffff")
        gravity_vortex_pen.pensize(5)
        gravity_vortex_pen.circle(radius)
        gravity_vortex_pen.penup()
        if gravity_explosion_timer == 0:
            gravity_vortex_pen.clear()
    if gravity_orb is None:
        return
    sprite = gravity_orb["sprite"]
    if gravity_orb["state"] == "traveling":
        gravity_orb["y"] += gravity_orb["dy"]
        sprite.goto(gravity_orb["x"], gravity_orb["y"])
        pulse = 1.15 + 0.25 * math.sin(frame * 0.5)
        sprite.shapesize(pulse, pulse)
        hit = False
        target_x, target_y = gravity_orb["x"], gravity_orb["y"]
        for enemy in enemies:
            if sprite.distance(enemy["sprite"]) < 32:
                hit = True
                target_x, target_y = enemy["sprite"].xcor(), enemy["sprite"].ycor()
                enemy["hp"] -= 5
                break
        if not hit and boss is not None:
            if sprite.distance(boss["sprite"]) < 45:
                hit = True
                target_x, target_y = boss["sprite"].xcor(), boss["sprite"].ycor()
                boss["hp"] -= 5
                if boss["hp"] <= 0:
                    defeat_boss()
        if hit or gravity_orb["y"] > 290:
            gravity_orb["state"] = "vortex"
            gravity_orb["x"] = target_x
            gravity_orb["y"] = min(280, target_y)
            gravity_orb["timer"] = GRAVITY_ORB_VORTEX_DURATION
            sprite.color("#38bdf8")
            show_message("GRAVITATIONAL VORTEX ENGAGED! (4s)", 180, 16, 50)
    elif gravity_orb["state"] == "vortex":
        gravity_orb["timer"] -= 1
        ox = gravity_orb["x"]
        oy = gravity_orb["y"]
        sprite.goto(ox, oy)
        pulse = 1.45 + 0.3 * math.sin(frame * 0.8)
        sprite.shapesize(pulse, pulse)
        sprite.color("#06b6d4" if frame % 6 < 3 else "#a855f7")
        gravity_vortex_pen.clear()
        for i in [1, 2]:
            ring_r = ((frame * 4 + i * 80) % GRAVITY_ORB_PULL_RADIUS)
            gravity_vortex_pen.penup()
            gravity_vortex_pen.goto(ox, oy - ring_r)
            gravity_vortex_pen.pendown()
            gravity_vortex_pen.pensize(2)
            gravity_vortex_pen.color("#818cf8" if i == 1 else "#38bdf8")
            gravity_vortex_pen.circle(ring_r)
            gravity_vortex_pen.penup()
        for enemy in enemies:
            ex = enemy["sprite"].xcor()
            ey = enemy["sprite"].ycor()
            dist = math.hypot(ox - ex, oy - ey)
            if dist < GRAVITY_ORB_PULL_RADIUS:
                pull_speed = 3.8
                dx = (ox - ex) / max(1, dist) * pull_speed
                dy = (oy - ey) / max(1, dist) * pull_speed
                enemy["sprite"].goto(ex + dx, ey + dy)
                enemy["bar"].goto(enemy["sprite"].xcor(), enemy["sprite"].ycor() - 15)
        if boss is not None:
            bx = boss["sprite"].xcor()
            by = boss["sprite"].ycor()
            dist_b = math.hypot(ox - bx, oy - by)
            if dist_b < GRAVITY_ORB_PULL_RADIUS:
                boss["sprite"].setx(bx + (ox - bx) * 0.018)
        for eb in enemy_bullets[:]:
            eb_s = eb["sprite"]
            eb_dist = math.hypot(ox - eb_s.xcor(), oy - eb_s.ycor())
            if eb_dist < GRAVITY_ORB_PULL_RADIUS:
                pull_eb = 5.8
                dx = (ox - eb_s.xcor()) / max(1, eb_dist) * pull_eb
                dy = (oy - eb_s.ycor()) / max(1, eb_dist) * pull_eb
                eb_s.goto(eb_s.xcor() + dx, eb_s.ycor() + dy)
                if eb_dist < 28:
                    remove_object(eb_s, [])
                    if eb in enemy_bullets:
                        enemy_bullets.remove(eb)
        if gravity_orb["timer"] <= 0:
            gravity_vortex_pen.clear()
            gravity_explosion_timer = 12
            gravity_explosion_pos = (ox, oy)
            show_message("★ GRAVITY SUPERNOVA DETONATION! ★", 180, 17, 60)
            explode_radius = GRAVITY_ORB_PULL_RADIUS
            for enemy in enemies:
                dist = math.hypot(ox - enemy["sprite"].xcor(), oy - enemy["sprite"].ycor())
                if dist < explode_radius:
                    enemy["hp"] -= GRAVITY_ORB_EXPLODE_DAMAGE
            for eb in enemy_bullets[:]:
                dist = math.hypot(ox - eb["sprite"].xcor(), oy - eb["sprite"].ycor())
                if dist < explode_radius:
                    remove_object(eb["sprite"], [])
                    if eb in enemy_bullets:
                        enemy_bullets.remove(eb)
            if boss is not None:
                dist_b = math.hypot(ox - boss["sprite"].xcor(), oy - boss["sprite"].ycor())
                if dist_b < explode_radius + 35:
                    boss["hp"] -= GRAVITY_ORB_EXPLODE_DAMAGE
                    if boss["hp"] <= 0:
                        defeat_boss()
            remove_object(sprite, [])
            gravity_orb = None
def update_gravity_repel():
    global gravity_repel_active, gravity_repel_radius, gravity_repel_pen
    global gravity_repel_pushed_enemies, score
    if not gravity_repel_active:
        gravity_repel_pen.clear()
        return
    gravity_repel_radius += GRAVITY_REPEL_SPEED
    ox, oy = gravity_repel_x, gravity_repel_y
    gravity_repel_pen.clear()
    gravity_repel_pen.penup()
    for offset_r, color, pen_size in [
        (0, "#00ffff", 5),
        (22, "#a855f7", 3),
        (44, "#ffffff", 2)
    ]:
        r = gravity_repel_radius - offset_r
        if r > 5:
            gravity_repel_pen.goto(ox, oy - r)
            gravity_repel_pen.pendown()
            gravity_repel_pen.color(color)
            gravity_repel_pen.pensize(pen_size)
            gravity_repel_pen.circle(r)
            gravity_repel_pen.penup()
    for enemy in enemies:
        ex = enemy["sprite"].xcor()
        ey = enemy["sprite"].ycor()
        dist = math.hypot(ex - ox, ey - oy)
        eid = id(enemy)
        if dist <= gravity_repel_radius + 25 and eid not in gravity_repel_pushed_enemies:
            gravity_repel_pushed_enemies.add(eid)
            push_force = 50
            vx = (ex - ox) / max(1, dist)
            vy = (ey - oy) / max(1, dist)
            new_x = max(-355, min(355, ex + vx * push_force))
            new_y = max(-260, min(340, ey + vy * push_force + 20))
            enemy["sprite"].goto(new_x, new_y)
            enemy["bar"].goto(new_x, new_y - 15)
            enemy["hp"] -= 8
    for guard in boss_guards:
        gx = guard["sprite"].xcor()
        gy = guard["sprite"].ycor()
        dist_g = math.hypot(gx - ox, gy - oy)
        gid = id(guard)
        if dist_g <= gravity_repel_radius + 25 and gid not in gravity_repel_pushed_enemies:
            gravity_repel_pushed_enemies.add(gid)
            guard["hp"] -= 12
    for eb in enemy_bullets[:]:
        bx = eb["sprite"].xcor()
        by = eb["sprite"].ycor()
        dist_b = math.hypot(bx - ox, by - oy)
        if dist_b <= gravity_repel_radius + 20:
            vx = (bx - ox) / max(1, dist_b)
            vy = (by - oy) / max(1, dist_b)
            eb["dx"] = vx * 9.0
            eb["dy"] = max(4.0, vy * 9.0)
            eb["damage"] = 0
            eb["sprite"].color("#67e8f9")
    if boss is not None:
        bx = boss["sprite"].xcor()
        by = boss["sprite"].ycor()
        dist_boss = math.hypot(bx - ox, by - oy)
        if dist_boss <= gravity_repel_radius + 35 and "boss" not in gravity_repel_pushed_enemies:
            gravity_repel_pushed_enemies.add("boss")
            boss["hp"] -= 10
            if boss["hp"] <= 0:
                defeat_boss()
    if gravity_repel_radius >= GRAVITY_REPEL_MAX_RADIUS:
        gravity_repel_active = False
        gravity_repel_pen.clear()
# ============================================================
# AUTOMATIC WEAPON
# ============================================================
def fire_bullet(x, y, dx=0, damage=1.0):
    bullet = make_turtle("square", "#ffe66d", x, y)
    bullet.shapesize(0.65, 0.25)
    bullets.append({
        "sprite": bullet,
        "dx": dx,
        "dy": BULLET_SPEED,
        "damage": damage
    })
def update_player_weapon():
    if frame < overheat_until:
        return
    interval = (
        FIRE_INTERVAL_UPGRADED if perm_fire_rate
        else FIRE_INTERVAL_BASE
    )
    if frame % interval != 0:
        return
    x = player.xcor()
    y = player.ycor() + 18
    dmg = get_player_damage()
    lanes = [-9, 9] if perm_dual else [0]
    for offset in lanes:
        fire_bullet(x + offset, y, damage=dmg)
    if frame < triple_shot_until:
        side = 20 if perm_dual else 10
        fire_bullet(x - side, y, -1.5, damage=dmg)
        fire_bullet(x + side, y, 1.5, damage=dmg)
def update_player_bullets():
    for bullet in bullets[:]:
        sprite = bullet["sprite"]
        sprite.goto(
            sprite.xcor() + bullet["dx"],
            sprite.ycor() + bullet["dy"]
        )
        if sprite.ycor() > HEIGHT / 2 + 30:
            if bullet in bullets:
                bullets.remove(bullet)
            sprite.hideturtle()
            sprite.goto(1200, 1200)
# ============================================================
# ENEMY SPAWNING (DENGAN HP YANG DIKURANGI/SEIMBANG)
# ============================================================
def spawn_enemy(during_boss=False):
    if game_over:
        return
    if boss is not None and not during_boss:
        return
    if boss is None and len(enemies) >= 8:
        return
    if boss is not None and len(enemies) >= BOSS_ENEMY_CAP:
        return
    difficulty = score // 100
    
    # Penskalan HP musuh dikurangi agar tidak terlalu tebal
    level_scaling = 1.0 + (player_level - 1) * 0.15
    
    kind = random.choice(["drone", "drone", "asteroid"])
    if kind == "drone":
        color = "#ff5263"
        shape = "triangle"
        hp = int(min(8, 2 + difficulty // 2) * level_scaling)
        speed = random.uniform(1.7, 2.6) + difficulty * 0.12
    else:
        color = "#b08cff"
        shape = "circle"
        hp = int(min(6, 1 + difficulty // 3) * level_scaling)
        speed = random.uniform(1.2, 2.0) + difficulty * 0.10
    
    hp = max(hp, 1)
    sprite = make_turtle(
        shape, color, random.randint(-350, 350), 345
    )
    sprite.shapesize(
        random.uniform(0.9, 1.3),
        random.uniform(0.9, 1.3)
    )
    bar = make_turtle(
        "square", "#54f28b",
        sprite.xcor(), sprite.ycor() - 15
    )
    bar.shapesize(0.15, 1.5)
    enemies.append({
        "sprite": sprite,
        "bar": bar,
        "hp": hp,
        "max_hp": hp,
        "speed": speed,
        "kind": kind,
        "phase": random.uniform(0, math.tau),
        "fire_cooldown": random.randint(70, 150)
    })
def spawn_enemy_bullet(x, y, target_x=None, target_y=None,
                       speed=4.0, color="#ff805f", bullet_type="normal"):
    sprite = make_turtle("circle", color, x, y)
    sprite.shapesize(0.45, 0.45)
    if target_x is None or target_y is None:
        dx = 0
        dy = -speed
    else:
        vx = target_x - x
        vy = target_y - y
        length = max(1, math.hypot(vx, vy))
        dx = vx / length * speed
        dy = vy / length * speed
    enemy_bullets.append({
        "sprite": sprite,
        "dx": dx,
        "dy": dy,
        "damage": 1,
        "type": bullet_type,
        "life": 0
    })
def update_enemies(shield_on):
    global score
    for enemy in enemies[:]:
        sprite = enemy["sprite"]
        bar = enemy["bar"]
        enemy["phase"] += 0.045
        drift = math.sin(enemy["phase"]) * 1.5
        speed = enemy["speed"]
        distance = sprite.distance(player)
        if shield_on and distance < 105:
            vx = sprite.xcor() - player.xcor()
            vy = sprite.ycor() - player.ycor()
            length = max(1, math.hypot(vx, vy))
            sprite.goto(
                sprite.xcor() + vx / length * 3,
                sprite.ycor() + vy / length * 3 - speed * 0.4
            )
        else:
            sprite.goto(
                sprite.xcor() + drift,
                sprite.ycor() - speed
            )
        bar.goto(sprite.xcor(), sprite.ycor() - 15)
        ratio = enemy["hp"] / enemy["max_hp"]
        bar.shapesize(0.15, max(0.05, 1.5 * ratio))
        if enemy["kind"] == "drone":
            enemy["fire_cooldown"] -= 1
            if enemy["fire_cooldown"] <= 0 and sprite.ycor() < 260:
                b_type = random.choices(["normal", "slow", "silence", "reverse"], weights=[5, 2, 2, 1], k=1)[0]
                color_map = {"normal": "#ff7b92", "slow": "#38bdf8", "silence": "#c084fc", "reverse": "#f43f5e"}
                spawn_enemy_bullet(
                    sprite.xcor(), sprite.ycor() - 12,
                    player.xcor(), player.ycor(),
                    speed=3.2 + min(2, score / 500),
                    color=color_map[b_type],
                    bullet_type=b_type
                )
                enemy["fire_cooldown"] = random.randint(100, 180)
        if sprite.distance(player) < 23:
            if shield_on:
                enemy["hp"] = 0
            else:
                damage_player()
                enemy["hp"] = 0
        
        # PERBAIKAN: Jika musuh melewati batas bawah layar, hapus TANPA menambah skor/XP
        if sprite.ycor() < -350:
            remove_object(sprite, [])
            bar.hideturtle()
            bar.goto(1200, 1200)
            if enemy in enemies:
                enemies.remove(enemy)
            continue
            
        if enemy["hp"] <= 0:
            score += 10
            xp_reward = 25 if enemy["kind"] == "drone" else 35
            add_player_xp(xp_reward)
            drop_chance = (
                BOSS_DROP_CHANCE if boss is not None
                else ENEMY_DROP_CHANCE
            )
            if random.random() < drop_chance:
                spawn_powerup(sprite.xcor(), sprite.ycor())
            remove_object(sprite, [])
            bar.hideturtle()
            bar.goto(1200, 1200)
            if enemy in enemies:
                enemies.remove(enemy)
# ============================================================
# GACHA POWER-UPS (TEMPORARY + PARTNER & LASER) - NO STACKING
# ============================================================
def spawn_powerup(x, y, boss_reward=False):
    sprite = make_turtle("square", "#ffe66d", x, y)
    sprite.shapesize(0.85, 0.85)
    if boss_reward:
        kind = random.choice(["triple", "energy", "health", "partner", "laser"])
    else:
        kind = random.choices(
            ["triple", "energy", "health", "partner", "laser", "overheat", "drain"],
            weights=[3, 3, 2, 2, 2, 1, 1],
            k=1
        )[0]
    sprite.color("#ffe66d")
    sprite.shape("square")
    sprite.shapesize(0.85, 0.85)
    powerups.append({
        "sprite": sprite,
        "kind": kind,
        "boss_reward": boss_reward
    })
def apply_powerup(powerup):
    global energy, lives, triple_shot_until, overheat_until
    global partner_until, player_laser_ammo
    kind = powerup["kind"]
    if kind == "triple":
        triple_shot_until = frame + 500
        message = "TRIPLE SHOT ACTIVATED!"
    elif kind == "energy":
        energy = min(max_energy, energy + SHIELD_GACHA_REWARD)
        message = "SHIELD ENERGY RESTORED!"
    elif kind == "health":
        if lives < 3:
            lives += 1
            message = "HEALTH RESTORED! +1 HP"
        else:
            energy = min(max_energy, energy + 20)
            message = "HP FULL! BONUS SHIELD ENERGY +20"
    elif kind == "partner":
        partner_until = frame + PARTNER_DURATION
        message = "WINGMAN PARTNER DEPLOYED! (30s)"
    elif kind == "laser":
        if player_laser_ammo < MAX_LASER_AMMO:
            player_laser_ammo += 1
            message = f"MEGA LASER ACQUIRED! [{player_laser_ammo}/{MAX_LASER_AMMO}] (PRESS 'L')"
        else:
            score += 50
            message = "MAX MEGA LASER! BONUS +50 SCORE"
    elif kind == "overheat":
        overheat_until = frame + 180
        message = "WEAPON OVERHEATED!"
    else:
        energy = max(0, energy - 30)
        message = "ENERGY DRAINED!"
    show_message(message, 200, 15, 70)
def update_powerups():
    for powerup in powerups[:]:
        sprite = powerup["sprite"]
        sprite.setheading(sprite.heading() + 5)
        sprite.sety(sprite.ycor() - 2.2)
        if sprite.distance(player) < 25:
            apply_powerup(powerup)
            remove_object(sprite, [])
            powerups.remove(powerup)
        elif sprite.ycor() < -350:
            remove_object(sprite, [])
            powerups.remove(powerup)
# ============================================================
# PERMANENT UPGRADES (BOSS REWARD)
# ============================================================
def grant_permanent_upgrade():
    global perm_dual, perm_fire_rate, perm_shield, perm_shield_ready_at
    options = []
    if not perm_dual:
        options.append("dual")
    if not perm_fire_rate:
        options.append("fire_rate")
    if not perm_shield:
        options.append("shield")
    if not options:
        return None
    choice = random.choice(options)
    if choice == "dual":
        perm_dual = True
        return "DUAL SHOT"
    if choice == "fire_rate":
        perm_fire_rate = True
        return "RAPID FIRE"
    perm_shield = True
    perm_shield_ready_at = frame
    return "AEGIS SHIELD (10s cooldown)"
# ============================================================
# ENEMY BULLETS
# ============================================================
def update_enemy_bullets(shield_on):
    global debuff_slow_until, debuff_silence_until, debuff_reverse_until
    for bullet in enemy_bullets[:]:
        sprite = bullet["sprite"]
        bullet["life"] = bullet.get("life", 0) + 1
        if bullet.get("type") == "homing" and bullet["life"] < 70:
            target_x = player.xcor()
            dx = (target_x - sprite.xcor()) * 0.04
            sprite.goto(
                sprite.xcor() + dx,
                sprite.ycor() + bullet["dy"]
            )
        else:
            sprite.goto(
                sprite.xcor() + bullet["dx"],
                sprite.ycor() + bullet["dy"]
            )
        if shield_on and sprite.distance(player) < 60:
            sprite.hideturtle()
            sprite.goto(1200, 1200)
            enemy_bullets.remove(bullet)
            continue
        if sprite.distance(player) < 17:
            b_type = bullet.get("type", "normal")
            if b_type == "slow":
                debuff_slow_until = frame + 500
                show_message("DEBUFF: MOVEMENT SLOWED! (10s)", 190, 15, 60)
            elif b_type == "silence":
                debuff_silence_until = frame + 500
                show_message("DEBUFF: ABILITIES BLOCKED! (10s)", 190, 15, 60)
            elif b_type == "reverse":
                debuff_reverse_until = frame + 250
                show_message("DEBUFF: CONTROLS REVERSED! (5s)", 190, 15, 60)

            damage_player(bullet["damage"])
            sprite.hideturtle()
            sprite.goto(1200, 1200)
            enemy_bullets.remove(bullet)
            continue
        if (
            abs(sprite.xcor()) > WIDTH / 2 + 40
            or abs(sprite.ycor()) > HEIGHT / 2 + 40
        ):
            sprite.hideturtle()
            sprite.goto(1200, 1200)
            enemy_bullets.remove(bullet)
# ============================================================
# BOSS SYSTEM
# ============================================================
def spawn_boss():
    global boss, boss_level, next_boss_score
    global laser_phase, laser_until, laser_x
    global laser_warning, laser_beam
    if boss_level >= 3:
        return
    boss_level += 1
    level = boss_level
    boss_data = {
        1: {"hp": 350, "color": "#ff304f", "speed": 2.2, "max_phases": 2},
        2: {"hp": 650, "color": "#b05cff", "speed": 2.6, "max_phases": 2},
        3: {"hp": 1200, "color": "#38bfff", "speed": 2.8, "max_phases": 3}
    }
    data = boss_data[level]
    sprite = make_turtle("turtle", data["color"], 0, 260)
    size = 2.8 if level == 3 else 2.3
    sprite.shapesize(size, size)
    sprite.setheading(270)
    boss = {
        "sprite": sprite,
        "level": level,
        "name": BOSS_NAMES[level],
        "hp": data["hp"],
        "max_hp": data["hp"],
        "speed": data["speed"],
        "base_speed": data["speed"],
        "direction": 1,
        "phase": 1,
        "max_phases": data["max_phases"],
        "attack_cooldown": 65,
        "laser_cooldown": 180,
        "special_cooldown": 140,
        "h_laser_cooldown": 140 if level == 3 else 9999,
        "missile_cooldown": 90 if level == 3 else 9999,
        "move_phase": 0
    }
    next_boss_score = (
        BOSS_THRESHOLDS[level]
        if level < 3
        else None
    )
    laser_phase = "idle"
    laser_until = 0
    laser_x = 0
    hide_laser_objects()
    laser_h_phase = "idle"
    laser_h_until = 0
    hide_horizontal_laser_objects()
    if level == 3:
        spawn_boss_guards()
    boss_bar_bg.showturtle()
    boss_bar.showturtle()
    show_message(
        f"WARNING: {BOSS_NAMES[level]} INCOMING!", 190, 18, 100
    )
def spawn_boss_missile(x, y, speed=9.5, color="#ff2a55"):
    sprite = make_turtle("triangle", color, x, y)
    sprite.shapesize(0.85, 0.45)
    sprite.setheading(270)
    enemy_bullets.append({
        "sprite": sprite,
        "dx": 0,
        "dy": -speed,
        "damage": 1,
        "type": "fast_missile",
        "life": 0
    })
def clear_boss_guards():
    for guard in boss_guards[:]:
        guard["sprite"].hideturtle()
        guard["sprite"].goto(1200, 1200)
        guard["bar"].hideturtle()
        guard["bar"].goto(1200, 1200)
    boss_guards.clear()
def spawn_boss_guards():
    clear_boss_guards()
    for idx, (offset_x, offset_y, name) in enumerate([
        (-95, -15, "GUARD ALPHA"),
        (95, -15, "GUARD BETA")
    ]):
        sprite = make_turtle("triangle", "#a855f7", 0, 300)
        sprite.shapesize(1.15, 1.15)
        sprite.setheading(270)
        bar = make_turtle("square", "#06b6d4", 0, 300)
        bar.shapesize(0.12, 1.3)
        boss_guards.append({
            "name": name,
            "sprite": sprite,
            "bar": bar,
            "hp": 75,
            "max_hp": 75,
            "offset_x": offset_x,
            "offset_y": offset_y,
            "fire_cooldown": 75 + idx * 40,
            "phase": idx * math.pi
        })
def update_boss_guards():
    global score
    if not boss_guards:
        return
    for guard in boss_guards[:]:
        if boss is None:
            guard["sprite"].hideturtle()
            guard["sprite"].goto(1200, 1200)
            guard["bar"].hideturtle()
            guard["bar"].goto(1200, 1200)
            boss_guards.remove(guard)
            continue
        boss_sprite = boss["sprite"]
        guard["phase"] += 0.05
        gx = boss_sprite.xcor() + guard["offset_x"] + 12 * math.sin(guard["phase"])
        gy = boss_sprite.ycor() + guard["offset_y"] + 6 * math.cos(guard["phase"])
        guard["sprite"].goto(gx, gy)
        guard["bar"].goto(gx, gy - 16)
        ratio = max(0.01, guard["hp"] / guard["max_hp"])
        guard["bar"].shapesize(0.12, 1.3 * ratio)
        guard["fire_cooldown"] -= 1
        if guard["fire_cooldown"] <= 0:
            spawn_enemy_bullet(
                gx, gy - 12,
                player.xcor(), player.ycor(),
                speed=3.8, color="#c084fc"
            )
            guard["fire_cooldown"] = random.randint(85, 130)
        if guard["hp"] <= 0:
            score += 150
            add_player_xp(100)
            guard["sprite"].hideturtle()
            guard["sprite"].goto(1200, 1200)
            guard["bar"].hideturtle()
            guard["bar"].goto(1200, 1200)
            show_message(f"{guard['name']} DESTROYED! +150", 190, 15, 60)
            if guard in boss_guards:
                boss_guards.remove(guard)
def spawn_boss_projectile(x, y, angle, speed, color, bullet_type="normal"):
    radians = math.radians(angle)
    dx = math.sin(radians) * speed
    dy = -math.cos(radians) * speed
    sprite = make_turtle("circle", color, x, y)
    sprite.shapesize(0.5, 0.5)
    enemy_bullets.append({
        "sprite": sprite,
        "dx": dx,
        "dy": dy,
        "damage": 1,
        "type": bullet_type,
        "life": 0
    })
def fire_boss_volley():
    if boss is None:
        return
    sprite = boss["sprite"]
    level = boss["level"]
    phase = boss["phase"]
    x = sprite.xcor()
    y = sprite.ycor() - 25
    speed = 3.5 + level * 0.35 + phase * 0.4
    if level == 1:
        spread = [-30, 0, 30] if phase == 1 else [-45, -20, 0, 20, 45]
        for offset in spread:
            spawn_enemy_bullet(
                x, y,
                player.xcor() + offset,
                player.ycor(),
                speed=speed,
                color="#ff5277" if phase == 1 else "#ff1744"
            )
    elif level == 2:
        angles = [-45, -30, -15, 0, 15, 30, 45] if phase == 1 else [-60, -45, -30, -15, 0, 15, 30, 45, 60]
        for angle in angles:
            spawn_boss_projectile(
                x, y, angle, speed + 0.2, "#c26bff" if phase == 1 else "#e040fb"
            )
        if frame % 2 == 0:
            spawn_enemy_bullet(
                x, y, player.xcor(), player.ycor(),
                speed=speed + 0.8,
                color="#ff75d8"
            )
    elif level == 3:
        if phase == 1:
            for angle in [-24, 0, 24]:
                spawn_boss_projectile(x, y, angle, speed + 0.2, "#42d9ff")
        elif phase == 2:
            for angle in [-32, -16, 0, 16, 32]:
                spawn_boss_projectile(x, y, angle, speed + 0.4, "#ff9100")
        else:
            for angle in [-36, -18, 0, 18, 36]:
                spawn_boss_projectile(x, y, angle, speed + 0.6, "#ff0055")
            spawn_enemy_bullet(x, y, player.ycor(), player.ycor(), speed=speed + 1.2, color="#ffe66d")
def trigger_boss_special_attack():
    if boss is None:
        return
    level = boss["level"]
    phase = boss["phase"]
    sprite = boss["sprite"]
    x = sprite.xcor()
    y = sprite.ycor() - 20
    if level == 1:
        show_message("STRIKER: HOMING MISSILE SALVO!", 190, 16, 45)
        for offset_x in [-25, 0, 25]:
            sprite_m = make_turtle("triangle", "#ff9100", x + offset_x, y)
            sprite_m.shapesize(0.55, 0.55)
            sprite_m.setheading(270)
            enemy_bullets.append({
                "sprite": sprite_m,
                "dx": 0,
                "dy": -2.8,
                "damage": 1,
                "type": "homing",
                "life": 0
            })
    elif level == 2:
        show_message("PHANTOM: VOID SPIRAL!", 190, 16, 45)
        if phase == 2:
            sprite.setx(random.randint(-300, 300))
        num_bullets = 14
        for i in range(num_bullets):
            angle = (360 / num_bullets) * i
            spawn_boss_projectile(x, y, angle, 3.2, "#d500f9")
    elif level == 3:
        if phase == 3:
            show_message("SINGULARITY: EVENT HORIZON BURST!", 190, 16, 45)
            for i in range(8):
                angle = 45 * i
                spawn_boss_projectile(x, y, angle, 4.0, "#ff1744")
            spawn_boss_missile(x - 50, y, speed=9.5)
            spawn_boss_missile(x + 50, y, speed=9.5)
        else:
            show_message("SINGULARITY: DUAL MISSILE STRIKE!", 190, 16, 40)
            for angle in [-25, 0, 25]:
                spawn_boss_projectile(x, y, angle, 4.2, "#00e5ff")
            spawn_boss_missile(x - 40, y, speed=9.0)
            spawn_boss_missile(x + 40, y, speed=9.0)
# ============================================================
# BOSS LASER
# ============================================================
def hide_laser_objects():
    global laser_warning, laser_beam
    if laser_warning is not None:
        laser_warning.hideturtle()
        laser_warning.goto(1200, 1200)
    if laser_beam is not None:
        laser_beam.hideturtle()
        laser_beam.goto(1200, 1200)
def start_boss_laser():
    global laser_phase, laser_until, laser_x
    global laser_warning, laser_beam
    global laser_width, laser_damage
    if boss is None:
        return
    laser_x = player.xcor()
    level = boss["level"]
    phase = boss["phase"]
    if level == 3 and phase == 3:
        laser_width = 135
        warn_time = 25
        active_time = 40
    elif phase >= 2:
        laser_width = 110
        warn_time = 32
        active_time = 34
    else:
        laser_width = 85
        warn_time = 45
        active_time = 30
    laser_damage = 1
    laser_phase = "warning"
    laser_until = frame + warn_time
    hide_laser_objects()
    laser_warning = make_turtle(
        "square", "#ffe66d", laser_x, -35
    )
    laser_warning.shapesize(
        0.12, max(0.1, laser_width / 20)
    )
    show_message(f"WARNING: {boss['name']} LASER SIGHT!", 190, 17, 35)
def update_boss_laser():
    global laser_phase, laser_until, laser_beam
    if boss is None:
        if laser_phase != "idle":
            hide_laser_objects()
            laser_phase = "idle"
            laser_until = 0
        return
    if laser_phase == "idle":
        return
    if laser_phase == "warning":
        if laser_warning is not None:
            laser_warning.goto(laser_x, -35)
        if frame >= laser_until:
            if laser_warning is not None:
                laser_warning.hideturtle()
                laser_warning.goto(1200, 1200)
            laser_beam = make_turtle(
                "square", "#ff263f", laser_x, -35
            )
            laser_beam.shapesize(
                18, max(0.1, laser_width / 20)
            )
            laser_phase = "active"
            laser_until = frame + (38 if boss["phase"] >= 2 else 30)
        return
    if laser_phase == "active":
        if laser_beam is not None:
            laser_beam.goto(laser_x, -35)
        if (
            abs(player.xcor() - laser_x) < laser_width / 2 + 12
            and -330 < player.ycor() < 300
        ):
            if "space" not in keys or energy <= 0 or frame < shield_overheated_until or frame < shield_delay_until:
                damage_player(laser_damage)
        if frame >= laser_until:
            hide_laser_objects()
            laser_phase = "idle"
            laser_until = 0
# ============================================================
# BOSS HORIZONTAL LASER (KHUSUS SINGULARITY)
# ============================================================
def hide_horizontal_laser_objects():
    global laser_h_warning, laser_h_beam
    if laser_h_warning is not None:
        laser_h_warning.hideturtle()
        laser_h_warning.goto(1200, 1200)
    if laser_h_beam is not None:
        laser_h_beam.hideturtle()
        laser_h_beam.goto(1200, 1200)
def start_boss_horizontal_laser():
    global laser_h_phase, laser_h_until, laser_h_y
    global laser_h_warning, laser_h_beam, laser_h_height
    if boss is None or boss["level"] != 3:
        return
    laser_h_y = max(-260, min(140, player.ycor()))
    laser_h_height = 70 if boss["phase"] < 3 else 90
    laser_h_phase = "warning"
    laser_h_until = frame + 35
    hide_horizontal_laser_objects()
    laser_h_warning = make_turtle("square", "#ffe66d", 0, laser_h_y)
    laser_h_warning.shapesize(0.12, 42)
    show_message("WARNING: HORIZONTAL LASER SIGHT!", 190, 17, 35)
def update_boss_horizontal_laser():
    global laser_h_phase, laser_h_until, laser_h_beam
    if boss is None or boss["level"] != 3:
        if laser_h_phase != "idle":
            hide_horizontal_laser_objects()
            laser_h_phase = "idle"
            laser_h_until = 0
        return
    if laser_h_phase == "idle":
        return
    if laser_h_phase == "warning":
        if frame >= laser_h_until:
            if laser_h_warning is not None:
                laser_h_warning.hideturtle()
                laser_h_warning.goto(1200, 1200)
            laser_h_beam = make_turtle("square", "#c026d3", 0, laser_h_y)
            laser_h_beam.shapesize(max(0.1, laser_h_height / 20), 42)
            laser_h_phase = "active"
            laser_h_until = frame + (32 if boss["phase"] == 3 else 26)
        return
    if laser_h_phase == "active":
        if (
            abs(player.ycor() - laser_h_y) < laser_h_height / 2 + 12
            and -370 < player.xcor() < 370
        ):
            if "space" not in keys or energy <= 0 or frame < shield_overheated_until or frame < shield_delay_until:
                damage_player(1)
        if frame >= laser_h_until:
            hide_horizontal_laser_objects()
            laser_h_phase = "idle"
            laser_h_until = 0
# ============================================================
# BOSS UPDATE AND MULTI-PHASE TRANSITIONS
# ============================================================
def update_boss():
    global boss, score, energy
    if boss is None:
        if (
            boss_level < 3
            and next_boss_score is not None
            and score >= next_boss_score
        ):
            spawn_boss()
        return
    sprite = boss["sprite"]
    level = boss["level"]
    phase = boss["phase"]
    if level == 3:
        boss["move_phase"] += 0.038
        p = boss["move_phase"]
        if phase == 1:
            target_x = 265 * math.sin(p * 1.25) + 65 * math.cos(p * 2.8)
            target_y = 245 + 30 * math.cos(p * 1.9) + 15 * math.sin(p * 3.5)
            sprite.goto(target_x, target_y)
        elif phase == 2:
            target_x = 285 * math.sin(p * 1.55) + 85 * math.sin(p * 3.2)
            target_y = 235 + 42 * math.cos(p * 2.3)
            sprite.goto(target_x, target_y)
        else:
            target_x = 295 * math.sin(p * 1.85) + 75 * math.cos(p * 4.4)
            target_y = 225 + 52 * math.sin(p * 2.6) * math.cos(p * 1.2)
            sprite.goto(target_x, target_y)
    else:
        boss["move_phase"] += 0.04
        speed_mult = 1.0 + (phase - 1) * 0.45
        sprite.setx(
            sprite.xcor()
            + boss["speed"] * speed_mult * boss["direction"]
        )
        if sprite.xcor() > 310:
            boss["direction"] = -1
        elif sprite.xcor() < -310:
            boss["direction"] = 1
        vertical_bob = 30 + (phase * 8)
        sprite.sety(
            255 + math.sin(boss["move_phase"] * (1.0 + phase * 0.2)) * vertical_bob
        )
    boss["attack_cooldown"] -= 1
    boss["laser_cooldown"] -= 1
    boss["special_cooldown"] -= 1
    if level == 3:
        boss["missile_cooldown"] = boss.get("missile_cooldown", 90) - 1
        boss["h_laser_cooldown"] = boss.get("h_laser_cooldown", 140) - 1
        if boss["missile_cooldown"] <= 0:
            bx = sprite.xcor()
            by = sprite.ycor() - 25
            spawn_boss_missile(bx - 45, by, speed=9.5)
            spawn_boss_missile(bx + 45, by, speed=9.5)
            boss["missile_cooldown"] = 75 if phase == 3 else 100
            show_message("WARNING: HIGH-SPEED MISSILES INCOMING!", 190, 16, 40)
        if phase >= 2 and boss["h_laser_cooldown"] <= 0 and laser_h_phase == "idle":
            start_boss_horizontal_laser()
            boss["h_laser_cooldown"] = 160 if phase == 3 else 210
    if boss["attack_cooldown"] <= 0:
        fire_boss_volley()
        if level == 1:
            boss["attack_cooldown"] = 70 if phase == 1 else 45
        elif level == 2:
            boss["attack_cooldown"] = 55 if phase == 1 else 36
        else:
            if phase == 1:
                boss["attack_cooldown"] = 48
            elif phase == 2:
                boss["attack_cooldown"] = 40
            else:
                boss["attack_cooldown"] = 34
    if boss["laser_cooldown"] <= 0 and laser_phase == "idle":
        start_boss_laser()
        boss["laser_cooldown"] = 180 if phase == 1 else 135
    if boss["special_cooldown"] <= 0:
        trigger_boss_special_attack()
        boss["special_cooldown"] = 150 if phase == 1 else 115
    update_boss_laser()
    if level == 3:
        update_boss_horizontal_laser()
        update_boss_guards()
    for bullet in bullets[:]:
        bullet_sprite = bullet["sprite"]
        if bullet_sprite.distance(sprite) < (45 if level == 3 else 36):
            dmg = bullet.get("damage", 1.0)
            boss["hp"] -= dmg
            bullet_sprite.hideturtle()
            bullet_sprite.goto(1200, 1200)
            bullets.remove(bullet)
    if level < 3 and boss["phase"] == 1 and boss["hp"] <= boss["max_hp"] * 0.5:
        boss["phase"] = 2
        sprite.color("#ff1744" if level == 1 else "#aa00ff")
        boss["attack_cooldown"] = 15
        boss["special_cooldown"] = 20
        show_message(f"{boss['name']}: ENRAGED PHASE 2! ATTACK SPEED INCREASED!", 190, 17, 100)
    elif level == 3 and boss["phase"] == 1 and boss["hp"] <= boss["max_hp"] * 0.66:
        boss["phase"] = 2
        sprite.color("#ff9100")
        boss["attack_cooldown"] = 15
        boss["special_cooldown"] = 20
        show_message("SINGULARITY: HYPER-OVERLOAD PHASE 2!", 190, 17, 100)
    elif level == 3 and boss["phase"] == 2 and boss["hp"] <= boss["max_hp"] * 0.33:
        boss["phase"] = 3
        sprite.color("#ff0055")
        boss["attack_cooldown"] = 10
        boss["special_cooldown"] = 15
        show_message("SINGULARITY: EVENT HORIZON FINAL PHASE 3!", 190, 18, 120)
    if boss is not None and boss["hp"] <= 0:
        defeat_boss()
def defeat_boss():
    global boss, score, energy
    global laser_phase, laser_until
    global laser_h_phase, laser_h_until
    if boss is None:
        return
    defeated_level = boss["level"]
    sprite = boss["sprite"]
    x = sprite.xcor()
    y = sprite.ycor()
    sprite.hideturtle()
    sprite.goto(1200, 1200)
    reward = BOSS_REWARDS[defeated_level]
    score += reward
    energy = min(max_energy, energy + SHIELD_BOSS_REWARD)
    add_player_xp(250 + defeated_level * 100)
    upgrade_name = None
    if defeated_level < 3:
        spawn_powerup(x, y, boss_reward=True)
        upgrade_name = grant_permanent_upgrade()
    boss = None
    laser_phase = "idle"
    laser_until = 0
    hide_laser_objects()
    laser_h_phase = "idle"
    laser_h_until = 0
    hide_horizontal_laser_objects()
    clear_boss_guards()
    if defeated_level == 3:
        win_game()
    else:
        text = f"{BOSS_NAMES[defeated_level]} DEFEATED! +{reward} SCORE"
        if upgrade_name is not None:
            text += f"\nPERMANENT UPGRADE: {upgrade_name}"
        show_message(text, 165, 17, 170)
# ============================================================
# PLAYER BULLET COLLISIONS
# ============================================================
def check_player_bullet_hits():
    for bullet in bullets[:]:
        sprite = bullet["sprite"]
        hit = False
        dmg = bullet.get("damage", 1.0)
        for enemy in enemies[:]:
            if sprite.distance(enemy["sprite"]) < 22:
                enemy["hp"] -= dmg
                hit = True
                break
        if not hit and boss_guards:
            for guard in boss_guards[:]:
                if sprite.distance(guard["sprite"]) < 25:
                    guard["hp"] -= dmg
                    hit = True
                    break
        if hit:
            sprite.hideturtle()
            sprite.goto(1200, 1200)
            if bullet in bullets:
                bullets.remove(bullet)
# ============================================================
# GAME OVER, VICTORY, AND RESTART
# ============================================================
def end_game():
    global game_over, gravity_repel_active
    if game_over:
        return
    game_over = True
    shield_visual.hideturtle()
    shield_outer.hideturtle()
    aegis_visual.clear()
    player.hideturtle()
    partner_turtle.hideturtle()
    player_laser_drawer.clear()
    gravity_repel_active = False
    gravity_repel_pen.clear()
    if gravity_orb is not None:
        remove_object(gravity_orb["sprite"], [])
        gravity_orb = None
    gravity_vortex_pen.clear()
    hide_horizontal_laser_objects()
    clear_boss_guards()
    draw_text(
        message_text, 0, 30,
        f"GAME OVER\nFinal Score: {score}  |  Level: {player_level}\nPress R to Restart",
        align="center",
        font=("Arial", 22, "bold")
    )
def win_game():
    global game_over, gravity_orb, gravity_repel_active
    game_over = True
    player.hideturtle()
    partner_turtle.hideturtle()
    hide_shield()
    aegis_visual.clear()
    player_laser_drawer.clear()
    boss_bar.hideturtle()
    boss_bar_bg.hideturtle()
    gravity_repel_active = False
    gravity_repel_pen.clear()
    if gravity_orb is not None:
        remove_object(gravity_orb["sprite"], [])
        gravity_orb = None
    gravity_vortex_pen.clear()
    hide_horizontal_laser_objects()
    clear_boss_guards()
    draw_text(
        message_text, 0, 30,
        f"VICTORY!\nSINGULARITY DESTROYED\nFinal Score: {score}  |  Level: {player_level}\nPress R to Restart",
        align="center",
        font=("Arial", 22, "bold")
    )
def restart():
    global score, lives, energy, game_over, paused, frame
    global boss, boss_level, next_boss_score
    global laser_phase, laser_until, laser_x
    global laser_warning, laser_beam
    global laser_h_phase, laser_h_until
    global triple_shot_until, overheat_until, invincible_until
    global perm_dual, perm_fire_rate, perm_shield, perm_shield_ready_at
    global message_until, player_level, player_xp, player_xp_needed, level_10_bonus_awarded
    global partner_until, player_laser_ammo, player_laser_timer, shield_overheated_until
    global shield_was_active, shield_delay_until
    global gravity_orb, gravity_orb_ready_at, gravity_explosion_timer
    global gravity_repel_ready_at, gravity_repel_active
    global debuff_slow_until, debuff_silence_until, debuff_reverse_until
    if boss is not None:
        boss["sprite"].hideturtle()
        boss["sprite"].goto(1200, 1200)
    score = 0
    lives = 3
    energy = 45
    game_over = False
    paused = False
    frame = 0
    player_level = 1
    player_xp = 0
    player_xp_needed = 100
    level_10_bonus_awarded = False
    partner_until = 0
    player_laser_ammo = 0
    player_laser_timer = 0
    shield_overheated_until = 0
    shield_was_active = False
    shield_delay_until = 0
    debuff_slow_until = 0
    debuff_silence_until = 0
    debuff_reverse_until = 0
    if gravity_orb is not None:
        remove_object(gravity_orb["sprite"], [])
        gravity_orb = None
    gravity_orb_ready_at = 0
    gravity_explosion_timer = 0
    gravity_vortex_pen.clear()
    gravity_repel_ready_at = 0
    gravity_repel_active = False
    gravity_repel_pen.clear()
    boss = None
    boss_level = 0
    next_boss_score = BOSS_THRESHOLDS[0]
    laser_phase = "idle"
    laser_until = 0
    laser_x = 0
    laser_h_phase = "idle"
    laser_h_until = 0
    hide_horizontal_laser_objects()
    clear_boss_guards()
    triple_shot_until = 0
    overheat_until = 0
    invincible_until = 0
    perm_dual = False
    perm_fire_rate = False
    perm_shield = False
    perm_shield_ready_at = 0
    message_until = 0
    clear_collection(enemies)
    clear_collection(bullets)
    clear_collection(enemy_bullets)
    clear_collection(powerups)
    clear_collection(boss_bullets)
    hide_laser_objects()
    laser_warning = None
    laser_beam = None
    player_laser_drawer.clear()
    player.goto(0, -260)
    player.setheading(90)
    player.showturtle()
    player.color("#48e5ff")
    partner_turtle.hideturtle()
    partner_turtle.goto(1200, 1200)
    shield_visual.hideturtle()
    shield_outer.hideturtle()
    hide_shield()
    aegis_visual.clear()
    message_text.clear()
    boss_text.clear()
    navigator_text.clear()
    boss_bar.hideturtle()
    boss_bar_bg.hideturtle()
    keys.clear()
    update_hud()
screen.onkeypress(restart, "r")
screen.onkeypress(restart, "R")
# ============================================================
# MAIN LOOP
# ============================================================
def game_loop():
    global frame
    if game_over:
        screen.update()
        screen.ontimer(game_loop, 20)
        return
    try:
        frame += 1
        if frame >= message_until:
            message_text.clear()
        shield_on = update_player()
        update_partner()
        update_player_weapon()
        update_player_bullets()
        update_player_mega_laser()
        update_gravity_orb()
        update_gravity_repel()
        spawn_interval = max(18, 42 - score // 100)
        if boss is None:
            if frame % spawn_interval == 0:
                spawn_enemy()
        else:
            if frame % BOSS_ENEMY_INTERVAL == 0:
                spawn_enemy(during_boss=True)
        check_player_bullet_hits()
        update_enemies(shield_on)
        update_powerups()
        update_enemy_bullets(shield_on)
        update_boss()
        update_hud()
    except Exception as e:
        print("Game loop safety exception:", e)
    screen.update()
    screen.ontimer(game_loop, 20)
# ============================================================
# START
# ============================================================
update_hud()
game_loop()
screen.mainloop()