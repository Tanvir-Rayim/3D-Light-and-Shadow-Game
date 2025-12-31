from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

colors = {
    "white": (1.0, 1.0, 1.0),
    "red": (1.0, 0.0, 0.0),
    "green": (0.0, 1.0, 0.0),
    "blue": (0.0, 0.0, 1.0),
    "yellow": (1.0, 1.0, 0.0)
}

win_width = 1000
win_height = 800
grid_length = 1000
boundary_min = 100 - grid_length
boundary_max = grid_length - 100

last_time = time.time()
delta_time = 0

camera_angle =0
cam_up_down = -25
fov = 120
cam_direction = [1, 0, 0]
view = "third_person"

player_xyz = [0, 0, 0]
player_radius = 25
player_speed = 5
run_speed = 12
running = False
player_color = [0.0, 0.0, 1.0]
enemies = []
enemy_count = 4
enemy_init_speed = 0.5
enemy_chase_speed = 1.5
enemy_damage_cooldown = 0.8
last_damage = 0

lives = 5
score = 0
game_over = False
paused = False
show_instructions = False
flash_on = True
flash_range = 150
flash_fov = 30
flash_brightness = 1.5
flash_off_dim = 0.2
flash_battery = 100
shadows = True
shadow_len = 1

cheat_mode = False
cheat_vision = False

hidden_items = []
items = 8

flash_recharge = 0
life_refill = 0
light_boost = 0
slow_enemies = 0

seed = 423
random.seed(seed)

# World bounds (used by walls and keep-inside logic)
WORLD_MIN = boundary_min
WORLD_MAX = boundary_max

# Simple helpers
def dist2(x1, y1, x2, y2):
    return (x1 - x2) ** 2 + (y1 - y2) ** 2

def normalize2(x, y):
    length = math.hypot(x, y)
    if length == 0:
        return 0.0, 0.0
    return x / length, y / length

def keep_inside_world(pos):
    pos[0] = max(WORLD_MIN, min(WORLD_MAX, pos[0]))
    pos[1] = max(WORLD_MIN, min(WORLD_MAX, pos[1]))

# Simple cheat flag used when enemies touch player
cheat_god = False

def in_flash(pos):
    """Return True if `pos` (x,y,...) is illuminated by the player's flashlight.

    Rules:
    - If `cheat_vision` is enabled, always return True.
    - If flashlight (`flash_on`) is off, return False.
    - Otherwise return True when the object is within `flash_range` and inside
      the cone defined by `cam_direction` and `flash_fov`.
    """
    if cheat_vision:
        return True
    if not flash_on:
        return False
    # ensure pos has at least x,y
    px, py = player_xyz[0], player_xyz[1]
    ox, oy = pos[0], pos[1]
    dx, dy = ox - px, oy - py
    dist = math.hypot(dx, dy)
    if dist > flash_range:
        return False
    # angle between camera forward (cam_direction) and vector to object
    fx, fy = cam_direction[0], cam_direction[1]
    cam_len = math.hypot(fx, fy)
    if cam_len == 0 or dist == 0:
        return True
    dot = fx * dx + fy * dy
    cosang = dot / (cam_len * dist)
    # clamp to valid domain for acos
    cosang = max(-1.0, min(1.0, cosang))
    ang_deg = math.degrees(math.acos(cosang))
    return ang_deg <= (flash_fov / 2.0)

def draw_text(x, y, text, font=GLUT_BITMAP_TIMES_ROMAN_24):
    glColor3f(1, 1, 1)
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

