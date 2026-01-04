from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

colors = {"white": (1.0, 1.0, 1.0), "red": (1.0, 0.0, 0.0), "green": (0.0, 1.0, 0.0), "blue": (0.0, 0.0, 1.0), "yellow": (1.0, 1.0, 0.0), "orange": (1.0, 0.5, 0.0)}
win_width = 1000
win_height = 800
grid_length = 2000
boundary_min = -grid_length
boundary_max = grid_length
wall_thickness = 60.0
last_time = time.time()
camera_angle = 0.0
cam_up_down = -25.0
fov = 120.0
cam_direction = [1.0, 0.0, 0.0]  
view = "third_person"            
camera_eye = [0.0, 0.0, 0.0]
player_xyz = [0.0, 0.0, 0.0]
player_radius = 25.0
player_speed = 5.0
run_speed = 12.0
running = False
player_color = [0.0, 0.0, 1.0]
player_yaw = 0.0
enemies = []
enemy_count = 4
enemy_init_speed = 0.5
enemy_chase_speed = 1.5
enemy_damage_cooldown = 0.8
last_damage = 0.0
lives = 5
score = 0
game_over = False
paused = False
show_instructions = False
flash_on = True
flash_range = 350.0
flash_fov = 40.0
flash_battery = 100.0
shadows = True
shadow_len = 1.0
cheat_mode = False   
cheat_vision = False 
item_pickups = []
item_count = 15
in_menu = True
light_boost = 0.0
slow_enemies = 0.0
speed_boost = 0.0
collectibles = []
collectible_count = 30
collectible_radius = 10
structures = []
outfit_colors = [
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.0, 1.0],
    [1.0, 1.0, 0.0],
    [1.0, 0.5, 0.0],
    [0.5, 0.0, 0.5],
    [0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0]
]
current_outfit_index = 2

