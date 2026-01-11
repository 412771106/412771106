import pygame
import random
import math

# ---------------- 初始化 ----------------
pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Pinball Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# ---------------- 顏色 ----------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
RED = (255, 80, 80)
GREEN = (0, 200, 100)

# ---------------- 球設定 ----------------
ball_radius = 10
ball_x = WIDTH // 2
ball_y = HEIGHT - 120
ball_vx = 0
ball_vy = 0
gravity = 0.35

# ---------------- 發射設定 ----------------
launch_power = 12
launched = False

# ---------------- 分數 ----------------
score = 0

# ---------------- 特殊彈跳區 ----------------
special_zone = pygame.Rect(200, 250, 200, 30)

# ---------------- 主迴圈 ----------------
running = True
while running:
    clock.tick(60)
    screen.fill(BLACK)

    # -------- 事件處理 --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not launched:
                angle = random.uniform(-math.pi / 4, math.pi / 4)
                ball_vx = launch_power * math.sin(angle)
                ball_vy = -launch_power
                launched = True

            if event.key == pygame.K_r:
                ball_x = WIDTH // 2
                ball_y = HEIGHT - 120
                ball_vx = 0
                ball_vy = 0
                score = 0
                gravity = 0.35
                launched = False

    # -------- 物理運算 --------
    if launched:
        ball_vy += gravity
        ball_x += ball_vx
        ball_y += ball_vy

        # 左右牆壁反彈
        if ball_x <= ball_radius or ball_x >= WIDTH - ball_radius:
            ball_vx *= -1

        # 上牆反彈
        if ball_y <= ball_radius:
            ball_vy *= -1
            score += 5

        # 特殊彈跳區（特色玩法）
        if special_zone.collidepoint(ball_x, ball_y):
            ball_vy *= -1.2
            score += 20
            gravity += 0.02  # 動態重力（特色玩法）

        # 掉落判定
        if ball_y > HEIGHT:
            launched = False

    # -------- 繪製物件 --------
    pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius)
    pygame.draw.rect(screen, GREEN, special_zone)

    # 發射槽
    pygame.draw.rect(screen, BLUE, (WIDTH//2 - 40, HEIGHT - 100, 80, 10))

    # -------- 顯示文字 --------
    score_text = font.render(f"Score: {score}", True, WHITE)
    gravity_text = font.render(f"Gravity: {gravity:.2f}", True, WHITE)
    info_text = font.render("SPACE: Launch  R: Reset", True, WHITE)

    screen.blit(score_text, (20, 20))
    screen.blit(gravity_text, (20, 60))
    screen.blit(info_text, (20, HEIGHT - 40))

    pygame.display.flip()

pygame.quit()



