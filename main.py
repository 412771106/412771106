import pygame
import random
import sys

# -------------------- 1. 初始化 --------------------
pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python 彈珠台")

# 顏色定義
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (255, 50, 50)   # 彈珠
GREEN  = (50, 255, 50)   # 彈板
BLUE   = (50, 50, 255)   # 移動得分區
PURPLE = (160, 32, 240)  # 傳送門
YELLOW = (255, 255, 0)   # 加速板

clock = pygame.time.Clock()
FPS = 60

# 遊戲變數
score = 0
font = pygame.font.SysFont("Arial", 32)
large_font = pygame.font.SysFont("Arial", 64)

# -------------------- 慢速物理參數 --------------------
ball_radius = 15
ball_x, ball_y = WIDTH // 2, HEIGHT - 80
ball_speed_x, ball_speed_y = 0, 0
ball_launched = False

# 重力調低 (原 0.45 -> 0.25)，球會緩慢下墜
gravity = 0.25  

# 彈板參數
flipper_width = 120
flipper_height = 20
flipper_x = WIDTH // 2 - flipper_width // 2
flipper_y = HEIGHT - 60
flipper_speed = 10 # 配合球速，稍微調慢彈板

# 特殊要素位置與變數
score_zone = pygame.Rect(WIDTH//2-50, 150, 100, 30)
score_zone_dir = 1
portal_in = pygame.Rect(30, 350, 60, 60)
portal_out = pygame.Rect(WIDTH-90, 350, 60, 60)
portal_cooldown = 0 # 傳送門冷卻，防止卡死
booster = pygame.Rect(WIDTH//2-40, 450, 80, 20)

game_started = False

def reset_ball():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, ball_launched
    ball_x, ball_y = WIDTH // 2, HEIGHT - 80
    ball_speed_x, ball_speed_y = 0, 0
    ball_launched = False

# -------------------- 2. 主遊戲迴圈 --------------------
running = True
while running:
    screen.fill(BLACK)

    # 事件偵測
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_started:
                    game_started = True
                elif not ball_launched:
                    # 降低發射初速 (原 -18 -> -12)
                    ball_speed_x = random.choice([-4, 4])
                    ball_speed_y = -12 
                    ball_launched = True
            
            if event.key == pygame.K_r:
                score = 0
                reset_ball()

    if not game_started:
        # 開始畫面
        title = large_font.render("PINBALL", True, WHITE)
        hint = font.render("Press SPACE to Start", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2))
    
    else:
        # -------------------- 3. 邏輯更新 --------------------
        # 彈板操作
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and flipper_x > 0:
            flipper_x -= flipper_speed
        if keys[pygame.K_RIGHT] and flipper_x + flipper_width < WIDTH:
            flipper_x += flipper_speed

        if ball_launched:
            ball_speed_y += gravity
            ball_x += ball_speed_x
            ball_y += ball_speed_y

            # 建立球的碰撞矩形
            ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius*2, ball_radius*2)

            # A. 牆壁反彈 (保持 1.0 速度)
            if ball_x - ball_radius <= 0 or ball_x + ball_radius >= WIDTH:
                ball_speed_x *= -1
                ball_x = max(ball_radius, min(WIDTH - ball_radius, ball_x))
            
            if ball_y - ball_radius <= 0:
                ball_speed_y *= -1
                ball_y = ball_radius

            # B. 彈板反彈 (移除 1.1x 加速，改為恆定反彈)
            flipper_rect = pygame.Rect(flipper_x, flipper_y, flipper_width, flipper_height)
            if ball_rect.colliderect(flipper_rect) and ball_speed_y > 0:
                ball_speed_y *= -1.0 
                ball_y = flipper_y - ball_radius
                # 計算水平偏移，讓球可以控制方向
                offset = (ball_x - (flipper_x + flipper_width/2)) / (flipper_width/2)
                ball_speed_x = offset * 8

            # C. 特殊要素：移動得分區
            score_zone.x += 2 * score_zone_dir # 移動速度減半
            if score_zone.right >= WIDTH or score_zone.left <= 0:
                score_zone_dir *= -1
            
            if ball_rect.colliderect(score_zone):
                score += 10
                ball_speed_y *= -1.0 # 不額外加速
                ball_y += 30 if ball_speed_y > 0 else -30

            # D. 特殊要素：傳送門
            if portal_cooldown > 0:
                portal_cooldown -= 1
            if portal_cooldown == 0:
                if ball_rect.colliderect(portal_in):
                    ball_x, ball_y = portal_out.centerx, portal_out.centery
                    portal_cooldown = 40
                elif ball_rect.colliderect(portal_out):
                    ball_x, ball_y = portal_in.centerx, portal_in.centery
                    portal_cooldown = 40

            # E. 特殊要素：加速板 (緩慢版加速)
            if ball_rect.colliderect(booster):
                ball_speed_y = -15 
                ball_y = booster.top - ball_radius

            # F. 掉落底部重置
            if ball_y > HEIGHT:
                reset_ball()

        # -------------------- 4. 繪製畫面 --------------------
        # 繪製移動得分區
        pygame.draw.rect(screen, BLUE, score_zone)
        
        # 繪製傳送門 (冷卻時變暗)
        p_color = (80, 0, 100) if portal_cooldown > 0 else PURPLE
        pygame.draw.rect(screen, p_color, portal_in, border_radius=10)
        pygame.draw.rect(screen, p_color, portal_out, border_radius=10)
        
        # 繪製加速板
        pygame.draw.rect(screen, YELLOW, booster)
        
        # 繪製彈板與球
        pygame.draw.rect(screen, GREEN, (flipper_x, flipper_y, flipper_width, flipper_height), border_radius=5)
        pygame.draw.circle(screen, RED, (int(ball_x), int(ball_y)), ball_radius)
        
        # 顯示分數
        score_display = font.render(f"SCORE: {score}", True, WHITE)
        screen.blit(score_display, (20, 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()


