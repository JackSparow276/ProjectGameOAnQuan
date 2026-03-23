import pygame
import random
import copy

# --- CẤU HÌNH HỆ THỐNG ---
pygame.init()
WIDTH, HEIGHT = 950, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ô Ăn Quan AI - Nhom 14")
clock = pygame.time.Clock()

# --- MÀU SẮC & FONT ---
BG_COLOR = (248, 245, 237)
BOARD_BORDER = (160, 145, 130)
SEED_COLOR = (100, 85, 70)
HIGHLIGHT = (210, 200, 255)
TEXT_COLOR = (80, 70, 60)
BTN_COLOR = (120, 110, 100)
BTN_HOVER = (180, 170, 160)
HAND_COLOR = (255, 100, 100)

FONT_MAIN = pygame.font.SysFont("Arial", 45, bold=True)
FONT_SUB = pygame.font.SysFont("Arial", 25, bold=True)

# --- TRẠNG THÁI GAME ---
# 0: Menu, 1: Chọn độ khó, 2: Chơi PvP, 3: Chơi PvE
game_state = 0
ai_difficulty = 3 
is_pvp = False

# --- DỮ LIỆU BÀN CỜ ---
board = [10, 5, 5, 5, 5, 5, 10, 5, 5, 5, 5, 5]
score = [0, 0] 
selected_index = -1
current_player = 0 
is_animating = False
current_hand_pos = -1
game_over = False

# --- HÀM HỖ TRỢ GIAO DIỆN ---
def draw_button(text, x, y, w, h, inactive_color, active_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    
    is_hover = x + w > mouse[0] > x and y + h > mouse[1] > y
    color = active_color if is_hover else inactive_color
    pygame.draw.rect(screen, color, rect, border_radius=12)
    
    txt_surf = FONT_SUB.render(text, True, (255, 255, 255))
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)
    
    return is_hover and click[0] == 1

def reset_game():
    global board, score, current_player, game_over, is_animating, selected_index
    board = [10, 5, 5, 5, 5, 5, 10, 5, 5, 5, 5, 5]
    score = [0, 0]
    current_player = 0
    game_over = False
    is_animating = False
    selected_index = -1

# --- LOGIC AI (MINIMAX & SIMULATION) ---
def simulate_move(curr_board, curr_scores, start_idx, direction, player_idx):
    temp_b = list(curr_board); temp_s = list(curr_scores)
    actual_dir = direction if player_idx == 0 else -direction
    hand = temp_b[start_idx]; temp_b[start_idx] = 0; pos = start_idx
    while hand > 0:
        while hand > 0:
            pos = (pos + actual_dir) % 12; temp_b[pos] += 1; hand -= 1
        next_p = (pos + actual_dir) % 12
        if temp_b[next_p] > 0 and next_p != 0 and next_p != 6:
            hand = temp_b[next_p]; temp_b[next_p] = 0; pos = next_p
        elif temp_b[next_p] == 0:
            while temp_b[next_p] == 0:
                target = (next_p + actual_dir) % 12
                if temp_b[target] > 0:
                    temp_s[player_idx] += temp_b[target]; temp_b[target] = 0
                    next_p = (target + actual_dir) % 12
                    if temp_b[next_p] != 0: break
                else: break
            break
        else: break
    return temp_b, temp_s

def minimax(b, s, depth, alpha, beta, is_max):
    if depth == 0 or (b[0] == 0 and b[6] == 0):
        return s[1] - s[0], None, None
    best_move = (None, None)
    if is_max:
        max_eval = float('-inf')
        for i in range(7, 12):
            if b[i] > 0:
                for d in [1, -1]:
                    nb, ns = simulate_move(b, s, i, d, 1)
                    ev, _, _ = minimax(nb, ns, depth-1, alpha, beta, False)
                    if ev > max_eval: max_eval = ev; best_move = (i, d)
                    alpha = max(alpha, ev)
                    if beta <= alpha: break
        return max_eval, best_move[0], best_move[1]
    else:
        min_eval = float('inf')
        for i in range(1, 6):
            if b[i] > 0:
                for d in [1, -1]:
                    nb, ns = simulate_move(b, s, i, d, 0)
                    ev, _, _ = minimax(nb, ns, depth-1, alpha, beta, True)
                    if ev < min_eval: min_eval = ev; best_move = (i, d)
                    beta = min(beta, ev)
                    if beta <= alpha: break
        return min_eval, best_move[0], best_move[1]

