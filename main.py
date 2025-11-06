from pygame import *
import socket
import json
from threading import Thread

WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг онлайн")


STATE_MENU = 0
STATE_CONNECTING = 1
STATE_PLAYING = 2
STATE_GAME_OVER = 3
current_state = STATE_MENU


font_win = font.Font(None, 72)
font_main = font.Font(None, 36)


def connect_to_server():

    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():

    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break



class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = (200, 0, 0)
        self.hover_color = (0, 200, 0)
        self.text_color = (255, 255, 255)

    def draw(self, screen):
        color_to_use = self.hover_color if self.rect.collidepoint(mouse.get_pos()) else self.color
        draw.rect(screen, color_to_use, self.rect, border_radius=10)
        text_surface = font_main.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()


def start_game():
    global current_state, my_id, game_state, buffer, client, game_over
    current_state = STATE_CONNECTING
    screen.fill((0, 0, 0))
    connecting_text = font_main.render("Підключення до сервера...", True, (255, 255, 255))
    screen.blit(connecting_text, (WIDTH // 2 - 150, HEIGHT // 2))
    display.update()

    try:
        my_id, game_state, buffer, client = connect_to_server()
        game_over = False
        Thread(target=receive, daemon=True).start()
        current_state = STATE_PLAYING
    except Exception as e:
        err = font_main.render(f"Помилка з’єднання: {e}", True, (255, 0, 0))
        screen.blit(err, (WIDTH // 2 - 200, HEIGHT // 2))
        display.update()
        time.wait(2000)
        current_state = STATE_MENU


def exit_game():
    quit()
    exit()



menu_buttons = [
    Button(WIDTH // 2 - 100, HEIGHT // 2 - 80, 200, 50, "Грати", start_game),
    Button(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50, "Вихід", exit_game),
]


def draw_menu():
    screen.fill((0, 0, 0))
    title_text = font_win.render("Пінг-Понг онлайн", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
    for btn in menu_buttons:
        btn.draw(screen)
    display.update()



game_over = False
winner = None
you_winner = None
my_id = None
game_state = {}
buffer = ""
client = None

running = True
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

        if current_state == STATE_MENU:
            for btn in menu_buttons:
                btn.handle_event(e)


    if current_state == STATE_MENU:
        draw_menu()


    elif current_state == STATE_PLAYING:
        if "countdown" in game_state and game_state["countdown"] > 0:
            screen.fill((0, 0, 0))
            countdown_text = font_win.render(str(game_state["countdown"]), True, (255, 255, 255))
            screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
            display.update()
            continue

        if "winner" in game_state and game_state["winner"] is not None:
            screen.fill((20, 20, 20))
            if you_winner is None:
                you_winner = (game_state["winner"] == my_id)

            text = "Ти переміг!" if you_winner else "Пощастить наступним разом!"
            win_text = font_win.render(text, True, (255, 215, 0))
            text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(win_text, text_rect)
            display.update()
            continue

        if game_state:
            screen.fill((30, 30, 30))
            draw.rect(screen, (0, 255, 0), (20, game_state['paddles']['0'], 20, 100))
            draw.rect(screen, (255, 0, 255), (WIDTH - 40, game_state['paddles']['1'], 20, 100))
            draw.circle(screen, (255, 255, 255), (game_state['ball']['x'], game_state['ball']['y']), 10)
            score_text = font_main.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True,
                                          (255, 255, 255))
            screen.blit(score_text, (WIDTH // 2 - 25, 20))
        else:
            waiting_text = font_main.render("Очікування гравців...", True, (255, 255, 255))
            screen.blit(waiting_text, (WIDTH // 2 - 100, HEIGHT // 2))

        keys = key.get_pressed()
        if keys[K_w]:
            client.send(b"UP")
        elif keys[K_s]:
            client.send(b"DOWN")

        display.update()

    clock.tick(60)

quit()
