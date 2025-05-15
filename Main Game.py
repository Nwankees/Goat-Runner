import pygame
import random
from pygame import K_ESCAPE, K_p, K_m, K_r, K_q, K_SPACE
import os

# --- Constants & Initialization ---
GAME_TITLE = "Goat Runner"
pygame.init()
pygame.mixer.init() # Initialize the mixer

# +++ Load and Setup Music +++
try:
    pygame.mixer.music.load('Sound/background_music.mp3')
    pygame.mixer.music.set_volume(0.4)
    print("Background music loaded.")
except pygame.error as e:
    print(f"Warning: Could not load background music 'bg_music.mp3': {e}")

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_TITLE)
clock = pygame.time.Clock()
pygame.event.set_blocked(None)
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP,
                          pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION])

# --- Colors & Fonts ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
GRAY = (200, 200, 200)
PEACH = (254, 251, 234)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
TITLE_COLOR = (70, 70, 70)
PAUSE_OVERLAY_COLOR = (0, 0, 0, 150)
font = pygame.font.Font('Fonts/PressStart2P-Regular.ttf', 18)
small_font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 72)
try:
    select_font = pygame.font.Font('Fonts/PressStart2P-Regular.ttf', 36)
except pygame.error as e:
    print(f"Error loading custom font: {e}. Using default font for selection title.")
    select_font = pygame.font.Font(None, 48)
try:
    title_font = pygame.font.Font('Fonts/PressStart2P-Regular.ttf', 48)
except pygame.error as e:
    print(f"Error loading custom font: {e}. Using default font for title.")
    title_font = pygame.font.Font(None, 60)


#Assets (Images & Sounds)
def load_and_extract_frames(sheet_path, frame_w, frame_h, num_frames):
    """Load our sprite sheet and dets the frames."""
    sheet = pygame.image.load(sheet_path).convert_alpha()
    frames = []
    for i in range(num_frames):
        rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
        frame = sheet.subsurface(rect)
        frame = frame.subsurface(frame.get_bounding_rect())
        frames.append(frame)
       #frames.append(frame)
    return frames

#Goat Constants
GOAT_FRAME_W = 24
GOAT_FRAME_H = 24
GOAT_IDLE_FRAMES_COUNT = 4
GOAT_RUN_FRAMES_COUNT = 6
GOAT_COLORS = ['black']

# --- Load Goat Animations ---
goat_animations = {
    'black': {
        'idle': load_and_extract_frames(
            "Sprites/Idle/black_idle.png",
            GOAT_FRAME_W, GOAT_FRAME_H, GOAT_IDLE_FRAMES_COUNT
        ),
        'running': load_and_extract_frames(
            "Sprites/Running/black_running.png",
            GOAT_FRAME_W, GOAT_FRAME_H, GOAT_RUN_FRAMES_COUNT
        )
    }
}

#SCALE UP ALL GOAT FRAMES
SCALE_FACTOR = 2

# Scale idle frames
scaled_idle_frames = []
for frame in goat_animations['black']['idle']:
    scaled_frame = pygame.transform.scale(
        frame, (GOAT_FRAME_W * SCALE_FACTOR, GOAT_FRAME_H * SCALE_FACTOR)
    )
    scaled_idle_frames.append(scaled_frame)
goat_animations['black']['idle'] = scaled_idle_frames

# Scale running frames
scaled_running_frames = []
for frame in goat_animations['black']['running']:
    scaled_frame = pygame.transform.scale(
        frame, (GOAT_FRAME_W * SCALE_FACTOR, GOAT_FRAME_H * SCALE_FACTOR)
    )
    scaled_running_frames.append(scaled_frame)
goat_animations['black']['running'] = scaled_running_frames

GOAT_FRAME_W *= SCALE_FACTOR
GOAT_FRAME_H *= SCALE_FACTOR


#Our other files
bg_image = pygame.image.load('Images/main_menu.jpg').convert()
menu_bg = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
stone_img_raw = pygame.image.load('Images/stone.png').convert_alpha()
stone_img = pygame.transform.smoothscale(stone_img_raw, (300, 80))
cactus_imgs = []

