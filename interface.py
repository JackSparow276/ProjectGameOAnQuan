import pygame
import random

# --- CẤU HÌNH ---
pygame.init()
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ô Ăn Quan AI - Full Rules & Optimized UX")
clock = pygame.time.Clock()

# Màu sắc
BG_COLOR = (248, 245, 237)
BOARD_BORDER = (160, 145, 130)
SEED_COLOR = (100, 85, 70)
HIGHLIGHT = (210, 200, 255)
TEXT_COLOR = (80, 70, 60)
BTN_COLOR = (100, 200, 100)
HAND_COLOR = (255, 100, 100)

# --- DỮ LIỆU GAME ---
board = [10, 5, 5, 5, 5, 5, 10, 5, 5, 5, 5, 5]
score = [0, 0]
selected_index = -1
current_player = 0 
is_animating = False
current_hand_pos = -1 
game_over = False

def get_cell_rects():
    board_w, board_h = 700, 200
    start_x = (WIDTH - board_w) // 2
    start_y = (HEIGHT - board_h) // 2
    cell_size = 100
    rects = [None] * 12
    rects[0] = pygame.Rect(start_x, start_y, 100, 200)
    rects[6] = pygame.Rect(start_x + 600, start_y, 100, 200)
    for i in range(5):
        rects[i+1] = pygame.Rect(start_x + 100 + (i * cell_size), start_y + 100, cell_size, cell_size)
        rects[11-i] = pygame.Rect(start_x + 100 + (i * cell_size), start_y, cell_size, cell_size)
    return rects

def check_game_over():
    global game_over, score
    # Nếu cả 2 ô Quan đều hết quân
    if board[0] == 0 and board[6] == 0:
        # Thu hoạch quân dân còn lại trên bàn cho mỗi bên
        for i in range(1, 6):
            score[0] += board[i]
            board[i] = 0
        for i in range(7, 12):
            score[1] += board[i]
            board[i] = 0
        game_over = True
        return True
    return False

def replenish_board():
    global score
    # Kiểm tra Player 1 (1-5)
    if sum(board[1:6]) == 0 and not game_over:
        print("P1 hết dân! Tự động rải lại 5 quân.")
        score[0] -= 5
        for i in range(1, 6): board[i] = 1
        
    # Kiểm tra Player 2 (7-12)
    if sum(board[7:12]) == 0 and not game_over:
        print("P2 hết dân! Tự động rải lại 5 quân.")
        score[1] -= 5
        for i in range(7, 12): board[i] = 1