def draw_text(x, y, text, font=GLUT_BITMAP_TIMES_ROMAN_24):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, win_width, 0, win_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_menu():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, win_width, 0, win_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    menu_width, menu_height = 480, 140
    menu_x = (win_width - menu_width) / 2
    menu_y = (win_height - menu_height) / 2
    glColor3f(0.12, 0.12, 0.12)
    glBegin(GL_QUADS)
    glVertex2f(menu_x, menu_y)
    glVertex2f(menu_x + menu_width, menu_y)
    glVertex2f(menu_x + menu_width, menu_y + menu_height)
    glVertex2f(menu_x, menu_y + menu_height)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glVertex2f(menu_x, menu_y)
    glVertex2f(menu_x + menu_width, menu_y)
    glVertex2f(menu_x + menu_width, menu_y)
    glVertex2f(menu_x + menu_width, menu_y + menu_height)
    glVertex2f(menu_x + menu_width, menu_y + menu_height)
    glVertex2f(menu_x, menu_y + menu_height)
    glVertex2f(menu_x, menu_y + menu_height)
    glVertex2f(menu_x, menu_y)
    glEnd()
    glClear(GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0, 1.0, 1.0)
    font = GLUT_BITMAP_TIMES_ROMAN_24
    label = "Press SPACE to start"
    char_width = 10
    total_width = len(label) * char_width
    start_x = int(win_width / 2) - (total_width // 2)
    start_y = int(win_height / 2)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    draw_text(start_x, start_y, label, font)
    draw_text(10, 60, "Controls: WASD move | Arrow keys rotate/tilt | P pause | L-click flashlight | R-click FPV toggle")
    draw_text(10, 35, "X run | C god | V vision | T shadows | R reset | H help")

def draw_ground():
    glBegin(GL_QUADS)
    glColor3f(0.08, 0.09, 0.10)
    glVertex3f(-grid_length, grid_length, 0)
    glVertex3f(0, grid_length, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(-grid_length, 0, 0)
    glColor3f(0.07, 0.09, 0.12)
    glVertex3f(grid_length, -grid_length, 0)
    glVertex3f(0, -grid_length, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(grid_length, 0, 0)
    glColor3f(0.08, 0.11, 0.09)
    glVertex3f(-grid_length, -grid_length, 0)
    glVertex3f(-grid_length, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, -grid_length, 0)
    glColor3f(0.11, 0.09, 0.10)
    glVertex3f(grid_length, grid_length, 0)
    glVertex3f(grid_length, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, grid_length, 0)
    glEnd()

    glColor3f(0.2, 0.22, 0.24)
    glBegin(GL_LINES)
    step = 100
    for x in range(-grid_length, grid_length + 1, step):
        glVertex3f(x, -grid_length, 0.2)
        glVertex3f(x,  grid_length, 0.2)
    for y in range(-grid_length, grid_length + 1, step):
        glVertex3f(-grid_length, y, 0.2)
        glVertex3f( grid_length, y, 0.2)
    glEnd()

def draw_walls():
    wall_height = 120.0
    thickness = wall_thickness
    span = boundary_max - boundary_min
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(boundary_min + thickness * 0.5, 0.0, wall_height * 0.5) # Left wall
    glScalef(thickness, span, wall_height)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(boundary_max - thickness * 0.5, 0.0, wall_height * 0.5)  # Right wall
    glScalef(thickness, span, wall_height)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, boundary_min + thickness * 0.5, wall_height * 0.5)  # Bottom wall
    glScalef(span, thickness, wall_height)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, boundary_max - thickness * 0.5, wall_height * 0.5)  # Top wall
    glScalef(span, thickness, wall_height)
    glutSolidCube(1.0)
    glPopMatrix()

def draw_shadow(x, y, r):
    glColor3f(0.02, 0.02, 0.02)
    glPointSize(2)
    glBegin(GL_POINTS)
    steps = 160
    for i in range(steps):
        angle = (i / steps) * 2.0 * math.pi
        for distance in range(0, int(r), 2):
            point_x = x + math.cos(angle) * distance
            point_y = y + math.sin(angle) * distance
            glVertex3f(point_x, point_y, 0.5)
    glEnd()

def in_flash(pos):
    if cheat_vision:
        return True
    if not flash_on:
        return False
    player_x, player_y = player_xyz[0], player_xyz[1]
    target_x, target_y = pos[0], pos[1]
    delta_x, delta_y = target_x - player_x, target_y - player_y
    distance = math.hypot(delta_x, delta_y)
    if distance > flash_range * 1.05:
        return False
    cam_x, cam_y = cam_direction[0], cam_direction[1]
    cam_length = math.hypot(cam_x, cam_y)
    if cam_length == 0 or distance == 0:
        return True
    dot = cam_x * delta_x + cam_y * delta_y
    cos_angle = dot / (cam_length * distance)
    cos_angle = max(-1.0, min(1.0, cos_angle))
    angle_deg = math.degrees(math.acos(cos_angle))
    return angle_deg <= ((flash_fov * 0.5) + 5.0)

def draw_player():
    if view == "first_person":
        return
    if flash_on:
        base = 0.72
    else:
        base = 0.5
    if shadows and flash_on:
        draw_shadow(player_xyz[0], player_xyz[1], player_radius * shadow_len)

    glPushMatrix()
    glTranslatef(player_xyz[0], player_xyz[1], player_radius)
    glRotatef(player_yaw - 90.0, 0, 0, 1)
    glColor3f(player_color[0]*base, player_color[1]*base, player_color[2]*base) # body
    glPushMatrix()
    glScalef(player_radius * 0.6, player_radius * 0.6, player_radius * 1.6)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()                                                  # Head
    glTranslatef(0, 0, player_radius * 1.2)
    glutSolidSphere(player_radius * 0.6, 16, 16)
    glPopMatrix()
    glPushMatrix()                                                  # Flashlight
    glTranslatef(0, 0, player_radius * 1.9) 
    glRotatef(-90, 1, 0, 0)  
    glPushMatrix()
    glColor3f(0.85, 0.85, 0.85)
    glScalef(player_radius * 0.25, player_radius * 0.25, player_radius * 0.6)
    glutSolidCube(1.0)
    glPopMatrix()
    glTranslatef(0, 0, player_radius * 0.35)
    glColor3f(1.0, 1.0, 0.6)
    glutSolidSphere(player_radius * 0.18, 10, 10)
    glPopMatrix()
    glPushMatrix()                                                   # Arms
    glTranslatef(player_radius * 0.65, 0, player_radius * 0.45)
    glScalef(player_radius * 0.3, player_radius * 0.3, player_radius * 1.1)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-player_radius * 0.65, 0, player_radius * 0.45)
    glScalef(player_radius * 0.3, player_radius * 0.3, player_radius * 1.1)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()                                                   # Legs
    glTranslatef(player_radius * 0.28, 0, -player_radius * 0.35)
    glScalef(player_radius * 0.35, player_radius * 0.35, player_radius * 1.25)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-player_radius * 0.28, 0, -player_radius * 0.35)
    glScalef(player_radius * 0.35, player_radius * 0.35, player_radius * 1.25)
    glutSolidCube(1.0)
    glPopMatrix()
    glPopMatrix()