for file in ('Obstacles/1 cactus.png', 'Obstacles/2 cacti.png', 'Obstacles/3 cacti.png'):
    img = pygame.image.load(file).convert_alpha()
    surf = pygame.transform.smoothscale(img, (90, 60)).copy()
    #crop vertically
    bbox = surf.get_bounding_rect()
    surf = surf.subsurface(pygame.Rect(0, bbox.y, surf.get_width(), bbox.height))
    cactus_imgs.append(surf)

HITBOX_INFLATIONS = [(-45, -5), (-40, -8), (-35, -10)] #The hitboxes were too big for cactus 1 to 3

#pOWER Up Images
super_jump_img = pygame.transform.smoothscale(pygame.image.load('Power Ups/super_jump.png').convert_alpha(), (60, 60))
double_jump_img = pygame.transform.smoothscale(pygame.image.load('Power Ups/double_jump.png').convert_alpha(), (60, 60))
revive_img = pygame.transform.smoothscale(pygame.image.load('Power Ups/revive.png').convert_alpha(), (60, 60))

#Sounds
jump_sound = pygame.mixer.Sound('Sound/jumping_sound.wav')
jump_sound.set_volume(1.0)
click_sound = pygame.mixer.Sound('Sound/click_sound.wav')
unavailable_sound = pygame.mixer.Sound('Sound/click_sound.wav')
unavailable_sound.set_volume(2.5)
revive_sound1 = pygame.mixer.Sound('Sound/revive.mp3')
revive_sound2 = pygame.mixer.Sound('Sound/ahhyooaaawhoaaa.mp3')


#File Handling
high_score_file = "Save Files/highscore.txt"
coin_file = "Save Files/coins.txt"
def load_value(filename, default=0):
    try:
        with open(filename, "r") as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return default

def save_value(filename, value):
    try:
        with open(filename, "w") as f:
            f.write(str(value))
    except IOError as e:
        print(f"Error saving value to {filename}: {e}")

score = 0
high_score = load_value(high_score_file)
total_coins = load_value(coin_file)
coins_at_round_start = 0 # This will change when game starts
deaths = 0
powerups = {
    'super_jump': {'price': 100, 'unlocked': False, 'enabled': False, 'img': super_jump_img},
    'double_jump': {'price': 200, 'unlocked': False, 'enabled': False, 'used': False, 'img': double_jump_img},
    'revive': {'price': 1000, 'unlocked': False, 'available': False, 'used': False, 'img': revive_img},
}