def draw_interface():
    screen.fill(BG_COLOR)
    rects = get_cell_rects()
    board_w, board_h = 700, 200
    start_x = (WIDTH - board_w) // 2
    start_y = (HEIGHT - board_h) // 2

    # Vẽ khung bàn cờ
    pygame.draw.rect(screen, BOARD_BORDER, (start_x, start_y, 700, 200), 2, border_radius=25)
    
    for i in range(12):
        if i == selected_index:
            pygame.draw.rect(screen, HIGHLIGHT, rects[i].inflate(-4, -4))
        
        if i == current_hand_pos:
            pygame.draw.rect(screen, HAND_COLOR, rects[i].inflate(-2, -2), 4, border_radius=10)

        # Vẽ quân
        font = pygame.font.SysFont("Verdana", 14, bold=True)
        txt = font.render(str(board[i]), True, TEXT_COLOR)
        screen.blit(txt, (rects[i].x + 8, rects[i].y + 8))
        
        if (i == 0 or i == 6) and board[i] >= 10:
            pygame.draw.ellipse(screen, SEED_COLOR, (rects[i].centerx-20, rects[i].centery-40, 40, 80))
        elif board[i] > 0:
            random.seed(i)
            for _ in range(min(board[i], 15)):
                rx = random.randint(rects[i].x+25, rects[i].right-25)
                ry = random.randint(rects[i].y+25, rects[i].bottom-25)
                pygame.draw.circle(screen, SEED_COLOR, (rx, ry), 4)

        if i != 0 and i != 6:
            pygame.draw.rect(screen, BOARD_BORDER, rects[i], 1)
    
    # Hiển thị điểm
    font_s = pygame.font.SysFont("Arial", 22, bold=True)
    screen.blit(font_s.render(f"P1: {score[0]}", True, TEXT_COLOR), (50, HEIGHT - 50))
    screen.blit(font_s.render(f"P2: {score[1]}", True, TEXT_COLOR), (WIDTH - 150, 50))

    if game_over:
        winner = "P1 THẮNG!" if score[0] > score[1] else "P2 THẮNG!"
        if score[0] == score[1]: winner = "HÒA!"
        res_txt = font_s.render(f"GAME OVER - {winner}", True, (200, 0, 0))
        screen.blit(res_txt, (WIDTH//2 - res_txt.get_width()//2, 50))

    # Nút mũi tên
    if selected_index != -1 and not is_animating and not game_over:
        r = rects[selected_index]
        btn_l = pygame.Rect(r.centerx - 45, r.centery - 15, 40, 30)
        btn_r = pygame.Rect(r.centerx + 5, r.centery - 15, 40, 30)
        pygame.draw.rect(screen, BTN_COLOR, btn_l, border_radius=5)
        pygame.draw.rect(screen, BTN_COLOR, btn_r, border_radius=5)
        font_btn = pygame.font.SysFont("Arial", 20, bold=True)
        screen.blit(font_btn.render("<", True, (255,255,255)), (btn_l.centerx-7, btn_l.centery-12))
        screen.blit(font_btn.render(">", True, (255,255,255)), (btn_r.centerx-7, btn_r.centery-12))
        return btn_l, btn_r
    return None, None

def move_logic(start_idx, direction):
    global current_player, selected_index, is_animating, current_hand_pos, board
    is_animating = True
    actual_dir = direction if current_player == 0 else -direction

    hand = board[start_idx]
    board[start_idx] = 0
    current_pos = start_idx
    
    while hand > 0:
        while hand > 0:
            current_pos = (current_pos + actual_dir) % 12
            current_hand_pos = current_pos 
            board[current_pos] += 1
            hand -= 1
            draw_interface(); pygame.display.flip(); pygame.time.wait(400)

        pygame.time.wait(600)
        next_pos = (current_pos + actual_dir) % 12
        current_hand_pos = next_pos 
        draw_interface(); pygame.display.flip()
        
        if board[next_pos] > 0 and next_pos != 0 and next_pos != 6:
            hand = board[next_pos]
            board[next_pos] = 0
            current_pos = next_pos
            pygame.time.wait(400)
        elif board[next_pos] == 0:
            # Logic ăn quân liên tiếp
            while board[next_pos] == 0:
                target_pos = (next_pos + actual_dir) % 12
                if board[target_pos] > 0:
                    score[current_player] += board[target_pos]
                    board[target_pos] = 0
                    current_hand_pos = target_pos
                    draw_interface(); pygame.display.flip(); pygame.time.wait(800)
                    # Sau khi ăn, kiểm tra ô tiếp theo có trống không để ăn tiếp
                    next_pos = (target_pos + actual_dir) % 12
                    if board[next_pos] != 0: break # Nếu ô tiếp theo có quân thì dừng
                else:
                    break
            break
        else:
            break

    current_hand_pos = -1
    selected_index = -1
    is_animating = False
    if not check_game_over():
        current_player = 1 - current_player
        replenish_board() # Kiểm tra và rải lại quân nếu hết dân

# --- MAIN LOOP ---
rects = get_cell_rects()
running = True
while running:
    btn_l, btn_r = draw_interface()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not is_animating and not game_over:
            pos = pygame.mouse.get_pos()
            if btn_l and btn_l.collidepoint(pos): move_logic(selected_index, -1)
            elif btn_r and btn_r.collidepoint(pos): move_logic(selected_index, 1)
            else:
                valid_range = range(1, 6) if current_player == 0 else range(7, 12)
                for i in valid_range:
                    if rects[i].collidepoint(pos) and board[i] > 0: selected_index = i
    pygame.display.flip()
    clock.tick(60)
pygame.quit()