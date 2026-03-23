import pygame
import random

# --- CẤU HÌNH ---
pygame.init()
WIDTH, HEIGHT = 850, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ô Ăn Quan AI - Click Logic")
clock = pygame.time.Clock()

# Màu sắc
BG_COLOR = (248, 245, 237)
BOARD_BORDER = (160, 145, 130)
SEED_COLOR = (100, 85, 70)
HIGHLIGHT = (180, 160, 255) # Màu tím khi chọn ô

# Dữ liệu bàn cờ
board = [10, 5, 5, 5, 5, 5, 10, 5, 5, 5, 5, 5]
selected_index = -1  # Chỉ số ô đang được người chơi chọn

def get_cell_rects():
    """Hàm này trả về danh sách các Rect tương ứng với 12 chỉ số của board"""
    board_w, board_h = 700, 200
    start_x = (WIDTH - board_w) // 2
    start_y = (HEIGHT - board_h) // 2
    cell_size = 100

    rects = [None] * 12
    # Index 0: Quan trái
    rects[0] = pygame.Rect(start_x, start_y, 100, 200)
    # Index 6: Quan phải
    rects[6] = pygame.Rect(start_x + 600, start_y, 100, 200)

    for i in range(5):
        # Index 1-5: Hàng dưới
        rects[i+1] = pygame.Rect(start_x + 100 + (i * cell_size), start_y + 100, cell_size, cell_size)
        # Index 11-7: Hàng trên
        rects[11-i] = pygame.Rect(start_x + 100 + (i * cell_size), start_y, cell_size, cell_size)
    
    return rects

def draw_seeds(surface, rect, count, is_quan=False, is_selected=False):
    # Vẽ highlight nếu ô này đang được chọn
    if is_selected:
        pygame.draw.rect(surface, HIGHLIGHT, rect.inflate(-4, -4))

    # Vẽ số lượng
    font = pygame.font.SysFont("Verdana", 14, bold=True)
    txt = font.render(str(count), True, (80, 70, 60))
    surface.blit(txt, (rect.x + 8, rect.y + 8))

    # Vẽ Quân Quan hoặc Dân
    if is_quan and count > 0:
        center = rect.center
        pygame.draw.ellipse(surface, SEED_COLOR, (center[0]-20, center[1]-35, 40, 70))
    else:
        random.seed(rect.x * 10 + rect.y)
        for _ in range(count):
            rx = random.randint(rect.x + 20, rect.x + rect.width - 20)
            ry = random.randint(rect.y + 20, rect.y + rect.height - 20)
            pygame.draw.circle(surface, SEED_COLOR, (rx, ry), 4)

def draw_game(cell_rects):
    screen.fill(BG_COLOR)
    board_w, board_h = 700, 200
    start_x = (WIDTH - board_w) // 2
    start_y = (HEIGHT - board_h) // 2
    
    # Vẽ khung chính
    pygame.draw.rect(screen, BOARD_BORDER, (start_x, start_y, board_w, board_h), 2, border_radius=25)
    
    # Vẽ từng ô dựa trên danh sách Rects
    for i in range(12):
        is_q = (i == 0 or i == 6)
        is_sel = (i == selected_index)
        draw_seeds(screen, cell_rects[i], board[i], is_quan=is_q, is_selected=is_sel)
        
        # Vẽ viền các ô dân
        if not is_q:
            pygame.draw.rect(screen, BOARD_BORDER, cell_rects[i], 1)

    # Vạch ngăn cách Quan
    pygame.draw.line(screen, BOARD_BORDER, (start_x + 100, start_y), (start_x + 100, start_y + 200), 2)
    pygame.draw.line(screen, BOARD_BORDER, (start_x + 600, start_y), (start_x + 600, start_y + 200), 2)

# --- VÒNG LẶP CHÍNH ---
cell_rects = get_cell_rects()
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Kiểm tra xem click vào ô nào
            for i in range(1, 6): # Chỉ cho phép click vào ô dân hàng dưới (Player 1)
                if cell_rects[i].collidepoint(mouse_pos):
                    if board[i] > 0: # Chỉ chọn nếu ô có quân
                        selected_index = i
                        print(f"Bạn đã chọn ô số: {i}")

    draw_game(cell_rects)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()