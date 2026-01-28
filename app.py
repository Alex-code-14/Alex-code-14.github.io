import streamlit as st
import turtle
import random
import math
import time

# =====================
# CONFIG
# =====================
WIDTH, HEIGHT = 900, 650
FPS = 60
FRAME_MS = int(1000 / FPS)

PLAYER_SPEED = 180
TURN_SPEED = 180
PICKUP_DIST = 26
FLOWER_GOAL = 20
JUMP_VEL = 420
GRAVITY = 1200

# =====================
# SCREEN
# =====================
screen = turtle.Screen()
screen.setup(WIDTH, HEIGHT)
screen.title("Turtle Flower Quest 🌸")
screen.bgcolor("#fff8b0")  # light yellow
screen.tracer(0)

# =====================
# STATE
# =====================
state = {
    "mode": "menu",   # menu | game | deliver | win | inventory
    "flowers": 0,
    "last_time": time.perf_counter(),
    "keys": {"w": False, "a": False, "s": False, "d": False},
    "jumping": False,
    "jump_v": 0.0,
    "jump_y": 0.0,
    "dialog_text": "",
    "dialog_target": "",
    "dialog_index": 0,
    "dialog_timer": 0.0,
    "flowers_list": [],
    "hearts_list": []
}

# =====================
# TURTLES
# =====================
ui = turtle.Turtle(visible=False)
ui.penup()

dialog = turtle.Turtle(visible=False)
dialog.penup()

player = turtle.Turtle("turtle")
player.color("#43f06b")
player.penup()
player.hideturtle()
player.setheading(90)

npc = turtle.Turtle("turtle")
npc.color("#7ed1f5")  # light blue
npc.penup()
npc.hideturtle()
npc.setheading(270)
player.shapesize(stretch_wid=2, stretch_len=2)  # Bigger player turtle
npc.shapesize(stretch_wid=2, stretch_len=2)     # Bigger NPC turtle

# =====================
# FLOWER EMOJIS
# =====================
def create_flower(x, y):
    f = turtle.Turtle(visible=False)
    f.penup()
    f.goto(x, y)
    f.color(random.choice(["#ff6fd8","#ff4444","#fff04d"]))
    f.write(random.choice(["🌸","🌸"]), align="center", font=("Arial", 24, "normal"))
    f.emoji = True
    return f

def spawn_flower():
    x = random.randint(-360, 360)
    y = random.randint(-260, 260)
    f = create_flower(x, y)
    state["flowers_list"].append(f)

# =====================
# HEART EMOJIS
# =====================
def create_heart(x, y):
    h = turtle.Turtle(visible=False)
    h.penup()
    h.goto(x, y)
    h.color("red")
    h.write("❤️", align="center", font=("Arial", 16, "normal"))
    h.dx = random.uniform(-20, 20)
    h.dy = random.uniform(30, 80)
    state["hearts_list"].append(h)

def spawn_heart_particles(x, y, count=15):
    for _ in range(count):
        create_heart(x, y)

# =====================
# DIALOGUE
# =====================
def set_dialogue(text):
    state["dialog_target"] = text
    state["dialog_text"] = ""
    state["dialog_index"] = 0
    state["dialog_timer"] = 0.0

def update_dialogue(dt):
    if state["dialog_index"] < len(state["dialog_target"]):
        state["dialog_timer"] += dt
        if state["dialog_timer"] > 0.035:
            state["dialog_text"] += state["dialog_target"][state["dialog_index"]]
            state["dialog_index"] += 1
            state["dialog_timer"] = 0.0

    dialog.clear()
    dialog.goto(npc.xcor(), npc.ycor() + 50)
    dialog.color("black")
    dialog.write(state["dialog_text"], align="center", font=("Arial", 14, "normal"))

# =====================
# MENU
# =====================
def draw_menu():
    ui.clear()
    ui.goto(0, 120)
    ui.color("black")
    ui.write("TURTLE FLOWER QUEST", align="center",
             font=("Arial", 32, "bold"))

    ui.goto(0, 50)
    ui.write("Collect flowers 🌸 and help your friend!",
             align="center", font=("Arial", 18, "normal"))

    ui.goto(-120, -120)
    ui.color("#3fa9f5")
    ui.begin_fill()
    for _ in range(2):
        ui.forward(240)
        ui.right(90)
        ui.forward(60)
        ui.right(90)
    ui.end_fill()

    ui.goto(0, -155)
    ui.color("black")
    ui.write("PLAY", align="center", font=("Arial", 22, "bold"))

# =====================
# START GAME
# =====================
def start_game(x=None, y=None):
    ui.clear()
    dialog.clear()
    state["mode"] = "game"
    state["flowers"] = 0

    for f in state["flowers_list"]:
        f.clear()
    state["flowers_list"].clear()

    for _ in range(12):
        spawn_flower()

    player.goto(0, -200)
    player.showturtle()

    npc.goto(0, 220)
    npc.showturtle()

    set_dialogue("Please bring me 20 flowers 🌸")

