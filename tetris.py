import pygame
import random
import sys
import time
import os
import copy

# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BLOCK_SIZE = 30
GRID_WIDTH = 20
GRID_HEIGHT = 20
GRID_X_OFFSET = 100
GRID_Y_OFFSET = 100

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (50, 50, 50)
COLORS = [
    (0, 255, 255),  # Cyan
    (255, 255, 0),  # Yellow
    (128, 0, 128),  # Purple
    (0, 255, 0),    # Green
    (255, 0, 0),    # Red
    (0, 0, 255),    # Blue
    (255, 165, 0)   # Orange
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]]
]

# Fonts
font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 16)
large_font = pygame.font.SysFont("Arial", 48)

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3D Tetris")
clock = pygame.time.Clock()

def draw_3d_block(surface, x, y, size, color):
    base = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, color, base)

    light = tuple(min(255, c + 60) for c in color)
    dark = tuple(max(0, c - 60) for c in color)

    pygame.draw.polygon(surface, light, [
        (x, y), (x + size, y), (x + size - 4, y + 4), (x + 4, y + 4)
    ])
    pygame.draw.polygon(surface, light, [
        (x, y), (x + 4, y + 4), (x + 4, y + size - 4), (x, y + size)
    ])
    pygame.draw.polygon(surface, dark, [
        (x, y + size), (x + size, y + size), (x + size - 4, y + size - 4), (x + 4, y + size - 4)
    ])
    pygame.draw.polygon(surface, dark, [
        (x + size, y), (x + size, y + size), (x + size - 4, y + size - 4), (x + size - 4, y + 4)
    ])

def draw_background_blocks():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if x == 0 or x == GRID_WIDTH - 1 or y == GRID_HEIGHT - 1:
                draw_3d_block(screen, GRID_X_OFFSET + x * BLOCK_SIZE, GRID_Y_OFFSET + y * BLOCK_SIZE, BLOCK_SIZE, GREY)

class Tetromino:
    def __init__(self):
        self.type = random.randint(0, len(SHAPES) - 1)
        self.shape = copy.deepcopy(SHAPES[self.type])
        self.color = COLORS[self.type]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.piece = Tetromino()
        self.next_piece = Tetromino()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.lives = 3
        self.game_over = False
        self.drop_timer = time.time()

    def reset_board(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.piece = Tetromino()
        self.next_piece = Tetromino()
        self.drop_timer = time.time()

    def is_valid(self, shape, x, y):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if x + j < 0 or x + j >= GRID_WIDTH or y + i >= GRID_HEIGHT:
                        return False
                    if y + i >= 0 and self.grid[y + i][x + j]:
                        return False
        return True

    def place_piece(self):
        for i, row in enumerate(self.piece.shape):
            for j, cell in enumerate(row):
                if cell and self.piece.y + i >= 0:
                    self.grid[self.piece.y + i][self.piece.x + j] = self.piece.color
        self.clear_lines()
        self.piece = self.next_piece
        self.next_piece = Tetromino()
        if not self.is_valid(self.piece.shape, self.piece.x, self.piece.y):
            self.lives -= 1
            if self.lives > 0:
                self.reset_board()
            else:
                self.game_over = True

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        lines_cleared = GRID_HEIGHT - len(new_grid)
        self.lines_cleared += lines_cleared
        self.score += lines_cleared * 100
        self.level = self.lines_cleared // 5 + 1
        while len(new_grid) < GRID_HEIGHT:
            new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        self.grid = new_grid

    def move(self, dx, dy):
        if self.is_valid(self.piece.shape, self.piece.x + dx, self.piece.y + dy):
            self.piece.x += dx
            self.piece.y += dy
            return True
        return False

    def rotate(self):
        old = self.piece.shape
        self.piece.rotate()
        if not self.is_valid(self.piece.shape, self.piece.x, self.piece.y):
            self.piece.shape = old

    def drop(self):
        while self.move(0, 1):
            pass
        self.place_piece()

    def update(self):
        fall_interval = max(0.1, 0.5 - (self.level - 1) * 0.05)
        if time.time() - self.drop_timer > fall_interval:
            if not self.move(0, 1):
                self.place_piece()
            self.drop_timer = time.time()

    def draw(self):
        screen.fill(BLACK)
        draw_background_blocks()
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    draw_3d_block(screen, GRID_X_OFFSET + x * BLOCK_SIZE, GRID_Y_OFFSET + y * BLOCK_SIZE, BLOCK_SIZE, self.grid[y][x])

        for i, row in enumerate(self.piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    draw_3d_block(screen, GRID_X_OFFSET + (self.piece.x + j) * BLOCK_SIZE, GRID_Y_OFFSET + (self.piece.y + i) * BLOCK_SIZE, BLOCK_SIZE, self.piece.color)

        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - 250, 100))
        lives_text = font.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(lives_text, (SCREEN_WIDTH - 250, 140))
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - 250, 180))

        if self.game_over:
            over_text = large_font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()

def main():
    game = Tetris()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not game.game_over:
                    if event.key == pygame.K_LEFT:
                        game.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        game.move(0, 1)
                    elif event.key == pygame.K_UP:
                        game.rotate()
                    elif event.key == pygame.K_SPACE:
                        game.drop()

        if not game.game_over:
            game.update()
        game.draw()
        clock.tick(60)

if __name__ == "__main__":
    main()