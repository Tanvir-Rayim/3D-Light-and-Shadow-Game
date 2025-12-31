from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

colors = {
    "white":  (1.0, 1.0, 1.0),
    "red":    (1.0, 0.0, 0.0),
    "green":  (0.0, 1.0, 0.0),
    "blue":   (0.0, 0.0, 1.0),
    "yellow": (1.0, 1.0, 0.0)
}
win_width = 1000
win_height = 800
grid_length = 2000
boundary_min = 100 - grid_length
boundary_max = grid_length - 100
last_time = time.time()
delta_time = 0.0
camera_angle = 0.0
cam_up_down = -25.0
fov = 120.0
cam_direction = [1.0, 0.0, 0.0]  
view = "third_person"            
player_xyz = [0.0, 0.0, 0.0]
player_radius = 25.0
player_speed = 5.0
run_speed = 12.0
running = False
player_color = [0.0, 0.0, 1.0]
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
flash_range = 300.0
flash_fov = 30.0
flash_brightness = 2.5
flash_off_dim = 0.2
flash_battery = 100.0
shadows = True
shadow_len = 1.0
cheat_mode = False   
cheat_vision = False 
hidden_items = []
items = 8
in_menu = True
light_boost = 0.0
slow_enemies = 0.0
structures = []

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

