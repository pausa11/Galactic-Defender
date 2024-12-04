import pygame
import sys
import random
from moviepy import VideoFileClip
import os

# Inicialización de Pygame
pygame.init()
pygame.mixer.init()

# Configuración de la pantalla
ANCHO, ALTO = 800, 600
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Galactic Defender")

# Reloj para controlar los FPS
FPS = 60
RELOJ = pygame.time.Clock()

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (100, 100, 100)
AZUL = (0, 0, 255)

# Cargar imágenes (asegúrate de tener estas imágenes en la ruta especificada)
imagen_nave = pygame.image.load('assets/nave_jugador.png').convert_alpha()
imagen_enemigo = pygame.image.load('assets/nave_enemiga.png').convert_alpha()
imagen_proyectil_jugador = pygame.image.load('assets/proyectil_jugador.png').convert_alpha()
imagen_proyectil_enemigo = pygame.image.load('assets/proyectil_enemigo.png').convert_alpha()
imagen_powerup = pygame.image.load('assets/powerup.png').convert_alpha()
imagen_jefe = pygame.image.load('assets/jefe.png').convert_alpha()

# Cargar imagen de fondo
try:
    imagen_fondo = pygame.image.load('assets/fondo.jpg').convert()
    # Opcional: Redimensionar si la imagen no tiene el tamaño correcto
    imagen_fondo = pygame.transform.scale(imagen_fondo, (ANCHO, ALTO))
except pygame.error as e:
    print(f"Error al cargar la imagen de fondo: {e}")
    # En caso de error, rellenar con negro
    imagen_fondo = pygame.Surface((ANCHO, ALTO))
    imagen_fondo.fill(NEGRO)

# Cargar sonidos
sonido_disparo = pygame.mixer.Sound('assets/sonido_disparo.wav')
sonido_explosion = pygame.mixer.Sound('assets/sonido_explosion.wav')
musica_fondo = 'assets/musica_fondo.mp3'

# Fuentes
fuente_puntuacion = pygame.font.SysFont('Arial', 25)
fuente_menu = pygame.font.SysFont('Arial', 50)
fuente_fin = pygame.font.SysFont('Arial', 40)

def reproducir_video(ruta_video):
    # Cargar el video con MoviePy
    clip = VideoFileClip(ruta_video)
    
    # Escalar el video si es necesario
    if clip.size != (ANCHO, ALTO):
        clip = clip.resized(width=ANCHO, height=ALTO)
    
    # Reproducir el audio del video
    audio_temp = 'temp_audio.mp3'
    if clip.audio:
        clip.audio.write_audiofile(audio_temp, logger=None)  # logger=None para evitar mensajes en la consola
        pygame.mixer.music.load(audio_temp)
        pygame.mixer.music.play()
    
    # Reproducir el video frame por frame
    for frame in clip.iter_frames(fps=FPS, dtype="uint8"):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()  # Descarga el audio del mezclador
                clip.close()
                if os.path.exists(audio_temp):
                    os.remove(audio_temp)
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()  # Descarga el audio del mezclador
                    clip.close()
                    if os.path.exists(audio_temp):
                        os.remove(audio_temp)
                    return  # Salir de la función y pasar al menú
    
        # Convertir el frame a una superficie de Pygame
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.flip(frame_surface, True, False)
    
        # Dibujar el frame en la ventana
        VENTANA.blit(frame_surface, (0, 0))
        pygame.display.update()
        RELOJ.tick(FPS)
    
    # Cerrar el clip y detener el audio al finalizar el video
    clip.close()
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()  # Descarga el audio del mezclador
    if os.path.exists(audio_temp):
        os.remove(audio_temp)

