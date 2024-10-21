#Se importan las bibliotecas 
import pygame
import random

#se inicia pygame
pygame.init()

#dimenciones de pantalla
ANCHO = 300
ALTURA = 600
CELL_SIZE = 30

#los colores que se vana  usar
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (128, 128, 128)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)

#el numero de columnas y filas en el tablero 
#dividiendo el ancho y alto de la pantalla por el tamano de las celdas
COLS = ANCHO // CELL_SIZE
ROWS = ALTURA // CELL_SIZE

#forma de las piezas del juego/tetrimonios
figuras = [
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1], [1, 1]],        # O
    [[1, 1, 1, 1]],          # I
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
]

#para que tome una pieza en aleatorio
def nuevaPieza():
    return random.choice(figuras)

#función para rotar la pieza
def girarDerecha(figura):
    return [list(row) for row in zip(*figura[::-1])]

# clase para el tablero
class Tablero:
    def __init__(self): #se inicia el tablero
        self.cuadricula = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.pieza = nuevaPieza()
        self.pieza_x = COLS // 2 - len(self.pieza[0]) // 2
        self.pieza_y = 0
        self.puntos = 0
        self.game_over = False
        self.ia_active = False

    def dibuja_cuadricula(self, screen): #se crea la cuadricula
        for y in range(ROWS):
            for x in range(COLS):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, GRIS, rect, 1)
    
    def dibuja_Tablero(self, screen): #las celdas ocupadas estaran de Azul
        for y, row in enumerate(self.cuadricula):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, AZUL, rect)
    
    def dibuja_pieza(self, screen): #la pieza actual
        for y, row in enumerate(self.pieza):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect((self.pieza_x + x) * CELL_SIZE, (self.pieza_y + y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, AZUL, rect)

    def mover_pieza(self, dx, dy): #puedes moverr la pieza de izquierda a derecha con dx o dy
        if not self.colision(dx, dy):
            self.pieza_x += dx
            self.pieza_y += dy
        else:
            #manejar la colisión si es necesario
            if dy > 0:  # si está moviendo hacia abajo
                self.unir_pieza()  #combina la pieza con el tablero
                self.pieza = nuevaPieza()
                self.pieza_x = COLS // 2 - len(self.pieza[0]) // 2
                self.pieza_y = 0
                if self.colision(0, 0):
                    self.game_over = True

    def colision(self, dx, dy, rotard_pieza=None): #con la colision se verifica si la nueva pieza choca con el fondo del tablero o con otra pieza
        pieza = rotard_pieza if rotard_pieza else self.pieza
        for y, row in enumerate(pieza):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.pieza_x + x + dx
                    new_y = self.pieza_y + y + dy
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS or self.cuadricula[new_y][new_x]:
                        return True
        return False
    
    def rotar_pieza(self): #se puede rotar la pieza actual si aun no ha colisionado con nada
        rotard_pieza = girarDerecha(self.pieza)
        if not self.colision(0, 0, rotard_pieza):
            self.pieza = rotard_pieza
    
    def unir_pieza(self): #se unen las piezas con el tablero o cuando chocan entre si
        for y, row in enumerate(self.pieza):
            for x, cell in enumerate(row):
                if cell:
                    self.cuadricula[self.pieza_y + y][self.pieza_x + x] = 1
        self.lineaCompleta()
    
    def lineaCompleta(self): #se eliminan las lineas horizontales cuando se llenan todos los campos y se
        new_cuadricula = [row for row in self.cuadricula if not all(row)]
        lines_cleared = ROWS - len(new_cuadricula)
        self.puntos += lines_cleared
        self.cuadricula = [[0 for _ in range(COLS)] for _ in range(lines_cleared)] + new_cuadricula

    def reset(self):
        self.__init__()



    # Activar IA
    def activate_ai(self):
        self.ia_active = not self.ia_active
        if self.ia_active:
            # Reiniciar la mejor posición cuando se activa la IA
            if hasattr(self, 'best_x'):
                del self.best_x
            if hasattr(self, 'best_rotation'):
                del self.best_rotation


    #calcula los movimientos de la IA
    def movimientos_ia(self):
        if not self.ia_active:  # Solo permitir movimiento si la IA está activa
            return

        best_x = self.pieza_x
        best_y = self.pieza_y
        best_rotation = self.pieza

        #probar cada rotación posible
        for rotation in range(4):
            rotard_pieza = girarDerecha(self.pieza)  # Obtener la rotación
            self.pieza = rotard_pieza  # Usar la pieza rotada

            # Probar cada columna en el tablero
            for x in range(COLS):
                self.pieza_x = x
                self.pieza_y = 0  #reiniciar la posición Y para empezar desde arriba

                # mover la pieza hacia abajo hasta que colisione
                while not self.colision(0, 1):  # mover hacia abajo
                    self.pieza_y += 1

                # Ajustar la posición a la fila 
                if self.pieza_y > 0:  # asegurarse de que la pieza se haya movido al menos una fila
                    self.pieza_y -= 1  # llevarla a la fila justo por encima de la última colisión

                #busca la posicion más baja donde puede encajar para lograr llenar una linea en horizontal
                if self.pieza_y > best_y:
                    best_y = self.pieza_y
                    best_x = x
                    best_rotation = self.pieza.copy()

            #la siguiente rotación
            self.pieza = rotard_pieza

        #la mejor posición encontrada
        self.pieza = best_rotation
        self.pieza_x = best_x
        self.pieza_y = best_y

        # mover la pieza a la fila más baja posible en la columna elegida
        while not self.colision(0, 1):  #comprobar si se puede mover hacia abajo
            self.mover_pieza(0, 1)

        #unir piezas al chocar
        self.unir_pieza()
        self.pieza = nuevaPieza()  #se generara una nueva pieza
        self.pieza_x = COLS // 2 - len(self.pieza[0]) // 2
        self.pieza_y = 0
        if self.colision(0, 0):
            self.game_over = True  #fin del juego si la nueva pieza no encaja mas en el tablero

    def calcular_posicion(self):
            puntos = 0
            #ver cuantas lineas se pueden completar
            for y in range(ROWS):
                if all(self.cuadricula[y][x] != 0 for x in range(COLS)):  #ver si la línea está llena
                    puntos += 100  #puntos si se completa la linea

            #que las piezas se acumulen en la parte inferior
            for y in range(ROWS - 1, -1, -1):
                if any(self.cuadricula[y][x] == 0 for x in range(COLS)):
                    puntos -= 10  #penalizar por líneas vacías hacia arriba

            # anadir piezas cerca unas de otras
            for y in range(ROWS):
                for x in range(COLS):
                    if self.cuadricula[y][x] == 1:  #ver si hay una pieza en esta celda
                        if x > 0 and self.cuadricula[y][x - 1] == 0:  # Versi hay espacio a la izquierda
                            puntos += 5  #se van acumulando puntos
                        if x < COLS - 1 and self.cuadricula[y][x + 1] == 0:  # Versi hay espacio a la derecha
                            puntos += 5  # ve acumulan puntos tambien

            return puntos  #puntuacion final

#VISIBILIDAD DEL JUEGO

# Crear la pantalla
screen = pygame.display.set_mode((ANCHO, ALTURA))
pygame.display.set_caption("Tetris")

#definir el reloj
clock = pygame.time.Clock()

#se crea el tablero
Tablero = Tablero()

#letra del marcador
font = pygame.font.SysFont('Arial', 20)

#la velocidad de caída
fall_time = 0
fall_speed = 500  # 500 milisegundos = medio segundo entre cada caída

#Bucle principal del juego
running = True
while running:
    screen.fill(NEGRO) #fondo negro
    
    #incrementar el tiempo de caída
    fall_time += clock.get_rawtime()
    
    clock.tick()

    # moverr la pieza hacia abajo por si sola
    if fall_time >= fall_speed:
        #si la IA está activa se mueve la pieza usando el método ia
        if Tablero.ia_active:
            Tablero.movimientos_ia()
        else:
            # Intentar moverr la pieza hacia abajo
            if not Tablero.colision(0, 1):  # Comprobar si puede bajar
                Tablero.mover_pieza(0, 1)  # mover hacia abajo
            else:
                Tablero.unir_pieza()  

        fall_time = 0

    #dibujar la cuadricula, el tablero y la pieza
    Tablero.dibuja_cuadricula(screen)
    Tablero.dibuja_Tablero(screen)
    Tablero.dibuja_pieza(screen)
    
    #marcador
    puntos_text = font.render(f"puntos: {Tablero.puntos}", True, BLANCO)
    screen.blit(puntos_text, (10, 10))

    #botón reiniciar
    restart_button = pygame.Rect(ANCHO - 80, 10, 70, 30)
    pygame.draw.rect(screen, BLANCO, restart_button)
    restart_text = font.render("Restart", True, NEGRO)
    screen.blit(restart_text, (ANCHO - 75, 15))
    
    # Botón IA
    ia_button = pygame.Rect(ANCHO - 80, 50, 70, 30)
    pygame.draw.rect(screen, VERDE, ia_button)
    ia_text = font.render("IA", True, NEGRO)
    screen.blit(ia_text, (ANCHO - 60, 55))

    pygame.display.update()
    
    #los eventos con las teclas
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN: #con el mouse se puede activar la ia o resetear
            if restart_button.collidepoint(event.pos):
                Tablero.reset()
            if ia_button.collidepoint(event.pos):
                Tablero.activate_ai()
        if event.type == pygame.KEYDOWN: #presionar una tecla
            if event.key == pygame.K_LEFT and not Tablero.ia_active: #hacia izquierda
                Tablero.mover_pieza(-1, 0)
            if event.key == pygame.K_RIGHT and not Tablero.ia_active: #hacia derecha
                Tablero.mover_pieza(1, 0)
            if event.key == pygame.K_DOWN and not Tablero.ia_active: #hacia abajo baja mas rapido la pieza
                Tablero.mover_pieza(0, 1)  # Movimiento hacia abajo manual
            if event.key == pygame.K_UP and not Tablero.ia_active: #hacia arriba se rota la pieza
                Tablero.rotar_pieza()

    if Tablero.game_over:
        running = False

pygame.quit()