def draw_ground():
    glBegin(GL_QUADS)
    glColor3f(0.12, 0.12, 0.12)
    glVertex3f(-grid_length, grid_length, 0)
    glVertex3f(0, grid_length, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(-grid_length, 0, 0)

    glColor3f(0.10, 0.10, 0.16)
    glVertex3f(grid_length, -grid_length, 0)
    glVertex3f(0, -grid_length, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(grid_length, 0, 0)

    glColor3f(0.10, 0.14, 0.10)
    glVertex3f(-grid_length, -grid_length, 0)
    glVertex3f(-grid_length, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, -grid_length, 0)

    glColor3f(0.14, 0.10, 0.10)
    glVertex3f(grid_length, grid_length, 0)
    glVertex3f(grid_length, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, grid_length, 0)
    glEnd()

    glColor3f(0.25, 0.25, 0.25)
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
    height = 100
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    # Left
    glVertex3f(WORLD_MIN, WORLD_MIN, 0)
    glVertex3f(WORLD_MIN, WORLD_MAX, 0)
    glVertex3f(WORLD_MIN, WORLD_MAX, height)
    glVertex3f(WORLD_MIN, WORLD_MIN, height)
    # Right
    glVertex3f(WORLD_MAX, WORLD_MIN, 0)
    glVertex3f(WORLD_MAX, WORLD_MAX, 0)
    glVertex3f(WORLD_MAX, WORLD_MAX, height)
    glVertex3f(WORLD_MAX, WORLD_MIN, height)
    # Bottom
    glVertex3f(WORLD_MIN, WORLD_MIN, 0)
    glVertex3f(WORLD_MAX, WORLD_MIN, 0)
    glVertex3f(WORLD_MAX, WORLD_MIN, height)
    glVertex3f(WORLD_MIN, WORLD_MIN, height)
    # Top
    """glVertex3f(WORLD_MIN, WORLD_MAX, 0)
    glVertex3f(WORLD_MAX, WORLD_MAX, 0)
    glVertex3f(WORLD_MAX, WORLD_MAX, height)
    glVertex3f(WORLD_MIN, WORLD_MAX, height)"""
    glEnd()

def draw_shadow(x, y, r):
    glColor3f(0.02, 0.02, 0.02)
    segments = 24
    thick = r * 0.25
    glBegin(GL_QUADS)
    for i in range(segments):
        angle1 = (i/segments) * 2 * math.pi
        angle2 = ((i+1)/segments) * 2 * math.pi
        x1_outer = x + r * math.cos(angle1)
        y1_outer = y + r * math.sin(angle1)
        x2_outer = x + r * math.cos(angle2)
        y2_outer = y + r * math.sin(angle2) 
        glVertex3f(x1_outer, y1_outer, 0.1)
        glVertex3f(x2_outer, y2_outer, 0.1)
        glVertex3f(x2_outer, y2_outer, thick)
        glVertex3f(x1_outer, y1_outer, thick)
    glEnd()

def draw_player():
    if flash_on == True:
        base = 0.7
    else:
        base = 0.45
    glColor3f(player_color[0]*base, player_color[1]*base, player_color[2]*base)
    glPushMatrix()
    glTranslatef(player_xyz[0], player_xyz[1], player_radius)
    glutSolidSphere(player_radius, 20, 20)
    glPopMatrix()
    if shadows == True:
        draw_shadow(player_xyz[0], player_xyz[1], player_radius*shadow_len)

def draw_items():
    for item in hidden_items:
        if item["collected"] == True:
            continue
        visible = in_flash(item["pos"])
        if visible == False and cheat_vision == False:
            continue
        # use item "kind" consistently and choose a single matching color
        if item.get("kind") == "flash_recharge":
            glColor3f(*colors["yellow"])
        elif item.get("kind") == "life_refill":
            glColor3f(*colors["green"])
        elif item.get("kind") == "light_boost":
            glColor3f(*colors["blue"])
        elif item.get("kind") == "slow_enemies":
            glColor3f(*colors["red"])   
        else:
            glColor3f(*colors["white"])
        glPushMatrix()
        glTranslatef(item["pos"][0], item["pos"][1], 10)
        glutSolidCube(item["r"]*1.4)
        glPopMatrix()
        if shadows == True:
            draw_shadow(item["pos"][0], item["pos"][1], item["r"]*shadow_len)

def draw_enemies():
    for enemy in enemies:
        visible = in_flash(enemy["pos"])
        if visible == True:
            glColor3f(*colors["red"])
        else:
            dim = tuple(c * 0.3 for c in colors["red"])
            glColor3f(*dim)
        glPushMatrix()
        glTranslatef(enemy["pos"][0], enemy["pos"][1], enemy["r"])
        glutSolidSphere(enemy["r"], 15, 15)
        glPopMatrix()
        if shadows == True:
            draw_shadow(enemy["pos"][0], enemy["pos"][1], enemy["r"]*shadow_len)

def setup_camera():
    global cam_direction
    fx = math.cos(math.radians(camera_angle))
    fy = math.sin(math.radians(camera_angle))
    cam_direction = [fx, fy, 0]
    eye_x = player_xyz[0] - cam_direction[0]*200
    eye_y = player_xyz[1] - cam_direction[1]*200
    eye_z = player_xyz[2] + 100 + cam_up_down
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect_ratio = win_width / win_height
    gluPerspective(fov, aspect_ratio, 1, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(eye_x, eye_y, eye_z,
              player_xyz[0], player_xyz[1], player_xyz[2],
              0, 0, 1)
    
def spawn_enemies():
    global enemies
    enemies = []
    for _ in range(enemy_count):
        while True:
            enemy_x = random.randint(boundary_min, boundary_max)
            enemy_y = random.randint(boundary_min, boundary_max)
            dist = math.sqrt((enemy_x - player_xyz[0])**2 + (enemy_y - player_xyz[1])**2)
            if dist > 200:
                break
        enemy = {
            "pos": [enemy_x, enemy_y, 0],
            "r": 20,
            "state": "idle",
            "base_speed": enemy_init_speed,
            "last_damage_time": 0
        }
        enemies.append(enemy)

def spawn_items():
    global hidden_items
    hidden_items = []
    for _ in range(items):
        item_x = random.randint(boundary_min, boundary_max)
        item_y = random.randint(boundary_min, boundary_max)
        kind = random.choice(["flash_recharge", "life_refill", "light_boost", "slow_enemies"])
        item = {
            "pos": [item_x, item_y, 0],
            "r": 15,
            "collected": False,
            "kind": kind
        }
        hidden_items.append(item)

def check_game_over():
    global game_over, lives
    if lives <= 0 or flash_battery <= 0:
        game_over = True

def effects():
    global flash_brightness, flash_range
    t = time.time()
    base_range = 150
    base_brightness = 1.5
    if t < light_boost:
        flash_range = base_range * 1.5
        flash_brightness = base_brightness * 1.5
    else:
        flash_range = base_range
        flash_brightness = base_brightness

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
        d2 = dist2(ex, ey, px, py)
        visible = in_flash(enemy["pos"])
        if visible or d2 < (260.0*260.0):
            enemy["state"] = "chase"
        else:
            enemy["state"] = "idle"
        speed = enemy["base_speed"] * slow_factor
        if enemy["state"] == "chase":
            speed *= enemy_chase_speed
            vx, vy = px - ex, py - ey
            nx, ny = normalize2(vx, vy)
            enemy["pos"][0] += nx * speed * 60.0 * dt
            enemy["pos"][1] += ny * speed * 60.0 * dt
        else:
            ang = (random.random()*2.0 - 1.0) * 60.0
            enemy["pos"][0] += math.cos(math.radians(ang)) * speed * 10.0 * dt
            enemy["pos"][1] += math.sin(math.radians(ang)) * speed * 10.0 * dt
        keep_inside_world(enemy["pos"])
        touch = dist2(enemy["pos"][0], enemy["pos"][1], px, py) <= (enemy["r"] + player_radius)**2
        if touch and (not cheat_god) and (t - last_damage > enemy_damage_cooldown):
            lives -= 1
            last_damage = t

def check_item_pickups():
    global score, light_boost, slow_enemies, flash_battery, lives
    px, py = player_xyz[0], player_xyz[1]

    for item in hidden_items:
        if item["collected"]:
            continue

        if dist2(item["pos"][0], item["pos"][1], px, py) <= (item["r"] + player_radius)**2:
            item["collected"] = True
            if item.get("kind") == "score":
                score += 10
            elif item.get("kind") == "light_boost":
                # make the boost last for 10 seconds
                light_boost = time.time() + 10.0
            elif item.get("kind") == "slow_enemies":
                slow_enemies = time.time() + 8.0
            elif item.get("kind") == "life_refill":
                lives += 1
            elif item.get("kind") == "flash_recharge":
                flash_battery = min(100, flash_battery + 30)

def update_game(dt=None):
    global last_time, delta_time, flash_battery
    current_time = time.time()
    if dt is None:
        delta_time = current_time - last_time
        last_time = current_time
    else:
        # caller already computed delta; update globals for consistency
        delta_time = dt
        last_time = current_time

    if not paused and not game_over:
        update_enemies(delta_time)
        check_item_pickups()

        # Battery drains only when flashlight is on and not in god-mode
        if flash_on and (not cheat_mode):
            flash_battery -= 5 * delta_time
            if flash_battery < 0:
                flash_battery = 0

        effects()
        check_game_over()

def reset_game():
    global player_xyz, lives, score, game_over, paused, flash_battery, cheat_mode, cheat_vision, light_boost, slow_enemies
    player_xyz = [0, 0, 0]
    lives = 5
    score = 0
    game_over = False
    paused = False
    flash_battery = 100
    cheat_mode = False
    cheat_vision = False
    light_boost = 0
    slow_enemies = 0
    spawn_enemies()
    spawn_items()

def keyboardListener(key, x, y):
    global paused, cheat_mode, cheat_vision, player_color, shadows, game_over, flash_on, show_instructions, running
    if key == b'\x1b' or key == b'p':  
        paused = not paused
        return
    if key == b'f':
        flash_on = not flash_on
        return
    if key == b'h':
        show_instructions = not show_instructions
        return
    if key == b'x':  # run toggle
        running = not running
        return
    if key == b'c':
        cheat_mode = not cheat_mode
        if cheat_mode:
            player_color = [1.0, 1.0, 0.0]
        else:
            player_color = [0.0, 0.0, 1.0]
        return
    if key == b'v':
        cheat_vision = not cheat_vision
        return
    if key == b'o':
        player_color = [random.random(), random.random(), random.random()]
        return
    if key == b't':
        shadows = not shadows
        return
    if key == b'r':
        reset_game()
        return
    if game_over == True or paused == True:
        return
    if running == True:
        speed = run_speed
    else:
        speed = player_speed
    fx, fy = cam_direction[0], cam_direction[1]
    rx, ry = -fy, fx  
    if key == b'w':
        player_xyz[0] += fx * speed
        player_xyz[1] += fy * speed
    elif key == b's':
        player_xyz[0] -= fx * speed
        player_xyz[1] -= fy * speed
    elif key == b'a':
        player_xyz[0] -= rx * speed
        player_xyz[1] -= ry * speed
    elif key == b'd':
        player_xyz[0] += rx * speed
        player_xyz[1] += ry * speed

    keep_inside_world(player_xyz)

def special_keys(key, x, y):
    global camera_angle, cam_up_down
    if key == GLUT_KEY_UP:
        cam_up_down += 2
    if key == GLUT_KEY_DOWN:
        cam_up_down -= 2
    if key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle - 2) % 360
    if key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle + 2) % 360

def mouse(button, state, x, y):
    global flash_on, view
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        flash_on = not flash_on
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if view == "third_person":
            view = "first_person"
        else:
            view = "third_person"

def idle():
    global last_time, delta_time
    now = time.time()
    delta_time = now - last_time
    last_time = now

    if not paused and not game_over:
        update_game(delta_time)

    glutPostRedisplay()

def display():
    glViewport(0, 0, win_width, win_height)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_camera()
    draw_ground()
    draw_walls()
    draw_items()
    draw_enemies()
    draw_player()
    # update_enemies is called by the game loop; don't call here without dt
    draw_text(10, win_height - 25, f"Score: {score}   Lives: {lives}   Battery: {int(flash_battery)}%")
    draw_text(10, win_height - 50, f"Flashlight: {'ON' if flash_on else 'OFF'}   Run(x): {'ON' if running else 'OFF'}   Shadows(t): {'ON' if shadows else 'OFF'}")
    if paused:
        draw_text(win_width//2 - 50, win_height//2, "PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
    if game_over:
        draw_text(win_width//2 - 90, win_height//2 + 30, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(win_width//2 - 170, win_height//2, "Press 'r' to restart", GLUT_BITMAP_HELVETICA_18)
    if show_instructions:
        y = win_height - 80
        draw_text(10, y,     "Controls:")
        draw_text(10, y-25,  "WASD move | Arrow keys rotate/tilt camera | P pause | F flashlight | X run toggle")
        draw_text(10, y-50,  "C god mode | V vision cheat | O outfit colour | T shadows | R reset | H help")
    glutSwapBuffers()

def init():
    glClearColor(0.02, 0.02, 0.02, 1.0)
    glEnable(GL_DEPTH_TEST)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D Light & Shadow Game")
    init()
    glutDisplayFunc(display)
    spawn_enemies()
    glutSpecialFunc(special_keys)
    glutKeyboardFunc(keyboardListener)
    glutMouseFunc(mouse)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