def draw_collectible(x, y, z, radius):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 1.0, 0.0)
    for i in range(5):
        glPushMatrix()
        glRotatef(i * 72, 0, 0, 1)
        glTranslatef(radius, 0, 0)
        glPushMatrix()
        glScalef(radius/3, radius/3, radius)
        glutSolidCube(1.0)
        glPopMatrix()
        glPopMatrix()
    glColor3f(1.0, 0.8, 0.0)
    glutSolidSphere(radius/2, 10, 10)
    glPopMatrix()

def draw_items():
    for item in item_pickups:
        if item["collected"]:
            continue
        visible = in_flash(item["pos"])
        if (not visible) and (not cheat_vision):
            continue
        item_type = item["type"]
        if item_type == "flash_recharge":
            glColor3f(*colors["yellow"])
        elif item_type == "life_refill":
            glColor3f(*colors["green"])
        elif item_type == "light_boost":
            glColor3f(*colors["blue"])
        elif item_type == "slow_enemies":
            glColor3f(*colors["red"])
        elif item_type == "speed_boost":
            glColor3f(*colors["orange"])
        else:
            glColor3f(*colors["white"])
        glPushMatrix()
        glTranslatef(item["pos"][0], item["pos"][1], 10)
        glutSolidCube(item["r"] * 1.4)
        glPopMatrix()
        if shadows:
            draw_shadow(item["pos"][0], item["pos"][1], item["r"] * shadow_len)

    for collectible in collectibles:
        if collectible.get("collected"):
            continue
        if (not in_flash(collectible["pos"])) and (not cheat_vision):
            continue
        draw_collectible(collectible["pos"][0], collectible["pos"][1], 15, collectible_radius)
        if shadows:
            draw_shadow(collectible["pos"][0], collectible["pos"][1], collectible_radius * shadow_len)