#UI Elements
BTN_W, BTN_H = 300, 80
play_rect = stone_img.get_rect(center=(WIDTH//2, HEIGHT//2 - BTN_H*0.8 + 50))
shop_rect = stone_img.get_rect(center=(WIDTH//2 - 160, HEIGHT//2 + BTN_H*0.3 + 50 ))
quit_rect = stone_img.get_rect(center=(WIDTH//2, HEIGHT//2 + BTN_H*1.4 + 50))
instr_rect = stone_img.get_rect(center=(WIDTH//2 + 160, HEIGHT//2 + BTN_H*0.3 + 50 ))
#stone_img.get_rect(bottomright=(WIDTH-10, HEIGHT-10))

play_text = font.render('Play', True, BLACK)
shop_text = font.render('Shop', True, BLACK)
quit_text = font.render('Quit', True, BLACK)
instr_text = font.render('Instructions', True, BLACK)

#Game Objects&Player Variables
ground_h = 50
player_rect = None # Will be initialized in reset_game
player_vel_y = 0
is_jumping = False
selected_goat_color = GOAT_COLORS[0]  # Default goat color set to the first in the list
player_run_frames = []
player_jump_frame = None
player_current_frame_index = 0
player_animation_timer = 0
PLAYER_ANIMATION_SPEED = 3

# Ground, Clouds, Obstacles
ground_rects = [pygame.Rect(i * 100, HEIGHT - ground_h, 100, ground_h) for i in range(WIDTH // 100 + 1)]
clouds = [pygame.Rect(random.randint(0, WIDTH), random.randint(20, 120), 60, 30) for _ in range(8)]
obstacles = []

#Shop Variables
shop_msg = ""
shop_item_rects = {}
shop_back_rect = None

#Game States
game_state = 'menu'
end_message = ""
fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.fill((0, 0, 0))
fade_alpha = 0
pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
pause_overlay.fill(PAUSE_OVERLAY_COLOR)

#Functions
def deactivate_powerups():
    powerups['super_jump']['enabled'] = False
    powerups['double_jump']['enabled'] = False
    powerups['double_jump']['used'] = False
    powerups['revive']['available'] = False
    powerups['revive']['used'] = False


def reset_game():
    """Resets game"""
    global score, obstacles, clouds, player_rect, is_jumping, player_vel_y
    global powerups, coins_at_round_start, total_coins, game_state, fade_alpha
    global player_run_frames, player_jump_frame, player_current_frame_index, player_animation_timer

    score = 0
    coins_at_round_start = total_coins  # Record coins at the start of this round

    player_frame_w = GOAT_FRAME_W
    player_frame_h = GOAT_FRAME_H
    # Initial player position
    player_rect = pygame.Rect(100, HEIGHT - ground_h - player_frame_h, player_frame_w, player_frame_h)
    player_vel_y = 0
    is_jumping = False

    player_run_frames = goat_animations[selected_goat_color]['running']
    # Use the first frame of the running animation for jumping pose
    player_jump_frame = player_run_frames[0]

    player_current_frame_index = 0
    player_animation_timer = 0

    obstacles.clear()
    # Reset clouds to random positions
    clouds[:] = [pygame.Rect(random.randint(0, WIDTH), random.randint(20, 120), 60, 30) for _ in range(8)]
    fade_alpha = 0  # Reset fade effect if any

    # Reset powerup status for the new round
    if powerups['super_jump']['unlocked']:
        powerups['super_jump']['enabled'] = True
    if powerups['double_jump']['unlocked']:
        powerups['double_jump']['enabled'] = True
    if powerups['revive']['unlocked']:
        powerups['revive']['available'] = True
    # Reset used status
    powerups['double_jump']['used'] = False
    powerups['revive']['used'] = False


#Main Loop
running = True
while running:
    game_ended_this_frame = False  # Add this line
    # Calculate coins to display
    if game_state == 'playing':
         coins_this_round = int(score * 0.5) # Example coin earning logic, we can make economy rough by setting this lower lol
         display_coins = coins_at_round_start + coins_this_round
    else:
         display_coins = total_coins # Show saved total

    events = pygame.event.get() # Get the events ONCE per frame for all states

    #Global Event Handling
    for e in events:
        if e.type == pygame.QUIT: running = False
        if e.type == pygame.KEYDOWN:
            if e.key == K_ESCAPE: running = False # our quit shortcut


    #States
    if game_state == 'menu':
        # Start music in menu if not already playing
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

        for e in events: # Menu specific events
             if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1: # Left click
                click_sound.play()
                if play_rect.collidepoint(e.pos):
                    reset_game()  # Initialize game with the default goat
                    game_state = 'playing'
                elif shop_rect.collidepoint(e.pos):
                     shop_msg = "" # Reset shop message
                     game_state = 'shop'
                elif quit_rect.collidepoint(e.pos):
                     running = False
                elif instr_rect.collidepoint(e.pos):
                    click_sound.play()
                    game_state = 'instructions'

        #Drawing the Menu
        screen.blit(menu_bg, (0, 0))
        title_surf = title_font.render(GAME_TITLE, True, TITLE_COLOR)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_surf, title_rect)
        # Draw buttons (stone image + text centered on it)
        for btn, text, rect in [(stone_img, play_text, play_rect),
                                (stone_img, shop_text, shop_rect),
                                (stone_img, quit_text, quit_rect),
                                (stone_img, instr_text, instr_rect)]:
            screen.blit(btn, rect)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)


    elif game_state == 'shop':
        #Shop Logic & Drawing
        shop_item_rects.clear() # Clear rects from previous frame

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                clicked_item = False
                # Check powerup clicks
                for i, (name, p) in enumerate(powerups.items()):
                    x = (WIDTH // 4) * (i + 1)
                    img_rect = p['img'].get_rect(center=(x, HEIGHT // 2 - 30))
                    shop_item_rects[name] = img_rect # Store rect for drawing
                    if not p['unlocked'] and img_rect.collidepoint(e.pos):
                        clicked_item = True
                        if total_coins >= p['price']:
                            click_sound.play()
                            total_coins -= p['price']
                            p['unlocked'] = True
                            save_value(coin_file, total_coins)
                            shop_msg = f"{name.replace('_', ' ').title()} Purchased!"
                            print(f"Purchased {name}")
                        else:
                            unavailable_sound.play()
                            shop_msg = "Not enough coins!"
                        break

                # Check back button click
                if not clicked_item and shop_back_rect and shop_back_rect.collidepoint(e.pos):
                    click_sound.play()
                    game_state = 'menu'
                    deaths = 0

        #Drawing the shop
        screen.fill(PEACH) # Shop background

        # Draw Shop Title
        shop_surf = title_font.render("Power-Up Shop", True, TITLE_COLOR)
        screen.blit(shop_surf, shop_surf.get_rect(center=(WIDTH // 2, 60)))

        # Draw Coin Count
        coin_text_shop = font.render(f"Coins: {total_coins}", True, TITLE_COLOR)
        screen.blit(coin_text_shop, coin_text_shop.get_rect(topright=(WIDTH - 20, 20)))

        # Draw Power-ups
        any_powerup_unlocked = any(p.get('unlocked', False) for p in powerups.values())
        for i, (name, p) in enumerate(powerups.items()):
            x = (WIDTH // 4) * (i + 1) # Position items across the screen
            # Get/calculate rect
            img_rect = shop_item_rects.get(name)
            if not img_rect:
                img_rect = p['img'].get_rect(center=(x, HEIGHT // 2 - 30))

            # Draw item image
            screen.blit(p['img'], img_rect)

            # Draw item name
            name_text = small_font.render(name.replace('_', ' ').title(), True, TITLE_COLOR)
            name_rect = name_text.get_rect(center=(x, HEIGHT // 2 + 30))
            screen.blit(name_text, name_rect)

            # Draw price/status
            if p['unlocked']:
                label = small_font.render("Unlocked", True, (0, 150, 0)) # Green
            else:
                label = small_font.render(f"Cost: {p['price']}", True, TITLE_COLOR)
            label_rect = label.get_rect(center=(x, HEIGHT // 2 + 60))
            screen.blit(label, label_rect)

            # Draw buy button area (optional visual cue)
            if not p['unlocked']:
                button_color = GRAY if total_coins < p['price'] else (100, 200, 100) # Lighter green if affordable
                buy_button_visual_rect = img_rect.inflate(10, 60)
                #pygame.draw.rect(screen, button_color, buy_button_visual_rect, 2, border_radius=5) #N/B I think we will have to scrap this


        # Display Shop Message
        if shop_msg:
            shop_msg_surf = small_font.render(shop_msg, True, RED if "Not enough" in shop_msg else TITLE_COLOR)
            shop_msg_rect = shop_msg_surf.get_rect(center=(WIDTH // 2, HEIGHT - 80))
            screen.blit(shop_msg_surf, shop_msg_rect)

        # Draw Back Button
        back_text = font.render("Back to Menu", True, WHITE)
        # Use a simple rect for the back button background
        back_button_bg_rect = pygame.Rect(0, 0, 250, 50)
        back_button_bg_rect.center = (WIDTH // 2, HEIGHT - 40)
        pygame.draw.rect(screen, TITLE_COLOR, back_button_bg_rect, border_radius=10)
        # Center text on the button bg
        back_text_rect = back_text.get_rect(center=back_button_bg_rect.center)
        screen.blit(back_text, back_text_rect)
        shop_back_rect = back_button_bg_rect # Store for click detection

    elif game_state == 'instructions':
        screen.fill(PEACH)
        lines = [
            "HOW TO PLAY Goat Runner:",
            "- PRESS SPACE to jump.",
            "- Earn 0.5 coins per point of score.",
            "    *Dont complain we can make the economy",
            "     harder if we want",
            "- BUY one power-up in shop:",
            "    * Super Jump: higher first jump",
            "    * Double Jump: extra mid-air jump",
            "    * Revive: auto-revive once per run",
            "- PAUSE with P, Resume with P.",
            "- BACK to Menu with M key or click back button.",
        ]
        for i, line in enumerate(lines):
            txt = font.render(line, True, TITLE_COLOR)
            screen.blit(txt, (40, 40 + i * 30))
        # draw a “Back” button
        back_btn = pygame.Rect(WIDTH - 140, HEIGHT - 60, 120, 40)
        pygame.draw.rect(screen, TITLE_COLOR, back_btn, border_radius=5)
        back_txt = small_font.render("Back", True, WHITE)
        screen.blit(back_txt, back_txt.get_rect(center=back_btn.center))
        instr_back_rect = back_btn

        # flip + tick
        pygame.display.flip()
        clock.tick(60)

        # catch back click or M key
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == K_m:
                game_state = 'menu'
                deaths = 0
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if instr_back_rect.collidepoint(e.pos):
                    click_sound.play()
                    game_state = 'menu'
                    deaths = 0

    elif game_state == 'playing':
        # Ensure player is initialized
        player_hitbox = player_rect.copy()
        player_hitbox.x += 20 // 2
        player_hitbox.width -= 20
        game_ended_this_frame = False # A fix to prevent drawing/ticking after the game ends

        #Event Handling for Playing
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == K_p:
                    game_state = 'paused'
                    pygame.mixer.music.pause() # Pause music
                elif e.key == K_SPACE:
                    # Handle jump / double jump
                    player_frame_h = GOAT_FRAME_H # Use constant height
                    if not is_jumping: # First jump
                        is_jumping = True
                        jump_power = -23 if powerups['super_jump']['enabled'] else -16
                        player_vel_y = jump_power
                        jump_sound.play()
                    elif powerups['double_jump']['enabled'] and not powerups['double_jump']['used']:
                        # Double jump
                        player_vel_y = -10 # Double jump power
                        jump_sound.play()
                        powerups['double_jump']['used'] = True

        #Game Updates
        score += 0.05

        # Win Condition Check (Reach score 80)
        WIN_SCORE = 80
        if int(score) >= WIN_SCORE:
            final_coins_earned = int(score * 0.5) # Calculate final coins
            total_coins = coins_at_round_start + final_coins_earned
            high_score = max(high_score, int(score))
            save_value(high_score_file, high_score)
            save_value(coin_file, total_coins)
            fade_alpha = 0 # Reset fade for win screen
            game_state = 'win'
            game_ended_this_frame = True
            pygame.mixer.music.stop() # Stop music on win
            print("YOU WIN!")


        #Physics & Movement (Only if game didn't end)
        if not game_ended_this_frame:
            player_frame_h = GOAT_FRAME_H # Use constant height
            if is_jumping:
                player_rect.y += player_vel_y
                player_vel_y += 1 # Gravity effect
                # Check if landed
                if player_rect.bottom >= HEIGHT - ground_h:
                    player_rect.bottom = HEIGHT - ground_h
                    is_jumping = False
                    player_vel_y = 0
                    powerups['double_jump']['used'] = False # Reset double jump on landing
            else:
                 player_rect.bottom = HEIGHT - ground_h

            # Update Player Animation
            if not is_jumping:
                player_animation_timer += 1
                if player_animation_timer >= PLAYER_ANIMATION_SPEED:
                    player_animation_timer = 0
                    player_current_frame_index = (player_current_frame_index + 1) % len(player_run_frames)

            # Environment Movement (Ground, Clouds, Obstacles)
            for gr in ground_rects:
                gr.x -= 4 # Ground scroll speed
            # Loop ground tiles
            if ground_rects[0].right <= 0:
                 ground_rects.append(ground_rects.pop(0))
                 ground_rects[-1].left = ground_rects[-2].right
            for c in clouds:
                c.x -= 9 # Cloud scroll speed. Yo put it at 20 and you will see MAIDEN HEAVEN!!
            # Loop clouds
            if c.right < 0:
                 c.x = WIDTH + random.randint(0, 100)
                 c.y = random.randint(20, 120)
            CLOUD_SPAWN_CHANCE = 0.02
            if random.random() < CLOUD_SPAWN_CHANCE:
                clouds.append(pygame.Rect(WIDTH,
                                          random.randint(20, 120),
                                          60, 30))

            # Spawn Obstacles
            OBSTACLE_SPAWN_RATE = 2 # Lower = more frequent
            MIN_OBSTACLE_DISTANCE = 50
            MAX_OBSTACLE_DISTANCE = 400
            if random.randint(1, 100) > OBSTACLE_SPAWN_RATE and \
               (not obstacles or WIDTH - obstacles[-1]['rect'].right > random.randint(MIN_OBSTACLE_DISTANCE, MAX_OBSTACLE_DISTANCE)):
                 # Choose cactus type (weights can adjust frequency)
                 idx = random.choices([0, 1, 2], weights=[50, 30, 20])[0]
                 if idx < len(cactus_imgs): # Safety check
                     img = cactus_imgs[idx]
                     # Position new obstacle off-screen to the right
                     rect = img.get_rect(midbottom=(WIDTH + 50, HEIGHT - ground_h))
                     # Get corresponding hitbox inflation
                     infl = HITBOX_INFLATIONS[idx]
                     obstacles.append({'img': img, 'rect': rect, 'infl': infl})

            # Move existing obstacles and remove off-screen ones
            OBSTACLE_SPEED = 5
            new_obs_list = []
            for obs in obstacles:
                obs['rect'].x -= OBSTACLE_SPEED
                if obs['rect'].right >= 0: # Keep if still on screen
                    new_obs_list.append(obs)
            obstacles = new_obs_list # Update obstacle list

            #Drawing Playing State
            screen.fill(SKY_BLUE)
            pygame.draw.circle(screen, (255, 223, 0), (WIDTH - 60, 60), 40)
            # Draw Ground
            for gr in ground_rects: pygame.draw.rect(screen, BROWN, gr)
            # Draw Clouds
            for c in clouds:
                pygame.draw.rect(screen, GRAY, c)
            # Draw Obstacles
            for obs in obstacles: screen.blit(obs['img'], obs['rect'])

            # Draw Score, High Score, Coins
            screen.blit(font.render(f"Score: {int(score)}", True, WHITE), (10, 10))
            screen.blit(font.render(f"High Score: {int(high_score)}", True, WHITE), (10, 40))
            screen.blit(font.render(f"Deaths: {deaths}", True, WHITE), (10, 70))
            screen.blit(font.render(f"Coins: {display_coins}", True, WHITE), (WIDTH - 160, 10))

            # Draw Current Player Frame
            if player_run_frames:
                if is_jumping and player_jump_frame:
                    current_player_image = player_jump_frame
                elif not is_jumping:
                    current_player_image = player_run_frames[player_current_frame_index]
                else: # Fallback if something unexpected happens. fix
                    current_player_image = player_run_frames[0]
                screen.blit(current_player_image, player_rect.topleft)
            else:
                # Fallback: Draw a red rectangle if animations failed to load. fix
                pygame.draw.rect(screen, RED, player_rect)

            #Collision Detection & Lose Condition
            for obs in obstacles:
                 # Inflate the visual rect to get the actual hitbox
                 hitbox = obs['rect'].inflate(*obs['infl'])
                 #This is our debugging rects(to help us view collision)
                 #pygame.draw.rect(screen, RED, hitbox, 1)
                 #pygame.draw.rect(screen, GREEN, player_hitbox, 1)

                 if player_hitbox.colliderect(hitbox):
                    # Check if revive is available and not used yet this round
                    can_revive = powerups['revive'].get('available', False) and not powerups['revive'].get('used', False)
                    if can_revive:
                         powerups['revive']['used'] = True
                         powerups['revive']['available'] = False # Can't use again this round
                         obstacles.remove(obs) # Remove the obstacle that was hit
                         print("REVIVED!")
                         revive_sound1.play()
                         revive_sound2.play()
                    else:
                         # Game Over
                         final_coins_earned = int(score * 0.5) # Calculate final coins
                         total_coins = coins_at_round_start + final_coins_earned
                         high_score = max(high_score, int(score))
                         save_value(high_score_file, high_score)
                         save_value(coin_file, total_coins)
                         end_message = "Game Over!"
                         fade_alpha = 0 # Reset fade for game over screen
                         game_state = 'game_over'
                         game_ended_this_frame = True
                         pygame.mixer.music.stop() # Stop music on death
                         print("GAME OVER!")
                         break # Exit

            # Only flip display and tick clock if game didn't end this frame
            if not game_ended_this_frame:
                pygame.display.flip()
                clock.tick(60)


    elif game_state == 'paused':
        #Paused Logic & Drawing
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == K_p: # Resume
                    game_state = 'playing'
                    pygame.mixer.music.unpause() # Resume music
                elif e.key == K_m: # Back to Menu
                     click_sound.play()
                     game_state = 'menu'
                     deaths = 0
                     deactivate_powerups() # Turn off active powerups
                     # Music will restart in the menu state loop
                elif e.key == K_q: # Quit Game
                     running = False
            # Mouse clicks for pause menu buttons (optional)
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                 # Define resume_text_rect, menu_text_rect, quit_text_rect before this
                 if resume_text_rect.collidepoint(e.pos):
                     game_state = 'playing'
                     pygame.mixer.music.unpause()
                 elif menu_text_rect.collidepoint(e.pos):
                     click_sound.play()
                     game_state = 'menu'
                     deaths = 0
                     deactivate_powerups()
                 elif quit_text_rect.collidepoint(e.pos):
                     running = False


        # --- Drawing Pause Screen ---
        # (Draw the last 'playing' frame underneath - screen is not cleared) fix
        screen.blit(pause_overlay, (0, 0)) # Draw semi-transparent overlay

        # Prepare text surfaces
        paused_text_surf = large_font.render("PAUSED", True, WHITE)
        resume_text_surf = font.render("Resume (P)", True, WHITE)
        menu_text_surf = font.render("Menu (M)", True, WHITE)
        quit_text_surf = font.render("Quit (Q)", True, WHITE)

        # Calculate text rects for positioning and potential clicking
        paused_text_rect = paused_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        resume_text_rect = resume_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        menu_text_rect = menu_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        quit_text_rect = quit_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

        # Blit text onto the screen
        screen.blit(paused_text_surf, paused_text_rect)
        screen.blit(resume_text_surf, resume_text_rect)
        screen.blit(menu_text_surf, menu_text_rect)
        screen.blit(quit_text_surf, quit_text_rect)


    elif game_state == 'game_over':
        #Game Over Logic & Drawing
        # Fade in effect
        if fade_alpha < 180:
            fade_alpha = min(fade_alpha + 15, 180)
            fade_surface.set_alpha(fade_alpha)

        for e in events:
             if e.type == pygame.KEYDOWN:
                 if e.key == K_r: # Restart
                     deaths += 1
                     click_sound.play()
                     reset_game() # Reset variables
                     game_state = 'playing'
                     # Start music again for new game
                     if not pygame.mixer.music.get_busy():
                          try: pygame.mixer.music.play(-1)
                          except pygame.error as err: print(f"Error starting music on restart: {err}")
                 elif e.key == K_m: # Menu
                     click_sound.play()
                     game_state = 'menu'
                     deaths = 0
                     deactivate_powerups() # Ensure powerups are off
                     # Music will restart in menu loop
                 elif e.key == K_q: # Quit
                     running = False
             elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                 # Define restart_text_rect, menu_text_rect, quit_text_rect before this
                 if restart_text_rect.collidepoint(e.pos):
                     click_sound.play()
                     reset_game()
                     game_state = 'playing'
                     if not pygame.mixer.music.get_busy():
                         pygame.mixer.music.play(-1)
                 elif menu_text_rect.collidepoint(e.pos):
                     click_sound.play()
                     game_state = 'menu'
                     deaths = 0
                     deactivate_powerups()
                 elif quit_text_rect.collidepoint(e.pos):
                      running = False


        #Drawing Game Over Screen
        screen.fill(SKY_BLUE)
        screen.blit(fade_surface, (0, 0)) # Apply fade overlay

        # Prepare text surfaces
        end_text_surf = large_font.render(end_message, True, WHITE) # "Game Over! You lose HAHA
        score_text_surf = font.render(f"Final Score: {int(score)}", True, WHITE)
        coin_text_surf = font.render(f"Coins Earned: {int(score * 0.5)}", True, WHITE)
        restart_text_surf = font.render("Restart (R)", True, WHITE)
        menu_text_surf = font.render("Menu (M)", True, WHITE)
        quit_text_surf = font.render("Quit (Q)", True, WHITE)


        # Calculate text rects
        end_text_rect = end_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
        score_text_rect = score_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        coin_text_rect = coin_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        restart_text_rect = restart_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        menu_text_rect = menu_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 90))
        quit_text_rect = quit_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 140))

        # Blit text
        screen.blit(end_text_surf, end_text_rect)
        screen.blit(score_text_surf, score_text_rect)
        screen.blit(coin_text_surf, coin_text_rect)
        screen.blit(restart_text_surf, restart_text_rect)
        screen.blit(menu_text_surf, menu_text_rect)
        screen.blit(quit_text_surf, quit_text_rect)


    elif game_state == 'win':
        #Win Logic & Drawing
        # Fade in effect
        if fade_alpha < 180:
            fade_alpha = min(fade_alpha + 15, 180)
            fade_surface.set_alpha(fade_alpha)

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == K_r: # Play Again (Restart)
                    click_sound.play()
                    reset_game()
                    game_state = 'playing'
                    # Start music again
                    if not pygame.mixer.music.get_busy():
                        pygame.mixer.music.play(-1)
                elif e.key == K_m: # Menu
                    click_sound.play()
                    game_state = 'menu'
                    deaths = 0
                    deactivate_powerups()
                elif e.key == K_q: # Quit
                    running = False
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                 if play_again_text_rect.collidepoint(e.pos):
                     click_sound.play()
                     reset_game()
                     game_state = 'playing'
                     if not pygame.mixer.music.get_busy():
                          try: pygame.mixer.music.play(-1)
                          except pygame.error as err: print(f"Error starting music on restart: {err}")
                 elif menu_text_rect.collidepoint(e.pos):
                     click_sound.play()
                     game_state = 'menu'
                     deaths = 0
                     deactivate_powerups()
                 elif quit_text_rect.collidepoint(e.pos):
                      running = False

        #Drawing Win Screen
        screen.fill(SKY_BLUE)
        screen.blit(fade_surface, (0, 0))

        # Prepare text surfaces
        win_text_surf = large_font.render("YOU WIN!", True, GOLD)
        score_text_surf = font.render(f"Final Score: {int(score)}", True, WHITE)
        coin_text_surf = font.render(f"Coins Earned: {int(score * 0.5)}", True, WHITE)
        play_again_text_surf = font.render("Play Again (R)", True, WHITE)
        menu_text_surf = font.render("Menu (M)", True, WHITE)
        quit_text_surf = font.render("Quit (Q)", True, WHITE)

        # Calculate text rects
        win_text_rect = win_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
        score_text_rect = score_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        coin_text_rect = coin_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        play_again_text_rect = play_again_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        menu_text_rect = menu_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 90))
        quit_text_rect = quit_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 140))

        # Blit text
        screen.blit(win_text_surf, win_text_rect)
        screen.blit(score_text_surf, score_text_rect)
        screen.blit(coin_text_surf, coin_text_rect)
        screen.blit(play_again_text_surf, play_again_text_rect)
        screen.blit(menu_text_surf, menu_text_rect)
        screen.blit(quit_text_surf, quit_text_rect)


    # Display Update
    # The playing state flips its own display within its loop to avoid extra flips
    if game_state != 'playing' or game_ended_this_frame:
         pygame.display.flip()
         clock.tick(60)

pygame.quit() #We are done thank God