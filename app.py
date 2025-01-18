import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import random
from streamlit_autorefresh import st_autorefresh

# --- Game Constants ---
GRID_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30

# Colors
COLOR_BG = (255, 255, 255)      # White
COLOR_GRID = (200, 200, 200)    # Light Gray
COLOR_SNAKE = (0, 255, 0)       # Green
COLOR_FOOD = (255, 0, 0)        # Red
COLOR_POWERUP = (0, 0, 255)     # Blue
COLOR_TEXT = (0, 0, 0)          # Black

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Power-up types
POWERUP_TYPES = ['shed_tail']

# --- Session State Initialization ---
if 'snake' not in st.session_state:
    st.session_state.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    st.session_state.direction = random.choice([UP, DOWN, LEFT, RIGHT])
    st.session_state.food = (random.randint(0, GRID_WIDTH -1), random.randint(0, GRID_HEIGHT -1))
    st.session_state.powerup = None
    st.session_state.powerup_timer = 0
    st.session_state.score = 0
    st.session_state.game_over = False

# --- Helper Functions ---
def change_direction(new_dir):
    """Change the snake's direction unless it's directly opposite."""
    opposite_dir = (-st.session_state.direction[0], -st.session_state.direction[1])
    if new_dir != opposite_dir:
        st.session_state.direction = new_dir

def move_snake():
    """Move the snake in the current direction."""
    if st.session_state.game_over:
        return

    head_x, head_y = st.session_state.snake[0]
    dir_x, dir_y = st.session_state.direction
    new_head = ((head_x + dir_x), (head_y + dir_y))

    # Check for boundary collision
    if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
        st.session_state.game_over = True
        return

    # Check for collision with self
    if new_head in st.session_state.snake:
        st.session_state.game_over = True
        return

    # Insert new head
    st.session_state.snake.insert(0, new_head)

    # Check for food
    if new_head == st.session_state.food:
        st.session_state.score += 10
        st.session_state.food = generate_food()
        # Reset power-up timer and remove existing power-up
        st.session_state.powerup_timer = 0
        st.session_state.powerup = None
    else:
        # Remove tail
        st.session_state.snake.pop()

    # Power-up Logic
    st.session_state.powerup_timer += 1
    if st.session_state.powerup_timer >= 50 and st.session_state.powerup is None:
        st.session_state.powerup = generate_powerup()
        st.session_state.powerup_timer = 0

    # Check for power-up collection
    if st.session_state.powerup and new_head == st.session_state.powerup['position']:
        apply_powerup(st.session_state.powerup['type'])
        st.session_state.score += 20
        st.session_state.powerup = None

def generate_food():
    """Generate a random position for food not occupied by the snake."""
    while True:
        pos = (random.randint(0, GRID_WIDTH -1), random.randint(0, GRID_HEIGHT -1))
        if pos not in st.session_state.snake:
            return pos

def generate_powerup():
    """Generate a random position for a power-up not occupied by the snake or food."""
    while True:
        pos = (random.randint(0, GRID_WIDTH -1), random.randint(0, GRID_HEIGHT -1))
        if pos not in st.session_state.snake and pos != st.session_state.food:
            powerup_type = random.choice(POWERUP_TYPES)
            return {'position': pos, 'type': powerup_type}

def apply_powerup(powerup_type):
    """Apply the effect of the power-up."""
    if powerup_type == 'shed_tail':
        if len(st.session_state.snake) > 1:
            st.session_state.snake.pop()

def render_game():
    """Render the game grid as an image."""
    img = Image.new('RGB', (GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # Draw grid lines
    for x in range(0, GRID_WIDTH * GRID_SIZE, GRID_SIZE):
        draw.line([(x, 0), (x, GRID_HEIGHT * GRID_SIZE)], fill=COLOR_GRID)
    for y in range(0, GRID_HEIGHT * GRID_SIZE, GRID_SIZE):
        draw.line([(0, y), (GRID_WIDTH * GRID_SIZE, y)], fill=COLOR_GRID)

    # Draw snake
    for segment in st.session_state.snake:
        x, y = segment
        draw.rectangle([x * GRID_SIZE, y * GRID_SIZE, (x +1)*GRID_SIZE, (y +1)*GRID_SIZE], fill=COLOR_SNAKE)

    # Draw food
    fx, fy = st.session_state.food
    draw.rectangle([fx * GRID_SIZE, fy * GRID_SIZE, (fx +1)*GRID_SIZE, (fy +1)*GRID_SIZE], fill=COLOR_FOOD)

    # Draw power-up
    if st.session_state.powerup:
        px, py = st.session_state.powerup['position']
        draw.rectangle([px * GRID_SIZE, py * GRID_SIZE, (px +1)*GRID_SIZE, (py +1)*GRID_SIZE], fill=COLOR_POWERUP)

    return img

def reset_game():
    """Reset the game to initial state."""
    st.session_state.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    st.session_state.direction = random.choice([UP, DOWN, LEFT, RIGHT])
    st.session_state.food = generate_food()
    st.session_state.powerup = None
    st.session_state.powerup_timer = 0
    st.session_state.score = 0
    st.session_state.game_over = False

# --- Streamlit App Layout ---
st.title("Snake Game with Power-ups")

# Display Score
st.write(f"**Score:** {st.session_state.score}")

# Display Game Over
if st.session_state.game_over:
    st.error("Game Over! Press Reset to play again.")

# Render and display the game
img = render_game()
st.image(img)

# Control Buttons
col1, col2, col3 = st.columns(3)
with col2:
    up_button = st.button("⬆️ Up")
with col1:
    left_button = st.button("⬅️ Left")
with col3:
    right_button = st.button("➡️ Right")
with col2:
    down_button = st.button("⬇️ Down")

# Reset Button
st.sidebar.button("🔄 Reset Game", on_click=reset_game)

# Handle Button Presses
if up_button:
    change_direction(UP)
if down_button:
    change_direction(DOWN)
if left_button:
    change_direction(LEFT)
if right_button:
    change_direction(RIGHT)

# Game Loop using Autorefresh
if not st.session_state.game_over:
    move_snake()
    # Refresh every 200 ms
    st_autorefresh(interval=200, limit=None, key="game_loop")
else:
    pass