def draw_enemies():
    for enemy in enemies:
        if shadows:
            draw_shadow(enemy["pos"][0], enemy["pos"][1], enemy["r"] * shadow_len)
        visible = in_flash(enemy["pos"])
        t = time.time()
        base_col = (0.32, 0.78, 0.46)  
        if t < slow_enemies:
            if visible:
                glColor3f(0.8, 0.8, 0.8)
            else:
                glColor3f(0.5, 0.5, 0.5)
        else:
            if visible:
                glColor3f(*base_col)
            else:
                glColor3f(base_col[0]*0.35, base_col[1]*0.35, base_col[2]*0.35)

        glPushMatrix()
        glTranslatef(enemy["pos"][0], enemy["pos"][1], enemy["r"])
        glPushMatrix()                                                  # Torso
        glScalef(enemy["r"] * 0.7, enemy["r"] * 0.7, enemy["r"] * 1.8)
        glutSolidCube(1.0)
        glPopMatrix()
        glPushMatrix()                                                  # Head
        glTranslatef(0, 0, enemy["r"] * 1.2)
        glutSolidSphere(enemy["r"] * 0.7, 14, 14)
        glPopMatrix()
        glPushMatrix()                                                  # Arms
        glTranslatef(enemy["r"] * 0.8, 0, enemy["r"] * 0.45)
        glRotatef(20, 0, 1, 0)
        glScalef(enemy["r"] * 0.35, enemy["r"] * 0.35, enemy["r"] * 1.35)
        glutSolidCube(1.0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(-enemy["r"] * 0.8, 0, enemy["r"] * 0.45)
        glRotatef(-20, 0, 1, 0)
        glScalef(enemy["r"] * 0.35, enemy["r"] * 0.35, enemy["r"] * 1.35)
        glutSolidCube(1.0)
        glPopMatrix()
        glPushMatrix()                                                 # Legs
        glTranslatef(enemy["r"] * 0.38, 0, -enemy["r"] * 0.45)
        glScalef(enemy["r"] * 0.4, enemy["r"] * 0.4, enemy["r"] * 1.4)
        glutSolidCube(1.0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(-enemy["r"] * 0.38, 0, -enemy["r"] * 0.45)
        glScalef(enemy["r"] * 0.4, enemy["r"] * 0.4, enemy["r"] * 1.4)
        glutSolidCube(1.0)
        glPopMatrix()
        glPopMatrix()

def setup_camera():
    global cam_direction, camera_eye
    cam_dir_x = math.cos(math.radians(camera_angle))
    cam_dir_y = math.sin(math.radians(camera_angle))
    cam_direction = [cam_dir_x, cam_dir_y, 0.0]
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect_ratio = win_width / float(win_height)
    gluPerspective(fov, aspect_ratio, 1.0, 5000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if view == "first_person":
        eye_x = player_xyz[0]
        eye_y = player_xyz[1]
        eye_z = 55.0
        look_x = eye_x + cam_dir_x * 120.0
        look_y = eye_y + cam_dir_y * 120.0
        look_z = eye_z
        camera_eye = [eye_x, eye_y, eye_z]
        gluLookAt(eye_x, eye_y, eye_z,
                  look_x, look_y, look_z,
                  0, 0, 1)
    else:
        eye_x = player_xyz[0] - cam_dir_x * 200.0
        eye_y = player_xyz[1] - cam_dir_y * 200.0
        eye_z = 100.0 + cam_up_down
        playable_min = boundary_min + wall_thickness
        playable_max = boundary_max - wall_thickness
        eye_x = max(playable_min + 1.0, min(playable_max - 1.0, eye_x))
        eye_y = max(playable_min + 1.0, min(playable_max - 1.0, eye_y))
        camera_eye = [eye_x, eye_y, eye_z]
        gluLookAt(eye_x, eye_y, eye_z,
                  player_xyz[0], player_xyz[1], player_xyz[2],
                  0, 0, 1)

def spawn_enemies():
    global enemies
    enemies = []
    for _ in range(enemy_count):
        while True:
            enemy_x = random.randint(int(boundary_min + wall_thickness), int(boundary_max - wall_thickness))
            enemy_y = random.randint(int(boundary_min + wall_thickness), int(boundary_max - wall_thickness))
            dist = math.sqrt((enemy_x - player_xyz[0])**2 + (enemy_y - player_xyz[1])**2)
            if dist > 200:
                break
        enemies.append({
            "pos": [float(enemy_x), float(enemy_y), 0.0],
            "r": 20.0,
            "state": "idle",
            "base_speed": enemy_init_speed
        })

def spawn_items():
    global item_pickups
    item_pickups = []
    item_types = [
        "flash_recharge",
        "life_refill",
        "light_boost",
        "slow_enemies",
        "speed_boost"
    ]
    for _ in range(item_count):
        item_x = random.randint(int(boundary_min + wall_thickness), int(boundary_max - wall_thickness))
        item_y = random.randint(int(boundary_min + wall_thickness), int(boundary_max - wall_thickness))
        kind = random.choice(item_types)
        item_pickups.append({
            "pos": [float(item_x), float(item_y), 0.0],
            "r": 15.0,
            "collected": False,
            "type": kind
        })

def spawn_collectibles():
    global collectibles
    collectibles = []
    for _ in range(collectible_count):
        while True:
            x = random.randint(int(boundary_min + wall_thickness), int(boundary_max - wall_thickness))
            y = random.randint(int(boundary_min + wall_thickness), int(boundary_max - wall_thickness))
            if math.hypot(x - player_xyz[0], y - player_xyz[1]) > 150:
                break
        collectibles.append({
            "pos": [float(x), float(y), 0.0],
            "collected": False
        })

def spawn_structures(count=30):
    global structures
    structures = []
    for _ in range(count):
        w = random.randint(40, 220)
        d = random.randint(40, 220)
        h = random.randint(40, 240)
        sx = random.randint(int(boundary_min + wall_thickness + w), int(boundary_max - wall_thickness - w))
        sy = random.randint(int(boundary_min + wall_thickness + d), int(boundary_max - wall_thickness - d))
        if math.hypot(sx - player_xyz[0], sy - player_xyz[1]) < 200:
            continue
        structures.append({
            "pos": [float(sx), float(sy)],
            "w": float(w),
            "d": float(d),
            "h": float(h),
            "type": random.choice([0,1,2])
        })

def draw_structures():
    eye_x, eye_y, eye_z = camera_eye
    sorted_structures = sorted(
        structures,
        key=lambda s: (
            (s["pos"][0] - eye_x) ** 2 +
            (s["pos"][1] - eye_y) ** 2 +
            ((s["h"] * 0.5) - eye_z) ** 2
        ),
        reverse=True
    )
    for structure in sorted_structures:
        structure_x, structure_y = structure["pos"]
        width, depth, height = structure["w"], structure["d"], structure["h"]
        structure_type = structure.get("type", 0)
        visible = in_flash([structure_x, structure_y, 0.0])
        if structure_type == 0:
            base_col = (0.2, 0.2, 0.25)
        elif structure_type == 1:
            base_col = (0.18, 0.14, 0.12)
        else:
            base_col = (0.22, 0.18, 0.2)
        if not visible:
            base_col = tuple(component * 0.35 for component in base_col)
        glColor3f(*base_col)
        glPushMatrix()
        glTranslatef(structure_x, structure_y, height/2.0)
        glScalef(width, depth, height)
        glutSolidCube(1.0)
        glPopMatrix()

def check_game_over():
    global game_over
    if lives <= 0 or flash_battery <= 0:
        game_over = True

def effects():
    global flash_range, player_speed, run_speed
    t = time.time()
    base_range = 350.0
    if t < light_boost:
        flash_range = base_range * 1.5
    else:
        flash_range = base_range
    if t < speed_boost:
        player_speed = 10.0
        run_speed = 24.0
    else:
        player_speed = 5.0
        run_speed = 12.0

def update_enemies(dt):
    global lives, last_damage
    t = time.time()
    if t < slow_enemies:
        slow_factor = 0.4
    else:
        slow_factor = 1.0
    for enemy in enemies:
        ex, ey = enemy["pos"][0], enemy["pos"][1]
        px, py = player_xyz[0], player_xyz[1]
        dx = ex - px
        dy = ey - py
        visible = in_flash(enemy["pos"])
        if enemy.get("state") == "idle":
            if visible:
                enemy["state"] = "chase"
        speed = enemy["base_speed"] * slow_factor
        if enemy.get("state") == "chase":
            speed *= enemy_chase_speed
            vx = px - ex
            vy = py - ey
            length = math.sqrt(vx*vx + vy*vy)
            if length != 0:
                nx = vx / length
                ny = vy / length
            else:
                nx, ny = 0.0, 0.0
            new_x = enemy["pos"][0] + nx * speed * 60.0 * dt
            new_y = enemy["pos"][1] + ny * speed * 60.0 * dt
            collided = False
            for s in structures:
                sx, sy = s["pos"]
                hw = s["w"]/2.0 + enemy["r"]
                hd = s["d"]/2.0 + enemy["r"]
                if abs(new_x - sx) < hw and abs(new_y - sy) < hd:
                    collided = True
                    break
            if not collided:
                enemy["pos"][0] = new_x
                enemy["pos"][1] = new_y
        playable_min = boundary_min + wall_thickness
        playable_max = boundary_max - wall_thickness
        if enemy["pos"][0] < playable_min:
            enemy["pos"][0] = playable_min
        elif enemy["pos"][0] > playable_max:
            enemy["pos"][0] = playable_max
        if enemy["pos"][1] < playable_min:
            enemy["pos"][1] = playable_min
        elif enemy["pos"][1] > playable_max:
            enemy["pos"][1] = playable_max
        dx2 = enemy["pos"][0] - px
        dy2 = enemy["pos"][1] - py
        dist_sq = dx2*dx2 + dy2*dy2
        if dist_sq <= (enemy["r"] + player_radius) ** 2:
            if enemy.get("state") != "idle":
                if (not cheat_mode) and (t - last_damage > enemy_damage_cooldown):
                    lives -= 1
                    last_damage = t

def check_item_pickups():
    global lives, flash_battery, light_boost, slow_enemies, score, speed_boost
    px, py = player_xyz[0], player_xyz[1]
    for item in item_pickups:
        if item["collected"]:
            continue
        dx = item["pos"][0] - px
        dy = item["pos"][1] - py
        dist_sq = dx*dx + dy*dy
        if dist_sq <= (item["r"] + player_radius) ** 2:
            item["collected"] = True
            score += 5
            item_type = item["type"]
            if item_type == "life_refill":
                lives = min(10, lives + 1)
            elif item_type == "flash_recharge":
                flash_battery = min(100.0, flash_battery + 30.0)
            elif item_type == "light_boost":
                light_boost = time.time() + 10.0
            elif item_type == "slow_enemies":
                slow_enemies = time.time() + 8.0
            elif item_type == "speed_boost":
                speed_boost = time.time() + 6.0

    for collectible in collectibles:
        if collectible.get("collected"):
            continue
        dx = collectible["pos"][0] - px
        dy = collectible["pos"][1] - py
        if dx*dx + dy*dy <= (collectible_radius + player_radius) ** 2:
            collectible["collected"] = True
            score += 5

def can_move_to(x, y, radius):
    playable_min = boundary_min + wall_thickness
    playable_max = boundary_max - wall_thickness
    if x < playable_min or x > playable_max or y < playable_min or y > playable_max:
        return False
    for s in structures:
        sx, sy = s["pos"]
        half_width = s["w"] / 2.0 + radius
        half_depth = s["d"] / 2.0 + radius
        if abs(x - sx) < half_width and abs(y - sy) < half_depth:
            return False
    return True

def update_game(dt):
    global flash_battery
    if paused or game_over:
        return
    update_enemies(dt)
    check_item_pickups()
    if flash_on and (not cheat_mode):
        flash_battery -= 1.2 * dt
        if flash_battery < 0.0:
            flash_battery = 0.0
    effects()
    check_game_over()

def reset_game():
    global player_xyz, lives, score, game_over, paused, flash_battery, cheat_mode, cheat_vision, light_boost, slow_enemies, speed_boost, view, camera_angle, cam_up_down, running, player_color, current_outfit_index
    player_xyz = [0.0, 0.0, 0.0]
    lives = 5
    score = 0
    game_over = False
    paused = False
    flash_battery = 100.
    cheat_mode = False
    cheat_vision = False
    light_boost = 0.0
    slow_enemies = 0.0
    speed_boost = 0.0
    view = "third_person"
    camera_angle = 0.0
    cam_up_down = -25.0
    running = False
    current_outfit_index = 2
    player_color = outfit_colors[current_outfit_index].copy()
    spawn_enemies()
    spawn_items()
    spawn_structures()
    spawn_collectibles()


def change_outfit():
    global current_outfit_index, player_color
    current_outfit_index = (current_outfit_index + 1) % len(outfit_colors)
    player_color = outfit_colors[current_outfit_index].copy()

def keyboardListener(key, x, y):
    global in_menu
    if key == b' ':
        if in_menu:
            in_menu = False
            reset_game()
            return
    global paused, cheat_mode, cheat_vision, player_color, shadows
    global flash_on, show_instructions, running
    if key == b'p':
        paused = not paused
        return
    if key == b'f':
        flash_on = not flash_on
        return
    if key == b'h':
        show_instructions = not show_instructions
        return
    if key == b'x':
        running = not running
        return
    if key == b'c':
        cheat_mode = not cheat_mode
        player_color = [1.0, 1.0, 0.0] if cheat_mode else outfit_colors[current_outfit_index].copy()
        return
    if key == b'v':
        cheat_vision = not cheat_vision
        return
    if key == b'u':
        change_outfit()
        return
    if key == b't':
        shadows = not shadows
        return
    if key == b'r':
        reset_game()
        return
    if game_over or paused:
        return
    if running:
        speed = run_speed
    else:
        speed = player_speed
    forward_x, forward_y = cam_direction[0], cam_direction[1]
    right_x, right_y = -forward_y, forward_x
    if key == b'w':
        nx = player_xyz[0] + forward_x * speed
        ny = player_xyz[1] + forward_y * speed
        if can_move_to(nx, ny, player_radius):
            player_xyz[0] = nx
            player_xyz[1] = ny
    elif key == b's':
        nx = player_xyz[0] - forward_x * speed
        ny = player_xyz[1] - forward_y * speed
        if can_move_to(nx, ny, player_radius):
            player_xyz[0] = nx
            player_xyz[1] = ny
    elif key == b'd':
        nx = player_xyz[0] - right_x * speed
        ny = player_xyz[1] - right_y * speed
        if can_move_to(nx, ny, player_radius):
            player_xyz[0] = nx
            player_xyz[1] = ny
    elif key == b'a':
        nx = player_xyz[0] + right_x * speed
        ny = player_xyz[1] + right_y * speed
        if can_move_to(nx, ny, player_radius):
            player_xyz[0] = nx
            player_xyz[1] = ny

    playable_min = boundary_min + wall_thickness
    playable_max = boundary_max - wall_thickness
    if player_xyz[0] < playable_min:
        player_xyz[0] = playable_min
    elif player_xyz[0] > playable_max:
        player_xyz[0] = playable_max

    if player_xyz[1] < playable_min:
        player_xyz[1] = playable_min
    elif player_xyz[1] > playable_max:
        player_xyz[1] = playable_max

def special_keys(key, x, y):
    global camera_angle, cam_up_down, player_yaw
    if key == GLUT_KEY_UP:
        cam_up_down += 2.0
    elif key == GLUT_KEY_DOWN:
        cam_up_down -= 2.0
    elif key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle - 2.0) % 360.0
        player_yaw = camera_angle
    elif key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle + 2.0) % 360.0
        player_yaw = camera_angle

def mouse(button, state, x, y):
    global flash_on, view
    if state != GLUT_DOWN:
        return
    if button == GLUT_LEFT_BUTTON:
        flash_on = not flash_on
    elif button == GLUT_RIGHT_BUTTON:
        view = "first_person" if view == "third_person" else "third_person"

def idle():
    global last_time
    now = time.time()
    dt = now - last_time
    last_time = now
    update_game(dt)
    glutPostRedisplay()

def update_text():
    mode = "FPV" if view == "first_person" else "TPV"
    font = GLUT_BITMAP_HELVETICA_18
    color_names = ["Red", "Green", "Blue", "Yellow", "Orange", "Purple", "Cyan", "Magenta"]
    outfit_name = color_names[current_outfit_index]
    t_now = time.time()
    active = []
    if t_now < light_boost:
        active.append(f"Light Boost {int(light_boost - t_now)}s")
    if t_now < slow_enemies:
        active.append(f"Slow Enemies {int(slow_enemies - t_now)}s")
    if t_now < speed_boost:
        active.append(f"Speed Boost {int(speed_boost - t_now)}s")
    active_effects_line = ", ".join(active) if active else "None"
    glColor3f(0.0, 1.0, 1.0)
    draw_text(10, win_height - 25, f"Score: {score}", font)
    glColor3f(0.9, 0.95, 0.6)
    draw_text(10, win_height - 50, f"Effects: {active_effects_line}", font)
    glColor3f(1.0, 0.8, 0.0)
    lives_label = f"Lives: {lives}"
    battery_label = f"Battery: {int(flash_battery)}%"
    char_w_hud = 10  
    lives_label_width = len(lives_label) * char_w_hud
    battery_label_width = len(battery_label) * char_w_hud
    draw_text(win_width - lives_label_width - 10, win_height - 25, lives_label, font)
    glColor3f(0.8, 0.8, 1.0)
    draw_text(win_width - battery_label_width - 10, win_height - 50, battery_label, font)
    if flash_on:
        flash_label = "ON"
    else:
        flash_label = "OFF"
    if running:
        run_label = "ON"
    else:
        run_label = "OFF"
    if shadows:
        shadows_label = "ON"
    else:
        shadows_label = "OFF"
    mid_strings = [
        f"Mode: {mode}",
        f"Outfit (u): {outfit_name}",
        f"Flash: {flash_label} | Run: {run_label} | Shadows: {shadows_label}"
    ]
    colors_mid = [(1.0, 1.0, 1.0), (0.6, 0.9, 1.0), (0.9, 0.7, 1.0)]
    y_offset = win_height - 25
    for idx in range(len(mid_strings)):
        text = mid_strings[idx]
        glColor3f(*colors_mid[idx])
        w = len(text) * char_w_hud
        draw_text(int(win_width/2 - w/2), y_offset - idx*25, text, font)
    if paused:
        draw_text(win_width//2 - 50, win_height//2, "PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
    if game_over:
        draw_text(win_width//2 - 90, win_height//2 + 30, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(win_width//2 - 170, win_height//2, "Press 'r' to restart", GLUT_BITMAP_HELVETICA_18)
    if show_instructions:
        y = win_height - 80
        draw_text(10, y,     "Controls:")
        draw_text(10, y-25,  "WASD move | Arrow keys rotate/tilt | P pause | L-click flashlight | R-click FPV toggle")
        draw_text(10, y-50,  "X run | C god | V vision | T shadows | R reset | H help")

def flash_mode():
    setup_camera()
    draw_ground()
    if flash_on:
        glColor3f(0.5, 0.45, 0.3)
        center_ang = math.atan2(cam_direction[1], cam_direction[0])
        half_ang = math.radians(flash_fov) * 0.5
        steps = 28
        glBegin(GL_LINES)
        for i in range(steps + 1):
            a = center_ang - half_ang + (2 * half_ang) * (i / steps)
            end_x = player_xyz[0] + math.cos(a) * flash_range
            end_y = player_xyz[1] + math.sin(a) * flash_range
            glVertex3f(player_xyz[0], player_xyz[1], 2.0)
            glVertex3f(end_x, end_y, 2.0)
        glEnd()
        glBegin(GL_LINES)
        for i in range(steps):
            a1 = center_ang - half_ang + (2 * half_ang) * (i / steps)
            a2 = center_ang - half_ang + (2 * half_ang) * ((i + 1) / steps)
            glVertex3f(
                player_xyz[0] + math.cos(a1) * flash_range,
                player_xyz[1] + math.sin(a1) * flash_range,
                2.0
            )
            glVertex3f(
                player_xyz[0] + math.cos(a2) * flash_range,
                player_xyz[1] + math.sin(a2) * flash_range,
                2.0
            )
        glEnd()
    draw_walls()
    draw_structures()
    draw_items()
    draw_enemies()
    draw_player()

def display():
    glViewport(0, 0, win_width, win_height)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    if in_menu:
        draw_menu()
        glutSwapBuffers()
        return
    flash_mode()
    update_text()
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(win_width, win_height)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Light & Shadow Game")
    spawn_enemies()
    spawn_items()
    spawn_structures()
    spawn_collectibles()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
