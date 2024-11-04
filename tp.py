import pygame
import os
import sys
import random

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackjack")

# Colors
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Constantes
CARD_IMAGES_DIR = r'C:\Users\maxlu\OneDrive\Documentos\Uade\Algoritmos\playing-cards-pack\Cards'
SALDOTXT_PATH = "saldonuevo.txt"
MIN_APUESTA = 100  # Apuesta mínima
MAX_APUESTA = 1000  # Apuesta máxima
INCREMENTO_APUESTA = 100  # Incremento de apuesta

# Fuente para el texto
font = pygame.font.SysFont(None, 36)

# Cargar las imágenes de las cartas
def load_card_images():
    card_images = {}
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    for suit in suits:
        for rank in ranks:
            card_name = f"card_{suit}_0{rank}"
            image_path = os.path.join(CARD_IMAGES_DIR, f"{card_name}.png")
            card_images[card_name] = pygame.image.load(image_path).convert_alpha()
    
    # Cargar imagen del reverso de la carta
    card_images['card_back'] = pygame.image.load(os.path.join(CARD_IMAGES_DIR, "card_back.png")).convert_alpha()
    
    return card_images

# Crear la baraja de cartas
def create_deck():
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [(rank, suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

# Calcular el valor de una mano
def calculate_hand_value(hand):
    value = 0
    aces = 0
    for rank, suit in hand:
        if rank in ['J', 'Q', 'K']:
            value += 10
        elif rank == 'A':
            aces += 1
            value += 11
        else:
            value += int(rank)
    
    while value > 21 and aces:
        value -= 10
        aces -= 1
    
    return value

# Repartir una carta
def deal_card(deck, hand):
    hand.append(deck.pop())

# Dibujar una carta en la pantalla
def draw_card(screen, card_image, x, y):
    screen.blit(card_image, (x, y))

# Dibujar la mano en la pantalla
def draw_hand(screen, hand, card_images, x, y, hide_second=False):
    for i, (rank, suit) in enumerate(hand):
        if i == 1 and hide_second:
            draw_card(screen, card_images['card_back'], x + i * 30, y)
        else:
            card_name = f"card_{suit}_0{rank}"
            draw_card(screen, card_images[card_name], x + i * 30, y)

# Función para dibujar texto en pantalla
def draw_text(screen, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Función para leer el saldo
def leer_saldo():
    try:
        with open(SALDOTXT_PATH, "r") as file:
            lines = file.readlines()
            last_line = lines[-1]
            saldo = int(last_line.split(":")[-1].strip())
    except (FileNotFoundError, IndexError):
        saldo = 1000  # Saldo inicial si el archivo no existe o está vacío
    return saldo

# Función para registrar el resultado en el archivo de saldo
def registrar_resultado(resultado, saldo_actual, apuesta):
    with open(SALDOTXT_PATH, "a") as file:
        if resultado == "win":
            file.write(f"Resultado: Ganaste, saldo actual: {saldo_actual + apuesta}\n")
        elif resultado == "lose":
            file.write(f"Resultado: Perdiste, saldo actual: {saldo_actual - apuesta}\n")
        elif resultado == "tie":
            file.write(f"Resultado: Empate, saldo actual: {saldo_actual}\n")
        else:
            file.write(f"Saldo actual: {saldo_actual}\n")

# Reiniciar el juego
def reset_game():
    global deck, player_hand, dealer_hand, player_standing, game_over, result, saldo, apuesta
    deck = create_deck()
    player_hand = []
    dealer_hand = []
    player_standing = False
    game_over = False
    result = ""
    saldo = leer_saldo()
    apuesta = MIN_APUESTA  # Apuesta inicial

    deal_card(deck, player_hand)
    deal_card(deck, player_hand)
    deal_card(deck, dealer_hand)
    deal_card(deck, dealer_hand)

# Bucle principal del juego
def main():
    global deck, player_hand, dealer_hand, player_standing, game_over, result, saldo, apuesta
    clock = pygame.time.Clock()
    card_images = load_card_images()
    reset_game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h and not player_standing and not game_over:
                    deal_card(deck, player_hand)
                    if calculate_hand_value(player_hand) > 21:
                        result = "Perdiste, te pasaste de 21."
                        saldo -= apuesta
                        registrar_resultado("lose", saldo, apuesta)
                        game_over = True
                elif event.key == pygame.K_s and not player_standing:
                    player_standing = True
                elif event.key == pygame.K_r and game_over:
                    reset_game()
                elif event.key == pygame.K_q and game_over:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_UP:  # Aumentar apuesta
                    if apuesta + INCREMENTO_APUESTA <= MAX_APUESTA:
                        apuesta += INCREMENTO_APUESTA
                elif event.key == pygame.K_DOWN:  # Reducir apuesta
                    if apuesta - INCREMENTO_APUESTA >= MIN_APUESTA:
                        apuesta -= INCREMENTO_APUESTA

        if player_standing and not game_over:
            while calculate_hand_value(dealer_hand) < 17:
                deal_card(deck, dealer_hand)

            player_value = calculate_hand_value(player_hand)
            dealer_value = calculate_hand_value(dealer_hand)

            if dealer_value > 21:
                result = "¡Ganaste! El dealer se pasó de 21."
                saldo += apuesta
                registrar_resultado("win", saldo, apuesta)
            elif player_value > dealer_value:
                result = "¡Ganaste!"
                saldo += apuesta
                registrar_resultado("win", saldo, apuesta)
            elif player_value < dealer_value:
                result = "Perdiste..."
                saldo -= apuesta
                registrar_resultado("lose", saldo, apuesta)
            else:
                result = "Empate"
                registrar_resultado("tie", saldo)
            game_over = True

        screen.fill(GREEN)
        pygame.draw.rect(screen, WHITE, (50, 50, WIDTH - 100, HEIGHT - 200), 5)

        draw_hand(screen, player_hand, card_images, 100, 400)
        draw_hand(screen, dealer_hand, card_images, 100, 100, hide_second=not player_standing)

        player_value = calculate_hand_value(player_hand)
        dealer_value = calculate_hand_value(dealer_hand) if player_standing else calculate_hand_value(dealer_hand[:-1])
        draw_text(screen, f"Jugador: {player_value}", font, WHITE, 50, 350)
        draw_text(screen, f"Dealer: {dealer_value}", font, BLACK, 50, 50)
        draw_text(screen, f"Saldo actual: {saldo}", font, WHITE, 500, 150)
        draw_text(screen, f"Apuesta: {apuesta}", font, RED, 500, 100)

        if game_over:
            draw_text(screen, result, font, WHITE, 50, 500)
            draw_text(screen, "Presiona 'R' para reiniciar o 'Q' para salir", font, WHITE, 50, 550)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
