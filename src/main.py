import pygame
import sys
import random
import time
import tkinter as tk
from tkinter import simpledialog

# Constants
TILE_SIZE = 23
GRID_WIDTH = 18
GRID_HEIGHT = 18
MINES = 20
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT + 60  # Extra for UI bar and menu

# Load images
def load_images():
    images = {}
    for i in range(9):
        images[str(i)] = pygame.image.load(f"assets/{i}.png")
    images["mine"] = pygame.image.load("assets/Mine.png")
    images["flag"] = pygame.image.load("assets/Flag.png")
    images["hidden"] = pygame.image.load("assets/Hidden.png")
    images["face_smile"] = pygame.image.load("assets/DefaultSmiley.png")
    images["face_oh"] = pygame.image.load("assets/OhFaceSmiley.png")
    images["face_dead"] = pygame.image.load("assets/LoseFaceSmiley.png")
    images["face_win"] = pygame.image.load("assets/WinFaceSmiley.png")
    return images

# Cell class
class Cell:
    def __init__(self):
        self.is_mine = False
        self.adjacent = 0
        self.revealed = False
        self.flagged = False

# Game logic
class Minesweeper:
    def __init__(self, width, height, mines):
        self.width = width
        self.height = height
        self.total_mines = mines
        self.reset()

    def reset(self):
        self.grid = [[Cell() for _ in range(self.width)] for _ in range(self.height)]
        self.mines = self.total_mines
        self.first_click = True
        self.game_over = False
        self.win = False
        self.start_time = None
        self.elapsed_time = 0
        self.place_mines()
        self.revealed_count = 0

    def place_mines(self):
        placed = 0
        while placed < self.total_mines:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if not self.grid[y][x].is_mine:
                self.grid[y][x].is_mine = True
                placed += 1

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].is_mine:
                    continue
                count = sum(
                    self.grid[ny][nx].is_mine
                    for dy in [-1, 0, 1]
                    for dx in [-1, 0, 1]
                    if 0 <= (ny := y + dy) < self.height and 0 <= (nx := x + dx) < self.width
                )
                self.grid[y][x].adjacent = count

    def reveal(self, x, y):
        if self.game_over or self.win:
            return

        cell = self.grid[y][x]
        if cell.flagged or cell.revealed:
            return

        cell.revealed = True
        self.revealed_count += 1
        if cell.is_mine:
            self.game_over = True
            self.reveal_all_mines()
            return

        if cell.adjacent == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < self.height and 0 <= nx < self.width:
                        if not self.grid[ny][nx].revealed:
                            self.reveal(nx, ny)

    def reveal_all_mines(self):
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell.is_mine and not cell.flagged:
                    cell.revealed = True

    def check_win(self):
        total_cells = self.width * self.height
        return self.revealed_count == total_cells - self.total_mines

# Show difficulty menu
def show_difficulty_menu():
    root = tk.Tk()
    root.withdraw()  # Hide main tkinter window

    try:
        w = simpledialog.askinteger("Custom Width", "Enter board width:", minvalue=5, maxvalue=50)
        h = simpledialog.askinteger("Custom Height", "Enter board height:", minvalue=5, maxvalue=50)
        m = simpledialog.askinteger("Custom Mines", "Enter number of mines:", minvalue=1, maxvalue=w*h-1)
    except:
        return GRID_WIDTH, GRID_HEIGHT, MINES  # fallback if cancelled or error

    if w and h and m:
        return w, h, m
    return GRID_WIDTH, GRID_HEIGHT, MINES

# Draw UI
def draw_ui(screen, images, game, font, face_rect, option_button_rect, menu_rects, menu_items, show_menu, hovered_index):
    pygame.draw.rect(screen, (192, 192, 192), (0, 0, SCREEN_WIDTH, 60))
    pygame.draw.rect(screen, (128, 128, 128), (0, 0, SCREEN_WIDTH, 60), 2)

    # Mine counter
    mines_text = font.render(f"{game.mines:03}", True, (255, 0, 0))
    screen.blit(mines_text, (5, 30))

    # Face
    if game.game_over:
        face_img = images["face_dead"]
    elif game.win:
        face_img = images["face_win"]
    else:
        face_img = images["face_smile"]
    screen.blit(face_img, face_rect.topleft)

    # Timer
    seconds = int(game.elapsed_time)
    timer_text = font.render(f"{seconds:03}", True, (255, 0, 0))
    screen.blit(timer_text, (SCREEN_WIDTH - 45, 30))

    # Options button
    pygame.draw.rect(screen, (200, 200, 200), option_button_rect)
    pygame.draw.rect(screen, (0, 0, 0), option_button_rect, 1)
    screen.blit(font.render("Options", True, (0, 0, 0)), (option_button_rect.x + 5, option_button_rect.y + 1))

    # Dropdown menu
    if show_menu:
        for i, rect in enumerate(menu_rects):
            color = (180, 180, 180) if i == hovered_index else (255, 255, 255)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)
            screen.blit(font.render(menu_items[i], True, (0, 0, 0)), (rect.x + 5, rect.y))