# --- HÀM VẼ GIAO DIỆN GAME ---
def get_cell_rects():
    board_w, board_h = 700, 200
    start_x = (WIDTH - board_w) // 2; start_y = (HEIGHT - board_h) // 2
    cell_size = 100; rects = [None] * 12
    rects[0] = pygame.Rect(start_x, start_y, 100, 200); rects[6] = pygame.Rect(start_x + 600, start_y, 100, 200)
    for i in range(5):
        rects[i+1] = pygame.Rect(start_x + 100 + (i * cell_size), start_y + 100, cell_size, cell_size)
        rects[11-i] = pygame.Rect(start_x + 100 + (i * cell_size), start_y, cell_size, cell_size)
    return rects

def draw_interface_game():
    screen.fill(BG_COLOR)
    rects = get_cell_rects()
    pygame.draw.rect(screen, BOARD_BORDER, (rects[0].x, rects[0].y, 700, 200), 2, border_radius=25)
    for i in range(12):
        if i == selected_index: pygame.draw.rect(screen, HIGHLIGHT, rects[i].inflate(-4, -4))
        if i == current_hand_pos: pygame.draw.rect(screen, HAND_COLOR, rects[i].inflate(-2, -2), 4, border_radius=10)
        font = pygame.font.SysFont("Verdana", 14, bold=True)
        txt = font.render(str(board[i]), True, TEXT_COLOR)
        screen.blit(txt, (rects[i].x + 8, rects[i].y + 8))
        if (i == 0 or i == 6) and board[i] >= 10:
            pygame.draw.ellipse(screen, SEED_COLOR, (rects[i].centerx-20, rects[i].centery-40, 40, 80))
        elif board[i] > 0:
            random.seed(i)
            for _ in range(min(board[i], 15)):
                rx, ry = random.randint(rects[i].x+25, rects[i].right-25), random.randint(rects[i].y+25, rects[i].bottom-25)
                pygame.draw.circle(screen, SEED_COLOR, (rx, ry), 4)
        if i != 0 and i != 6: pygame.draw.rect(screen, BOARD_BORDER, rects[i], 1)
    
    font_s = pygame.font.SysFont("Arial", 22, bold=True)
    p2_label = "MÁY (P2)" if not is_pvp else "NGƯỜI 2 (P2)"
    screen.blit(font_s.render(f"NGƯỜI 1 (P1): {score[0]}", True, (50, 50, 150)), (50, HEIGHT - 60))
    screen.blit(font_s.render(f"{p2_label}: {score[1]}", True, (150, 50, 50)), (WIDTH - 300, 40))
    
    if game_over:
        msg = "HÒA!" if score[0] == score[1] else ("BẠN THẮNG!" if score[0] > score[1] else f"{p2_label} THẮNG!")
        txt = font_s.render(f"KẾT THÚC: {msg}", True, (200, 0, 0))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT - 100))

    if selected_index != -1 and not is_animating and not game_over:
        r = rects[selected_index]
        btn_l, btn_r = pygame.Rect(r.centerx - 45, r.centery - 15, 40, 30), pygame.Rect(r.centerx + 5, r.centery - 15, 40, 30)
        pygame.draw.rect(screen, BTN_COLOR, btn_l, border_radius=5); pygame.draw.rect(screen, BTN_COLOR, btn_r, border_radius=5)
        font_btn = pygame.font.SysFont("Arial", 20, bold=True)
        screen.blit(font_btn.render("<", True, (255,255,255)), (btn_l.centerx-7, btn_l.centery-12))
        screen.blit(font_btn.render(">", True, (255,255,255)), (btn_r.centerx-7, btn_r.centery-12))
        return btn_l, btn_r
    return None, None

# --- QUY TẮC TRÒ CHƠI ---
def handle_empty_rows():
    global score, board
    if sum(board[1:6]) == 0 and (board[0] > 0 or board[6] > 0):
        score[0] -= 5; [board.__setitem__(i, 1) for i in range(1, 6)]
    if sum(board[7:12]) == 0 and (board[0] > 0 or board[6] > 0):
        score[1] -= 5; [board.__setitem__(i, 1) for i in range(7, 12)]

def check_game_over():
    global game_over, score
    if board[0] == 0 and board[6] == 0:
        for i in range(1, 6): score[0] += board[i]; board[i] = 0
        for i in range(7, 12): score[1] += board[i]; board[i] = 0
        game_over = True; return True
    return False

