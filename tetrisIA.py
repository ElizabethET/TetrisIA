import pygame
import random

#se inicia pygame
pygame.init()

#dimenciones de pantalla
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
CELL_SIZE = 30

#los colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

#dimensiones del tablero
COLS = SCREEN_WIDTH // CELL_SIZE
ROWS = SCREEN_HEIGHT // CELL_SIZE

#Las Piezas del Tetris
shapes = [
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1], [1, 1]],        # O
    [[1, 1, 1, 1]],          # I
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
]

#para que tome una pieza en aleatorio
def new_piece():
    return random.choice(shapes)

#función para rotar la pieza
def rotate_clockwise(shape):
    return [list(row) for row in zip(*shape[::-1])]

# Clase para el tablero
class Board:
    def __init__(self):
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.piece = new_piece()
        self.piece_x = COLS // 2 - len(self.piece[0]) // 2
        self.piece_y = 0
        self.score = 0
        self.game_over = False
        self.ai_active = False

    def draw_grid(self, screen):
        for y in range(ROWS):
            for x in range(COLS):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, GRAY, rect, 1)
    
    def draw_board(self, screen):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, BLUE, rect)
    
    def draw_piece(self, screen):
        for y, row in enumerate(self.piece):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect((self.piece_x + x) * CELL_SIZE, (self.piece_y + y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, BLUE, rect)

    def move_piece(self, dx, dy):
        if not self.collision(dx, dy):
            self.piece_x += dx
            self.piece_y += dy
        else:
            # Aquí podrías manejar la colisión si es necesario
            if dy > 0:  # Solo si está moviendo hacia abajo
                self.merge_piece()  # Combina la pieza con el tablero
                self.piece = new_piece()
                self.piece_x = COLS // 2 - len(self.piece[0]) // 2
                self.piece_y = 0
                if self.collision(0, 0):
                    self.game_over = True

    def collision(self, dx, dy, rotated_piece=None):
        piece = rotated_piece if rotated_piece else self.piece
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.piece_x + x + dx
                    new_y = self.piece_y + y + dy
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS or self.grid[new_y][new_x]:
                        return True
        return False
    
    def rotate_piece(self):
        rotated_piece = rotate_clockwise(self.piece)
        if not self.collision(0, 0, rotated_piece):
            self.piece = rotated_piece
    
    def merge_piece(self):
        for y, row in enumerate(self.piece):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.piece_y + y][self.piece_x + x] = 1
        self.clear_lines()
    
    def clear_lines(self):
        new_grid = [row for row in self.grid if not all(row)]
        lines_cleared = ROWS - len(new_grid)
        self.score += lines_cleared
        self.grid = [[0 for _ in range(COLS)] for _ in range(lines_cleared)] + new_grid

    def reset(self):
        self.__init__()

    # Activar IA
    def activate_ai(self):
        self.ai_active = not self.ai_active
        if self.ai_active:
            # Reiniciar la mejor posición cuando se activa la IA
            if hasattr(self, 'best_x'):
                del self.best_x
            if hasattr(self, 'best_rotation'):
                del self.best_rotation


    def ai_move_step(self):
        if not self.ai_active:  # Solo permitir movimiento si la IA está activa
            return

        best_x = self.piece_x
        best_y = self.piece_y
        best_rotation = self.piece

        # Probar cada rotación posible
        for rotation in range(4):
            rotated_piece = rotate_clockwise(self.piece)  # Obtener la rotación
            self.piece = rotated_piece  # Usar la pieza rotada

            # Probar cada columna en el tablero
            for x in range(COLS):
                self.piece_x = x
                self.piece_y = 0  # Reiniciar la posición Y para empezar desde arriba

                # Mover la pieza hacia abajo hasta que colisione
                while not self.collision(0, 1):  # Mover hacia abajo
                    self.piece_y += 1

                # Ajustar la posición a la fila más baja donde puede encajar
                if self.piece_y > 0:  # Asegurarse de que la pieza se haya movido al menos una fila
                    self.piece_y -= 1  # Llevarla a la fila justo por encima de la última colisión

                # Si esta posición es mejor (más baja) que la mejor encontrada, guardarla
                if self.piece_y > best_y:
                    best_y = self.piece_y
                    best_x = x
                    best_rotation = self.piece.copy()

            # Restaurar la pieza original para la siguiente rotación
            self.piece = rotated_piece

        # Establecer la mejor posición encontrada
        self.piece = best_rotation
        self.piece_x = best_x
        self.piece_y = best_y

        # Mover la pieza a la fila más baja posible en la columna elegida
        while not self.collision(0, 1):  # Comprobar si se puede mover hacia abajo
            self.move_piece(0, 1)

        # Fusionar la pieza si no puede bajar
        self.merge_piece()
        self.piece = new_piece()  # Generar nueva pieza
        self.piece_x = COLS // 2 - len(self.piece[0]) // 2
        self.piece_y = 0
        if self.collision(0, 0):
            self.game_over = True  # Fin del juego si la nueva pieza no encaja

    def evaluate_position(self):
                                    score = 0
                                    # Evaluar cuántas líneas se pueden completar
                                    for y in range(ROWS):
                                        if all(self.grid[y][x] != 0 for x in range(COLS)):  # Comprobar si la línea está llena
                                            score += 100  # Aumentar puntuación si se puede completar una línea

                                    # Penalizar líneas vacías más arriba para que las piezas se acumulen en la parte inferior
                                    for y in range(ROWS - 1, -1, -1):
                                        if any(self.grid[y][x] == 0 for x in range(COLS)):
                                            score -= 10  # Penalizar por líneas vacías hacia arriba

                                    # Añadir lógica para colocar las piezas más cerca unas de otras
                                    for y in range(ROWS):
                                        for x in range(COLS):
                                            if self.grid[y][x] == 1:  # Si hay una pieza en esta celda
                                                if x > 0 and self.grid[y][x - 1] == 0:  # Verificar si hay espacio a la izquierda
                                                    score += 5  # Bonificación por espacios vacíos a la izquierda
                                                if x < COLS - 1 and self.grid[y][x + 1] == 0:  # Verificar si hay espacio a la derecha
                                                    score += 5  # Bonificación por espacios vacíos a la derecha

                                    return score  # Devuelve la puntuación total