def draw_menu():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, win_width, 0, win_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glColor3f(0.02, 0.02, 0.02)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(win_width, 0)
    glVertex2f(win_width, win_height)
    glVertex2f(0, win_height)
    glEnd()
    bw, bh = 480, 140
    bx = (win_width - bw) / 2
    by = (win_height - bh) / 2
    glColor3f(0.12, 0.12, 0.12)
    glBegin(GL_QUADS)
    glVertex2f(bx, by)
    glVertex2f(bx + bw, by)
    glVertex2f(bx + bw, by + bh)
    glVertex2f(bx, by + bh)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(bx, by)
    glVertex2f(bx + bw, by)
    glVertex2f(bx + bw, by + bh)
    glVertex2f(bx, by + bh)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    font = GLUT_BITMAP_TIMES_ROMAN_24
    part1 = "Press "
    bold_part = "SPACE"
    part2 = " to start"
    w1 = sum(glutBitmapWidth(font, ord(ch)) for ch in part1)
    wb = sum(glutBitmapWidth(font, ord(ch)) for ch in bold_part)
    w2 = sum(glutBitmapWidth(font, ord(ch)) for ch in part2)
    total_w = int(w1 + wb + w2)
    start_x = int(win_width / 2) - (total_w // 2)
    y = int(win_height / 2) + 20
    draw_text(start_x, y, part1, font)
    bx = start_x + int(w1)
    offsets = [(0,0), (1,0), (0,1), (1,1)]
    for dx, dy in offsets:
        draw_text(bx + dx, y + dy, bold_part, font)
    draw_text(bx + int(wb) + 2, y, part2, font)
    draw_text(10, 60, "Controls: WASD move | Arrow keys rotate/tilt | P pause | L-click flashlight | R-click FPV toggle")
    draw_text(10, 35, "X run | C god | V vision | O outfit | T shadows | R reset | H help")


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
    height = 100.0
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(boundary_min, boundary_min, 0)
    glVertex3f(boundary_min, boundary_max, 0)
    glVertex3f(boundary_min, boundary_max, height)
    glVertex3f(boundary_min, boundary_min, height)

    glVertex3f(boundary_max, boundary_min, 0)
    glVertex3f(boundary_max, boundary_max, 0)
    glVertex3f(boundary_max, boundary_max, height)
    glVertex3f(boundary_max, boundary_min, height)

    glVertex3f(boundary_min, boundary_min, 0)
    glVertex3f(boundary_max, boundary_min, 0)
    glVertex3f(boundary_max, boundary_min, height)
    glVertex3f(boundary_min, boundary_min, height)

    glVertex3f(boundary_min, boundary_max, 0)
    glVertex3f(boundary_max, boundary_max, 0)
    glVertex3f(boundary_max, boundary_max, height)
    glVertex3f(boundary_min, boundary_max, height)
    glEnd()

def draw_shadow(x, y, r):
    glColor3f(0.02, 0.02, 0.02)
    glPointSize(2)
    glBegin(GL_POINTS)
    steps = 160
    for i in range(steps):
        ang = (i / steps) * 2.0 * math.pi
        for d in range(0, int(r), 2):
            px = x + math.cos(ang) * d
            py = y + math.sin(ang) * d
            glVertex3f(px, py, 0.5)
    glEnd()

def in_flash(obj_pos):
    if not flash_on:
        return False
    ox, oy = obj_pos[0], obj_pos[1]
    px, py = player_xyz[0], player_xyz[1]
    vx = ox - px
    vy = oy - py
    if (vx*vx + vy*vy) > (flash_range * flash_range):
        return False
    fx, fy = cam_direction[0], cam_direction[1]
    length = math.sqrt(vx*vx + vy*vy)
    if length != 0:
        vnx = vx / length
        vny = vy / length
    else:
        vnx, vny = 0.0, 0.0
    dot = fx*vnx + fy*vny
    if dot < -1.0:
        dot = -1.0
    elif dot > 1.0:
        dot = 1.0
    theta = math.degrees(math.acos(dot))
    return theta <= (flash_fov * 0.5)

def draw_player():
    if view == "first_person":
        return
    base = 0.7 if flash_on else 0.45
    glColor3f(player_color[0]*base, player_color[1]*base, player_color[2]*base)
    glPushMatrix()
    glTranslatef(player_xyz[0], player_xyz[1], player_radius)
    glutSolidSphere(player_radius, 20, 20)
    glPopMatrix()
    if shadows:
        draw_shadow(player_xyz[0], player_xyz[1], player_radius * shadow_len)

def draw_items():
    for item in hidden_items:
        if item["collected"]:
            continue
        visible = in_flash(item["pos"])
        if (not visible) and (not cheat_vision):
            continue
        t = item["type"]
        if t == "flash_recharge":
            glColor3f(*colors["yellow"])
        elif t == "life_refill":
            glColor3f(*colors["green"])
        elif t == "light_boost":
            glColor3f(*colors["blue"])
        elif t == "slow_enemies":
            glColor3f(*colors["red"])
        else:
            glColor3f(*colors["white"])
        glPushMatrix()
        glTranslatef(item["pos"][0], item["pos"][1], 10)
        glutSolidCube(item["r"] * 1.4)
        glPopMatrix()
        if shadows:
            draw_shadow(item["pos"][0], item["pos"][1], item["r"] * shadow_len)

def draw_enemies():
    for enemy in enemies:
        visible = in_flash(enemy["pos"])
        if visible:
            glColor3f(*colors["red"])
        else:
            r, g, b = colors["red"]
            glColor3f(r*0.3, g*0.3, b*0.3)
        glPushMatrix()
        glTranslatef(enemy["pos"][0], enemy["pos"][1], enemy["r"])
        glutSolidSphere(enemy["r"], 15, 15)
        glPopMatrix()
        if shadows:
            draw_shadow(enemy["pos"][0], enemy["pos"][1], enemy["r"] * shadow_len)

def setup_camera():
    global cam_direction
    fx = math.cos(math.radians(camera_angle))
    fy = math.sin(math.radians(camera_angle))
    cam_direction = [fx, fy, 0.0]
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
        look_x = eye_x + fx * 120.0
        look_y = eye_y + fy * 120.0
        look_z = eye_z
        gluLookAt(eye_x, eye_y, eye_z,
                  look_x, look_y, look_z,
                  0, 0, 1)
    else:
        eye_x = player_xyz[0] - fx * 200.0
        eye_y = player_xyz[1] - fy * 200.0
        eye_z = 100.0 + cam_up_down

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
        enemies.append({
            "pos": [float(enemy_x), float(enemy_y), 0.0],
            "r": 20.0,
            "state": "idle",
            "base_speed": enemy_init_speed
        })

def spawn_items():
    global hidden_items
    hidden_items = []
    for _ in range(items):
        item_x = random.randint(boundary_min, boundary_max)
        item_y = random.randint(boundary_min, boundary_max)
        kind = random.choice(["flash_recharge", "life_refill", "light_boost", "slow_enemies"])
        hidden_items.append({
            "pos": [float(item_x), float(item_y), 0.0],
            "r": 15.0,
            "collected": False,
            "type": kind
        })

def spawn_structures(count=30):
    global structures
    structures = []
    for _ in range(count):
        w = random.randint(40, 220)
        d = random.randint(40, 220)
        h = random.randint(40, 240)
        sx = random.randint(boundary_min + w, boundary_max - w)
        sy = random.randint(boundary_min + d, boundary_max - d)
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
    for s in structures:
        sx, sy = s["pos"]
        w, d, h = s["w"], s["d"], s["h"]
        t = s.get("type", 0)
        if t == 0:
            glColor3f(0.2, 0.2, 0.25)
        elif t == 1:
            glColor3f(0.18, 0.14, 0.12)
        else:
            glColor3f(0.22, 0.18, 0.2)
        glPushMatrix()
        glTranslatef(sx, sy, h/2.0)
        glScalef(w, d, h)
        glutSolidCube(1.0)
        glPopMatrix()

def check_game_over():
    global game_over
    if lives <= 0 or flash_battery <= 0:
        game_over = True

def effects():
    global flash_brightness, flash_range
    t = time.time()
    base_range = 300.0
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
    slow_factor = 0.4 if t < slow_enemies else 1.0
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
        if enemy["pos"][0] < boundary_min:
            enemy["pos"][0] = boundary_min
        elif enemy["pos"][0] > boundary_max:
            enemy["pos"][0] = boundary_max
        if enemy["pos"][1] < boundary_min:
            enemy["pos"][1] = boundary_min
        elif enemy["pos"][1] > boundary_max:
            enemy["pos"][1] = boundary_max
        dx2 = enemy["pos"][0] - px
        dy2 = enemy["pos"][1] - py
        dist_sq = dx2*dx2 + dy2*dy2
        if dist_sq <= (enemy["r"] + player_radius) ** 2:
            if (not cheat_mode) and (t - last_damage > enemy_damage_cooldown):
                lives -= 1
                last_damage = t

def check_item_pickups():
    global lives, flash_battery, light_boost, slow_enemies, score
    px, py = player_xyz[0], player_xyz[1]
    for item in hidden_items:
        if item["collected"]:
            continue
        dx = item["pos"][0] - px
        dy = item["pos"][1] - py
        dist_sq = dx*dx + dy*dy

        if dist_sq <= (item["r"] + player_radius) ** 2:
            item["collected"] = True
            score += 5

            t = item["type"]
            if t == "life_refill":
                lives = min(10, lives + 1)
            elif t == "flash_recharge":
                flash_battery = min(100.0, flash_battery + 30.0)
            elif t == "light_boost":
                light_boost = time.time() + 10.0
            elif t == "slow_enemies":
                slow_enemies = time.time() + 8.0

def can_move_to(x, y, radius):
    if x < boundary_min or x > boundary_max or y < boundary_min or y > boundary_max:
        return False
    for s in structures:
        sx, sy = s["pos"]
        hw = s["w"] / 2.0 + radius
        hd = s["d"] / 2.0 + radius
        if abs(x - sx) < hw and abs(y - sy) < hd:
            return False
    return True

def update_game(dt):
    global flash_battery
    if paused or game_over:
        return
    update_enemies(dt)
    check_item_pickups()
    if flash_on and (not cheat_mode):
        flash_battery -= 2.0 * dt
        if flash_battery < 0.0:
            flash_battery = 0.0
    effects()
    check_game_over()

def reset_game():
    global player_xyz, lives, score, game_over, paused, flash_battery
    global cheat_mode, cheat_vision, light_boost, slow_enemies, view
    global camera_angle, cam_up_down, running, player_color
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
    view = "third_person"
    camera_angle = 0.0
    cam_up_down = -25.0
    running = False
    player_color = [0.0, 0.0, 1.0]
    spawn_enemies()
    spawn_items()
    spawn_structures()

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
        player_color = [1.0, 1.0, 0.0] if cheat_mode else [0.0, 0.0, 1.0]
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
    if game_over or paused:
        return
    speed = run_speed if running else player_speed
    fx, fy = cam_direction[0], cam_direction[1]
    rx, ry = -fy, fx
    if key == b'w':
        nx = player_xyz[0] + fx * speed
        ny = player_xyz[1] + fy * speed
        if can_move_to(nx, ny, player_radius):
            player_xyz[0] = nx
            player_xyz[1] = ny
    elif key == b's':
        nx = player_xyz[0] - fx * speed
        ny = player_xyz[1] - fy * speed
        if can_move_to(nx, ny, player_radius):
            player_xyz[0] = nx
            player_xyz[1] = ny
    elif key == b'd':
        nx = player_xyz[0] - rx * speed
        ny = player_xyz[1] - ry * speed
        if can_move_to(nx, ny, player_radius):
            player_xyz[0] = nx
            player_xyz[1] = ny
    elif key == b'a':
        nx = player_xyz[0] + rx * speed
        ny = player_xyz[1] + ry * speed
        if can_move_to(nx, ny, player_radius):
            player_xyz[0] = nx
            player_xyz[1] = ny

    if player_xyz[0] < boundary_min:
        player_xyz[0] = boundary_min
    elif player_xyz[0] > boundary_max:
        player_xyz[0] = boundary_max

    if player_xyz[1] < boundary_min:
        player_xyz[1] = boundary_min
    elif player_xyz[1] > boundary_max:
        player_xyz[1] = boundary_max

def special_keys(key, x, y):
    global camera_angle, cam_up_down
    if key == GLUT_KEY_UP:
        cam_up_down += 2.0
    elif key == GLUT_KEY_DOWN:
        cam_up_down -= 2.0
    elif key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle - 2.0) % 360.0
    elif key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle + 2.0) % 360.0

