import pygame
import sys
import random
import json
import os  # برای چک کردن وجود فایل

pygame.init()
WIDTH, HEIGHT = 960, 640
FPS = 8
CELL_SIZE = 20

BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 150, 255)
TURQUOISE = (0, 255, 255)
GRAY = (30, 30, 30)
DARK_BG = (5, 5, 5)

font = pygame.font.SysFont("consolas", 24)
large_font = pygame.font.SysFont("consolas", 40)
title_font = pygame.font.SysFont("consolas", 50, bold=True)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Farda Snake Game")
clock = pygame.time.Clock()

player1_name = "Player 1"
player2_name = "Player 2"
high_scores = []

import sys

if getattr(sys, 'frozen', False):
    # وقتی برنامه به exe تبدیل شده
    base_path = os.path.dirname(sys.executable)
else:
    # وقتی برنامه به صورت اسکریپت پایتون اجرا میشه
    base_path = os.path.dirname(os.path.abspath(__file__))

SCORE_FILE = os.path.join(base_path, "high_scores.json")


def load_high_scores():
    global high_scores
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and all(isinstance(i, dict) for i in data):
                    high_scores = data
                else:
                    high_scores = []
        except Exception as e:
            print("Error loading high scores:", e)
            high_scores = []
    else:
        high_scores = []
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(high_scores, f)



def save_high_scores():
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(high_scores, f)