# Crear la pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# Definir el reloj
clock = pygame.time.Clock()

# Crear el tablero
board = Board()

# Fuente para el marcador
font = pygame.font.SysFont('Arial', 20)

# Variables para controlar la velocidad de caída
fall_time = 0
fall_speed = 500  # 500 milisegundos (medio segundo) entre cada caída

# Bucle principal del juego
running = True
while running:
    screen.fill(BLACK)
    
    # Incrementar el tiempo de caída
    fall_time += clock.get_rawtime()
    
    # Actualizar el reloj
    clock.tick()

    # Mover la pieza hacia abajo si el tiempo de caída ha superado el límite
    if fall_time >= fall_speed:
        # Si la IA está activa, mueve la pieza usando el método AI
        if board.ai_active:
            board.ai_move_step()
        else:
            # Intentar mover la pieza hacia abajo
            if not board.collision(0, 1):  # Comprobar si puede bajar
                board.move_piece(0, 1)  # Mover hacia abajo
            else:
                board.merge_piece()  # Si no puede bajar, combinar con el tablero

        fall_time = 0

    # Dibujar la cuadrícula, el tablero y la pieza
    board.draw_grid(screen)
    board.draw_board(screen)
    board.draw_piece(screen)
    
    # Dibujar el marcador
    score_text = font.render(f"Score: {board.score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Botón de reiniciar
    restart_button = pygame.Rect(SCREEN_WIDTH - 80, 10, 70, 30)
    pygame.draw.rect(screen, WHITE, restart_button)
    restart_text = font.render("Restart", True, BLACK)
    screen.blit(restart_text, (SCREEN_WIDTH - 75, 15))
    
    # Botón de activar IA
    ai_button = pygame.Rect(SCREEN_WIDTH - 80, 50, 70, 30)
    pygame.draw.rect(screen, GREEN, ai_button)
    ai_text = font.render("IA", True, BLACK)
    screen.blit(ai_text, (SCREEN_WIDTH - 60, 55))

    pygame.display.update()
    
    # Procesar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if restart_button.collidepoint(event.pos):
                board.reset()
            if ai_button.collidepoint(event.pos):
                board.activate_ai()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and not board.ai_active:
                board.move_piece(-1, 0)
            if event.key == pygame.K_RIGHT and not board.ai_active:
                board.move_piece(1, 0)
            if event.key == pygame.K_DOWN and not board.ai_active:
                board.move_piece(0, 1)  # Movimiento hacia abajo manual
            if event.key == pygame.K_UP and not board.ai_active:
                board.rotate_piece()

    if board.game_over:
        running = False

pygame.quit()