# Main loop
def main():
    pygame.init()
    width, height, mines = GRID_WIDTH, GRID_HEIGHT, MINES
    global SCREEN_WIDTH, SCREEN_HEIGHT
    SCREEN_WIDTH = TILE_SIZE * width
    SCREEN_HEIGHT = TILE_SIZE * height + 60

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Minesweeper XP")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Courier", 20, bold=True)
    images = load_images()
    game = Minesweeper(width, height, mines)
    face_rect = pygame.Rect((SCREEN_WIDTH // 2 - 13, 30, 26, 26))

    # Menu UI
    show_options_menu = False
    option_button_rect = pygame.Rect(5, 5, 95, 25)
    menu_items = ["Easy", "Medium", "Hard", "Extreme", "Custom"]
    hovered_index = -1

    def create_menu_rects():
        return [pygame.Rect(5, 25 + i * 20, 120, 20) for i in range(len(menu_items))]

    menu_rects = create_menu_rects()

    while True:
        screen.fill((255, 255, 255))
        hovered_index = -1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEMOTION:
                mx, my = pygame.mouse.get_pos()
                if show_options_menu:
                    for i, rect in enumerate(menu_rects):
                        if rect.collidepoint(mx, my):
                            hovered_index = i

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                if option_button_rect.collidepoint(mx, my):
                    show_options_menu = not show_options_menu
                elif show_options_menu:
                    clicked_any = False
                    for i, rect in enumerate(menu_rects):
                        if rect.collidepoint(mx, my):
                            clicked_any = True
                            difficulties = {
                                "Easy": (9, 9, 10),
                                "Medium": (16, 16, 40),
                                "Hard": (30, 16, 99),
                                "Extreme": (30, 24, 150)
                            }
                            if menu_items[i] == "Custom":
                                width, height, mines = show_difficulty_menu()
                            else:
                                width, height, mines = difficulties[menu_items[i]]

                            SCREEN_WIDTH = TILE_SIZE * width
                            SCREEN_HEIGHT = TILE_SIZE * height + 60
                            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                            game = Minesweeper(width, height, mines)
                            face_rect = pygame.Rect((SCREEN_WIDTH // 2 - 13, 30, 26, 26))
                            menu_rects = create_menu_rects()
                            show_options_menu = False
                            break
                    if not clicked_any:
                        show_options_menu = False

                elif face_rect.collidepoint(mx, my):
                    game.reset()
                elif my >= 60:
                    x, y = mx // TILE_SIZE, (my - 60) // TILE_SIZE
                    if 0 <= x < game.width and 0 <= y < game.height:
                        cell = game.grid[y][x]
                        if event.button == 1:
                            if game.first_click:
                                game.start_time = time.time()
                                game.first_click = False
                            game.reveal(x, y)
                            if game.check_win():
                                game.win = True
                        elif event.button == 3:
                            if not cell.revealed and not game.game_over:
                                cell.flagged = not cell.flagged
                                game.mines += -1 if cell.flagged else 1
                    show_options_menu = False  # Close menu if clicked on grid

        if not game.first_click and not game.game_over and not game.win:
            game.elapsed_time = time.time() - game.start_time

        for y in range(game.height):
            for x in range(game.width):
                cell = game.grid[y][x]
                px, py = x * TILE_SIZE, y * TILE_SIZE + 60
                if cell.revealed:
                    if cell.is_mine:
                        screen.blit(images["mine"], (px, py))
                    else:
                        screen.blit(images[str(cell.adjacent)], (px, py))
                elif cell.flagged:
                    screen.blit(images["flag"], (px, py))
                else:
                    screen.blit(images["hidden"], (px, py))

        draw_ui(screen, images, game, font, face_rect, option_button_rect, menu_rects, menu_items, show_options_menu, hovered_index)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