def mouse(button, state, x, y):
    global flash_on, view
    if state != GLUT_DOWN:
        return
    if button == GLUT_LEFT_BUTTON:
        flash_on = not flash_on
    elif button == GLUT_RIGHT_BUTTON:
        view = "first_person" if view == "third_person" else "third_person"

def idle():
    global last_time, delta_time
    now = time.time()
    delta_time = now - last_time
    last_time = now
    update_game(delta_time)
    glutPostRedisplay()

def display():
    glViewport(0, 0, win_width, win_height)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    if in_menu:
        draw_menu()
        glutSwapBuffers()
        return
    setup_camera()
    draw_ground()
    draw_structures()
    draw_walls()
    draw_items()
    draw_enemies()
    draw_player()
    mode = "FPV" if view == "first_person" else "TPV"
    draw_text(10, win_height - 25, f"Score: {score}   Lives: {lives}   Battery: {int(flash_battery)}%   Mode: {mode}")
    draw_text(10, win_height - 50, f"Flash(L-click): {'ON' if flash_on else 'OFF'}   Run(x): {'ON' if running else 'OFF'}   Shadows(t): {'ON' if shadows else 'OFF'}")
    if paused:
        draw_text(win_width//2 - 50, win_height//2, "PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
    if game_over:
        draw_text(win_width//2 - 90, win_height//2 + 30, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(win_width//2 - 170, win_height//2, "Press 'r' to restart", GLUT_BITMAP_HELVETICA_18)
    if show_instructions:
        y = win_height - 80
        draw_text(10, y,     "Controls:")
        draw_text(10, y-25,  "WASD move | Arrow keys rotate/tilt | P pause | L-click flashlight | R-click FPV toggle")
        draw_text(10, y-50,  "X run | C god | V vision | O outfit | T shadows | R reset | H help")
    glutSwapBuffers()

def init():
    glClearColor(0.02, 0.02, 0.02, 1.0)
    glEnable(GL_DEPTH_TEST)
    global quadric
    quadric = gluNewQuadric()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(win_width, win_height)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Light & Shadow Game (Inline Math)")
    init()
    spawn_enemies()
    spawn_items()
    spawn_structures()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