class Snake:
    def __init__(self, color, keys, start_pos):
        self.color = color
        self.keys = keys
        self.body = [start_pos]
        self.direction = (1, 0)
        self.grow = 0
        self.score = 0

    def update(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        if not (0 <= new_head[0] < WIDTH // CELL_SIZE and 0 <= new_head[1] < HEIGHT // CELL_SIZE):
            self.body.clear()
            return
        self.body.insert(0, new_head)
        if self.grow > 0:
            self.grow -= 1
        else:
            self.body.pop()

    def draw(self):
        for segment in self.body:
            pygame.draw.rect(screen, self.color, (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def eat(self):
        self.grow += 1
        self.score += 1

    def check_collision(self, other):
        if self.body and other.body:
            if self.body[0] == other.body[0]:
                if len(self.body) > 1: self.body.pop()
                if len(other.body) > 1: other.body.pop()
            elif self.body[0] in other.body[1:]:
                index = other.body.index(self.body[0])
                del other.body[index:]

def spawn_food(snake1, snake2, foods):
    while True:
        pos = (random.randint(0, WIDTH // CELL_SIZE - 1), random.randint(0, HEIGHT // CELL_SIZE - 1))
        if pos not in snake1.body and pos not in snake2.body and pos not in foods:
            return pos

def game_loop():
    global screen, WIDTH, HEIGHT
    snake1 = Snake(RED, {pygame.K_UP: (0,-1), pygame.K_DOWN: (0,1), pygame.K_LEFT: (-1,0), pygame.K_RIGHT: (1,0)}, (5, 5))
    snake2 = Snake(BLUE, {pygame.K_w: (0,-1), pygame.K_s: (0,1), pygame.K_a: (-1,0), pygame.K_d: (1,0)}, (20, 20))
    foods = [spawn_food(snake1, snake2, []), spawn_food(snake1, snake2, [])]
    save_high_scores()

    
    running = True
    while running:
        screen.fill(DARK_BG)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key in snake1.keys:
                    snake1.direction = snake1.keys[event.key]
                elif event.key in snake2.keys:
                    snake2.direction = snake2.keys[event.key]

        snake1.update()
        snake2.update()

        for i, food in enumerate(foods):
            if snake1.body and snake1.body[0] == food:
                snake1.eat()
                foods[i] = spawn_food(snake1, snake2, foods)
            elif snake2.body and snake2.body[0] == food:
                snake2.eat()
                foods[i] = spawn_food(snake1, snake2, foods)

        snake1.check_collision(snake2)
        snake2.check_collision(snake1)

        snake1.draw()
        snake2.draw()

        for food in foods:
            pygame.draw.rect(screen, WHITE, (food[0]*CELL_SIZE, food[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        screen.blit(font.render(f"{snake1.score} | {player1_name}", True, WHITE), (20, 12))
        screen.blit(font.render(f"{player2_name} | {snake2.score}", True, WHITE), (WIDTH - 240, 12))

        if len(snake1.body) == 0 or len(snake2.body) == 0:
            winner_name = player1_name if len(snake2.body) == 0 else player2_name
            winner_score = snake1.score if len(snake2.body) == 0 else snake2.score

            loser_name = player2_name if winner_name == player1_name else player1_name
            loser_score = snake2.score if winner_name == player1_name else snake1.score

            high_scores.append({"name": winner_name, "score": winner_score})
            high_scores.append({"name": loser_name, "score": loser_score})

            high_scores.sort(key=lambda x: x["score"], reverse=True)
            high_scores[:] = high_scores[:10]
            save_high_scores()

            show_winner(winner_name, winner_score)
            running = False


        pygame.display.flip()
        clock.tick(FPS)


def show_winner(name, score):
    screen.fill(BLACK)
    msg = large_font.render(f"Winner: {name}", True, TURQUOISE)
    scr = font.render(f"Score: {score}", True, WHITE)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 40))
    screen.blit(scr, (WIDTH // 2 - scr.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.flip()
    pygame.time.wait(5000)

def get_player_names():
    global player1_name, player2_name, screen, WIDTH, HEIGHT
    input_box1 = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 50)
    input_box2 = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 + 10, 400, 50)
    active1, active2 = False, False
    name1, name2 = '', ''

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                input_box1 = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 50)
                input_box2 = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 + 10, 400, 50)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                active1 = input_box1.collidepoint(event.pos)
                active2 = input_box2.collidepoint(event.pos)
            elif event.type == pygame.KEYDOWN:
                if active1:
                    if event.key == pygame.K_BACKSPACE:
                        name1 = name1[:-1]
                    else:
                        name1 += event.unicode
                elif active2:
                    if event.key == pygame.K_BACKSPACE:
                        name2 = name2[:-1]
                    else:
                        name2 += event.unicode
                if event.key == pygame.K_RETURN and name1 and name2:
                    player1_name, player2_name = name1, name2
                    return

        pygame.draw.rect(screen, RED, input_box1, 3)
        pygame.draw.rect(screen, BLUE, input_box2, 3)
        txt1 = font.render(name1, True, WHITE)
        txt2 = font.render(name2, True, WHITE)
        screen.blit(txt1, (input_box1.x + 10, input_box1.y + 10))
        screen.blit(txt2, (input_box2.x + 10, input_box2.y + 10))
        screen.blit(font.render("Enter Player 1 Name:", True, WHITE), (input_box1.x, input_box1.y - 30))
        screen.blit(font.render("Enter Player 2 Name:", True, WHITE), (input_box2.x, input_box2.y - 30))
        pygame.display.flip()
        clock.tick(30)

def record_screen():
    global screen, WIDTH, HEIGHT
    running = True
    while running:
        screen.fill(BLACK)
        title = large_font.render("Top 10 Records", True, TURQUOISE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        for i, entry in enumerate(high_scores):
            line = font.render(f"{i+1}. {entry['name']} - {entry['score']}", True, WHITE)
            screen.blit(line, (WIDTH//2 - line.get_width()//2, 140 + i * 35))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                running = False
        pygame.display.flip()
        clock.tick(30)

def about_game():
    global WIDTH, HEIGHT, screen
    running = True
    lines = [
        "Builder Game: Alireza Amjadi - Sadra Abdi",
        "Game Name: Two Mar = Tomaroww = Farda",
        "Year: 2025 / 1404",
        "",
        "This is a two-player snake game.",
        "Grow your snake by eating food.",
        "Avoid crashing into walls or each other.",
        "The last player standing wins."
        "",
        "In Baze ro To Home Sadrashon Bikar Bodem Neveshtem Va Sakhtem Yadegare",
        "Bad 2 mah rekht toie hard man dorostesh kardam va public kardam",
    ]
    while running:
        screen.fill(BLACK)
        for i, line in enumerate(lines):
            text = font.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 80 + i*35))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                running = False

        pygame.display.flip()
        clock.tick(30)



def main_menu():
    global screen, WIDTH, HEIGHT
    buttons = ["Start Game", "About Game", "Record", "Full Screen", "Exit"]
    selected = -1
    is_fullscreen = False

    load_high_scores()  

    while True:
        screen.fill(DARK_BG)
        title = title_font.render("FARDA", True, TURQUOISE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        for i, text in enumerate(buttons):
            color = TURQUOISE if i == selected else WHITE
            rendered = large_font.render(text, True, color)
            rect = rendered.get_rect(center=(WIDTH//2, 250 + i*70))
            screen.blit(rendered, rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEMOTION:
                for i in range(len(buttons)):
                    if pygame.Rect(WIDTH//2 - 150, 240 + i*70, 300, 50).collidepoint(event.pos):
                        selected = i
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if selected == 0:
                    get_player_names()
                    game_loop()
                elif selected == 1:
                    about_game()
                elif selected == 2:
                    record_screen()
                elif selected == 3:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        WIDTH, HEIGHT = screen.get_size()
                    else:
                        screen = pygame.display.set_mode((960, 640), pygame.RESIZABLE)
                        WIDTH, HEIGHT = 960, 640
                elif selected == 4:
                    pygame.quit(); sys.exit()

        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    main_menu()
    pygame.quit()
    sys.exit()