# Clases
class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = imagen_nave
        self.rect = self.image.get_rect(center=(ANCHO // 2, ALTO - 70))
        self.velocidad = 5
        self.vida = 3
        self.puntuacion = 0

    def update(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocidad
        if teclas[pygame.K_RIGHT] and self.rect.right < ANCHO:
            self.rect.x += self.velocidad
        if teclas[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.velocidad
        if teclas[pygame.K_DOWN] and self.rect.bottom < ALTO:
            self.rect.y += self.velocidad

    def disparar(self):
        proyectil = Proyectil(self.rect.centerx, self.rect.top, -10, 'jugador')
        todos_los_sprites.add(proyectil)
        proyectiles_jugador.add(proyectil)
        sonido_disparo.play()

class Proyectil(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidad, propietario):
        super().__init__()
        if propietario == 'jugador':
            self.image = imagen_proyectil_jugador
        else:
            self.image = imagen_proyectil_enemigo
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = velocidad
        self.propietario = propietario

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.bottom < 0 or self.rect.top > ALTO:
            self.kill()

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, nivel):
        super().__init__()
        self.image = imagen_enemigo
        self.rect = self.image.get_rect(
            center=(random.randint(20, ANCHO - 20), random.randint(-100, -40))
        )
        self.velocidad = random.randint(1 + nivel, 2 + nivel)
        self.vida = 1 + nivel // 2
        self.tiempo_disparo = random.randint(30, 120)

    def update(self):
        self.rect.y += self.velocidad
        self.tiempo_disparo -= 1
        if self.tiempo_disparo <= 0:
            self.disparar()
            self.tiempo_disparo = random.randint(60, 120)
        if self.rect.top > ALTO:
            self.kill()

    def disparar(self):
        proyectil = Proyectil(self.rect.centerx, self.rect.bottom, 5, 'enemigo')
        todos_los_sprites.add(proyectil)
        proyectiles_enemigos.add(proyectil)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = imagen_powerup
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 3

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.top > ALTO:
            self.kill()

class Jefe(pygame.sprite.Sprite):
    def __init__(self, nivel):
        super().__init__()
        self.image = imagen_jefe
        self.rect = self.image.get_rect(center=(ANCHO // 2, -150))
        self.velocidad = 2
        self.vida = 20 + nivel * 10
        self.tiempo_disparo = 50
        self.direccion = 1  # 1: derecha, -1: izquierda

    def update(self):
        # Movimiento hacia abajo al inicio
        if self.rect.top < 50:
            self.rect.y += self.velocidad
        else:
            # Movimiento horizontal
            self.rect.x += self.velocidad * self.direccion
            if self.rect.right >= ANCHO or self.rect.left <= 0:
                self.direccion *= -1

            # Disparo
            self.tiempo_disparo -= 1
            if self.tiempo_disparo <= 0:
                self.disparar()
                self.tiempo_disparo = 30

    def disparar(self):
        proyectil = Proyectil(self.rect.centerx, self.rect.bottom, 7, 'enemigo')
        todos_los_sprites.add(proyectil)
        proyectiles_enemigos.add(proyectil)

# Función para mostrar el menú de inicio
def mostrar_menu():
    seleccion = 0  # 0: Jugar, 1: Salir
    opciones = ["Jugar", "Salir"]
    esperando = True

    while esperando:
        RELOJ.tick(FPS)
        VENTANA.fill(NEGRO)
        texto_titulo = fuente_menu.render("GALACTIC DEFENDER", True, BLANCO)
        VENTANA.blit(texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, ALTO // 2 - 150))

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                if evento.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                if evento.key == pygame.K_RETURN:
                    if seleccion == 0:
                        esperando = False  # Iniciar juego
                    elif seleccion == 1:
                        pygame.quit()
                        sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    mouse_click = True

        # Dibujar botones
        botones = []
        for i, opcion in enumerate(opciones):
            if i == seleccion:
                color = AZUL
            else:
                color = BLANCO

            # Detectar hover con el mouse
            texto_opcion = fuente_fin.render(opcion, True, color)
            rect_opcion = texto_opcion.get_rect()
            rect_opcion.center = (ANCHO // 2, ALTO // 2 + i * 60)
            botones.append((rect_opcion, opcion))
            if rect_opcion.collidepoint(mouse_pos):
                color = AZUL
                texto_opcion = fuente_fin.render(opcion, True, color)
                seleccion = i  # Actualizar selección con el mouse
                if mouse_click:
                    if opcion == "Jugar":
                        esperando = False  # Iniciar juego
                    elif opcion == "Salir":
                        pygame.quit()
                        sys.exit()
            VENTANA.blit(texto_opcion, rect_opcion)

        pygame.display.flip()

# Función para mostrar la pantalla de fin de juego
def mostrar_fin_juego(ganaste, puntuacion):
    VENTANA.fill(NEGRO)
    if ganaste:
        mensaje = "¡Has ganado!"
    else:
        mensaje = "Juego terminado"
    texto_fin = fuente_fin.render(mensaje, True, BLANCO)
    texto_puntuacion = fuente_puntuacion.render(f"Puntuación: {puntuacion}", True, BLANCO)
    texto_reiniciar = fuente_puntuacion.render("Presiona ENTER para volver al menú", True, BLANCO)
    VENTANA.blit(texto_fin, (ANCHO // 2 - texto_fin.get_width() // 2, ALTO // 2 - 50))
    VENTANA.blit(texto_puntuacion, (ANCHO // 2 - texto_puntuacion.get_width() // 2, ALTO // 2))
    VENTANA.blit(texto_reiniciar, (ANCHO // 2 - texto_reiniciar.get_width() // 2, ALTO // 2 + 50))
    pygame.display.flip()

    esperando = True
    while esperando:
        RELOJ.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    esperando = False

# Función principal del juego
def juego():
    # Reproducir música de fondo
    pygame.mixer.music.load(musica_fondo)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Repetir indefinidamente

    # Grupos de sprites
    global todos_los_sprites, enemigos, proyectiles_jugador, proyectiles_enemigos, powerups
    todos_los_sprites = pygame.sprite.Group()
    enemigos = pygame.sprite.Group()
    proyectiles_jugador = pygame.sprite.Group()
    proyectiles_enemigos = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    # Instancia del jugador
    jugador = Jugador()
    todos_los_sprites.add(jugador)

    # Variables de nivel y enemigos
    nivel = 1
    enemigos_eliminados = 0
    enemigos_por_nivel = {1: 10, 2: 15}
    jefe_generado = False

    # Temporizadores
    GENERAR_ENEMIGO = pygame.USEREVENT + 1
    pygame.time.set_timer(GENERAR_ENEMIGO, max(200, 1000 - nivel * 100))  # Aumenta la frecuencia con el nivel
    GENERAR_POWERUP = pygame.USEREVENT + 2
    pygame.time.set_timer(GENERAR_POWERUP, 10000)  # Cada 10 segundos

    # Bucle principal del juego
    ejecutando = True
    while ejecutando:
        RELOJ.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == GENERAR_ENEMIGO and not jefe_generado:
                enemigo = Enemigo(nivel)
                todos_los_sprites.add(enemigo)
                enemigos.add(enemigo)
            elif evento.type == GENERAR_POWERUP:
                x = random.randint(20, ANCHO - 20)
                powerup = PowerUp(x, -20)
                todos_los_sprites.add(powerup)
                powerups.add(powerup)
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    jugador.disparar()

        # Actualizaciones
        todos_los_sprites.update()

        # Colisiones entre proyectiles del jugador y enemigos
        colisiones_enemigos = pygame.sprite.groupcollide(enemigos, proyectiles_jugador, False, True)
        for enemigo, proyectiles in colisiones_enemigos.items():
            enemigo.vida -= len(proyectiles)
            if enemigo.vida <= 0:
                enemigo.kill()
                sonido_explosion.play()
                jugador.puntuacion += 100
                enemigos_eliminados += 1

        # Colisiones entre proyectiles del jugador y el jefe
        if jefe_generado:
            colisiones_jefe = pygame.sprite.spritecollide(jefe, proyectiles_jugador, True)
            for proyectil in colisiones_jefe:
                jefe.vida -= 1
                if jefe.vida <= 0:
                    jefe.kill()
                    sonido_explosion.play()
                    jugador.puntuacion += 1000
                    jefe_generado = False
                    nivel += 1
                    enemigos_eliminados = 0
                    if nivel > 2:
                        # Fin del juego (has ganado)
                        ejecutando = False
                        mostrar_fin_juego(True, jugador.puntuacion)
                        break

        # Colisiones entre jugador y proyectiles enemigos
        colisiones_jugador_proyectiles = pygame.sprite.spritecollide(jugador, proyectiles_enemigos, True)
        if colisiones_jugador_proyectiles:
            jugador.vida -= 1
            if jugador.vida <= 0:
                ejecutando = False
                mostrar_fin_juego(False, jugador.puntuacion)
                break

        # Colisiones entre jugador y enemigos
        colisiones_jugador_enemigos = pygame.sprite.spritecollide(jugador, enemigos, True)
        if colisiones_jugador_enemigos:
            jugador.vida -= 1
            sonido_explosion.play()
            if jugador.vida <= 0:
                ejecutando = False
                mostrar_fin_juego(False, jugador.puntuacion)
                break

        # Colisiones entre jugador y power-ups
        colisiones_powerups = pygame.sprite.spritecollide(jugador, powerups, True)
        for powerup in colisiones_powerups:
            # Implementa el efecto del power-up (ejemplo: vida extra)
            jugador.vida += 1

        # Verificar si se debe generar el jefe
        if enemigos_eliminados >= enemigos_por_nivel[nivel] and not jefe_generado:
            jefe = Jefe(nivel)
            todos_los_sprites.add(jefe)
            jefe_generado = True

        # Dibujar el fondo
        VENTANA.blit(imagen_fondo, (0, 0))  # Dibujar el fondo antes de los sprites

        # Dibujar sprites
        todos_los_sprites.draw(VENTANA)

        # Mostrar puntuación y vida
        texto_puntuacion = fuente_puntuacion.render(f"Puntuación: {jugador.puntuacion}", True, BLANCO)
        texto_vida = fuente_puntuacion.render(f"Vida: {jugador.vida}", True, BLANCO)
        VENTANA.blit(texto_puntuacion, (10, 10))
        VENTANA.blit(texto_vida, (ANCHO - 100, 10))

        pygame.display.flip()

    # Detener la música al salir del juego
    pygame.mixer.music.stop()

# Bucle principal del programa
while True:
    reproducir_video('assets/intro.mp4')
    mostrar_menu()
    juego()