def move_logic(start_idx, direction):
    global current_player, selected_index, is_animating, current_hand_pos
    is_animating = True
    actual_dir = direction if current_player == 0 else -direction
    hand = board[start_idx]; board[start_idx] = 0; pos = start_idx
    while hand > 0:
        while hand > 0:
            pos = (pos + actual_dir) % 12; current_hand_pos = pos; board[pos] += 1; hand -= 1
            draw_interface_game(); pygame.display.flip(); pygame.time.wait(200)
        pygame.time.wait(400)
        next_p = (pos + actual_dir) % 12
        if board[next_p] > 0 and next_p != 0 and next_p != 6:
            hand = board[next_p]; board[next_p] = 0; pos = next_p; pygame.time.wait(300)
        elif board[next_p] == 0:
            while board[next_p] == 0:
                target = (next_p + actual_dir) % 12
                if board[target] > 0:
                    score[current_player] += board[target]; board[target] = 0; current_hand_pos = target
                    draw_interface_game(); pygame.display.flip(); pygame.time.wait(600)
                    next_p = (target + actual_dir) % 12
                    if board[next_p] != 0: break
                else: break
            break
        else: break
    current_hand_pos = -1; selected_index = -1; is_animating = False
    if not check_game_over():
        current_player = 1 - current_player
        handle_empty_rows()

# --- VÒNG LẶP CHÍNH ---
running = True
rects = get_cell_rects()

while running:
    # 1. GIAO DIỆN MENU CHÍNH
    if game_state == 0:
        screen.fill(BG_COLOR)
        title = FONT_MAIN.render("Ô ĂN QUAN AI", True, TEXT_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        if draw_button("NGƯỜI VS NGƯỜI", WIDTH//2-150, 300, 300, 60, BTN_COLOR, BTN_HOVER):
            is_pvp = True; reset_game(); game_state = 2; pygame.time.wait(200)
        if draw_button("NGƯỜI VS MÁY", WIDTH//2-150, 400, 300, 60, BTN_COLOR, BTN_HOVER):
            is_pvp = False; game_state = 1; pygame.time.wait(200)

    # 2. GIAO DIỆN CHỌN ĐỘ KHÓ
    elif game_state == 1:
        screen.fill(BG_COLOR)
        title = FONT_MAIN.render("CHỌN MỨC ĐỘ", True, TEXT_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        if draw_button("DỄ (AI NON NỚT)", WIDTH//2-150, 280, 300, 50, (100, 180, 100), (120, 200, 120)):
            ai_difficulty = 1; reset_game(); game_state = 3; pygame.time.wait(200)
        if draw_button("KHÓ (AI CÂN TẤT)", WIDTH//2-150, 360, 300, 50, (200, 150, 50), (220, 170, 70)):
            ai_difficulty = 3; reset_game(); game_state = 3; pygame.time.wait(200)
        if draw_button("SIÊU KHÓ (MASTER)", WIDTH//2-150, 440, 300, 50, (180, 50, 50), (200, 70, 70)):
            ai_difficulty = 5; reset_game(); game_state = 3; pygame.time.wait(200)

    # 3. GIAO DIỆN CHƠI GAME
    elif game_state in [2, 3]:
        btn_l, btn_r = draw_interface_game()
        if draw_button("THOÁT", 20, 20, 100, 40, (150, 70, 70), (180, 90, 90)):
            game_state = 0; pygame.time.wait(200)
        
        # LOGIC AI (Chỉ chạy ở state 3 - PvE)
        if game_state == 3 and current_player == 1 and not is_animating and not game_over:
            pygame.display.flip(); pygame.time.wait(800)
            if ai_difficulty == 1: # Mức dễ có 50% đi ngẫu nhiên
                if random.random() < 0.5:
                    v_moves = [(i, d) for i in range(7, 12) for d in [1, -1] if board[i] > 0]
                    ai_idx, ai_dir = random.choice(v_moves)
                else:
                    _, ai_idx, ai_dir = minimax(board, score, 1, float('-inf'), float('inf'), True)
            else: # Khó và Siêu khó dùng Minimax chuẩn
                _, ai_idx, ai_dir = minimax(board, score, ai_difficulty, float('-inf'), float('inf'), True)
            if ai_idx is not None: move_logic(ai_idx, ai_dir)

    # XỬ LÝ SỰ KIỆN CHUỘT
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not is_animating and not game_over:
            pos = pygame.mouse.get_pos()
            if game_state in [2, 3]:
                if btn_l and btn_l.collidepoint(pos): move_logic(selected_index, -1)
                elif btn_r and btn_r.collidepoint(pos): move_logic(selected_index, 1)
                else:
                    # Player 1 luôn đi hàng dưới (1-5)
                    # Player 2 (nếu là người) đi hàng trên (7-11)
                    v_range = range(1, 6) if current_player == 0 else range(7, 12)
                    if game_state == 3 and current_player == 1: v_range = range(0) # Khóa click khi tới lượt AI
                    for i in v_range:
                        if rects[i].collidepoint(pos) and board[i] > 0: selected_index = i

    pygame.display.flip()
    clock.tick(60)
pygame.quit()