# =====================
# HUD
# =====================
def draw_hud():
    ui.clear()
    ui.goto(-WIDTH//2 + 20, HEIGHT//2 - 40)
    ui.color("black")
    ui.write(f"🌸 {state['flowers']} / {FLOWER_GOAL}",
             align="left", font=("Arial", 18, "bold"))
    ui.goto(WIDTH//2 - 180, HEIGHT//2 - 40)
    ui.write("I = Pause", align="left", font=("Arial", 12, "normal"))

# =====================
# PLAYER MOVEMENT + JUMP
# =====================
def clamp(x, y):
    mx = WIDTH//2 - 40
    my = HEIGHT//2 - 40
    return max(-mx, min(mx, x)), max(-my, min(my, y))

def update_player(dt):
    if state["keys"]["a"]:
        player.left(TURN_SPEED * dt)
    if state["keys"]["d"]:
        player.right(TURN_SPEED * dt)

    if state["keys"]["w"]:
        dx = math.cos(math.radians(player.heading())) * PLAYER_SPEED * dt
        dy = math.sin(math.radians(player.heading())) * PLAYER_SPEED * dt
        x, y = clamp(player.xcor() + dx, player.ycor() + dy)
        player.goto(x, y)

    if state["jumping"]:
        state["jump_v"] -= GRAVITY * dt
        state["jump_y"] += state["jump_v"] * dt
        if state["jump_y"] <= 0:
            state["jump_y"] = 0
            state["jumping"] = False
            state["jump_v"] = 0

    player.sety(player.ycor() + state["jump_y"] * dt)

# =====================
# FLOWERS
# =====================
def update_flowers(dt):
    pass  # emoji flowers don't animate

def check_flowers():
    for f in state["flowers_list"][:]:
        if player.distance(f) < PICKUP_DIST:
            f.clear()
            state["flowers_list"].remove(f)
            state["flowers"] += 1
            spawn_flower()

# =====================
# DELIVERY + END
# =====================
def check_delivery():
    if state["flowers"] >= FLOWER_GOAL and player.distance(npc) < 40:
        state["mode"] = "win"
        set_dialogue("Thank you! Let's celebrate! ❤️")
        spawn_heart_particles(npc.xcor(), npc.ycor(), 15)

def update_win(dt):
    for h in state["hearts_list"][:]:
        h.sety(h.ycor() + h.dy * dt)
        h.setx(h.xcor() + h.dx * dt)
        h.dy -= 150 * dt
        if h.ycor() < -HEIGHT//2 - 20:
            h.clear()
            state["hearts_list"].remove(h)

# =====================
# MAIN LOOP
# =====================
def update():
    now = time.perf_counter()
    dt = now - state["last_time"]
    state["last_time"] = now

    if state["mode"] == "game":
        update_player(dt)
        update_flowers(dt)
        check_flowers()
        check_delivery()
        draw_hud()
        update_dialogue(dt)
    elif state["mode"] == "inventory":
        draw_hud()
    elif state["mode"] == "win":
        update_dialogue(dt)
        update_win(dt)

    screen.update()
    screen.ontimer(update, FRAME_MS)

# =====================
# INPUT
# =====================
def key_down(k):
    if k == "space" and not state["jumping"]:
        state["jumping"] = True
        state["jump_v"] = JUMP_VEL
    elif k == "i":
        state["mode"] = "inventory" if state["mode"] == "game" else "game"
    else:
        state["keys"][k] = True

def key_up(k):
    if k in state["keys"]:
        state["keys"][k] = False

screen.listen()
for k in ("w", "a", "s", "d"):
    screen.onkeypress(lambda k=k: key_down(k), k)
    screen.onkeyrelease(lambda k=k: key_up(k), k)

screen.onkeypress(lambda: key_down("space"), "space")
screen.onkeypress(lambda: key_down("i"), "i")
screen.onclick(start_game)

# =====================
# BOOT
# =====================
draw_menu()
update()
screen.mainloop()

# =====================
# MOBILE JOYSTICK SUPPORT
# =====================
canvas = screen.getcanvas()
screen_width = WIDTH
screen_height = HEIGHT

# Define joystick areas (simple rectangles)
JOYSTICK_SIZE = 150  # size of touch areas

def mobile_press(event):
    x = event.x - screen_width // 2
    y = screen_height // 2 - event.y
    # Up
    if -JOYSTICK_SIZE < x < JOYSTICK_SIZE and 0 < y < JOYSTICK_SIZE:
        state["keys"]["w"] = True
    # Down
    elif -JOYSTICK_SIZE < x < JOYSTICK_SIZE and -JOYSTICK_SIZE < y < 0:
        state["keys"]["s"] = True
    # Left
    elif -JOYSTICK_SIZE < x < 0 and -JOYSTICK_SIZE < y < JOYSTICK_SIZE:
        state["keys"]["a"] = True
    # Right
    elif 0 < x < JOYSTICK_SIZE and -JOYSTICK_SIZE < y < JOYSTICK_SIZE:
        state["keys"]["d"] = True

def mobile_release(event):
    x = event.x - screen_width // 2
    y = screen_height // 2 - event.y
    # Up
    if -JOYSTICK_SIZE < x < JOYSTICK_SIZE and 0 < y < JOYSTICK_SIZE:
        state["keys"]["w"] = False
    # Down
    elif -JOYSTICK_SIZE < x < JOYSTICK_SIZE and -JOYSTICK_SIZE < y < 0:
        state["keys"]["s"] = False
    # Left
    elif -JOYSTICK_SIZE < x < 0 and -JOYSTICK_SIZE < y < JOYSTICK_SIZE:
        state["keys"]["a"] = False
    # Right
    elif 0 < x < JOYSTICK_SIZE and -JOYSTICK_SIZE < y < JOYSTICK_SIZE:
        state["keys"]["d"] = False

canvas.bind("<ButtonPress-1>", mobile_press)
canvas.bind("<ButtonRelease-1>", mobile_release)

