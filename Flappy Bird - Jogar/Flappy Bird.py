import pygame
import sys
import random

pygame.init()

# Config da tela
LARGURA_TELA = 400
ALTURA_TELA = 600

tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Flappy Bird")

relogio = pygame.time.Clock()

# Cores
AZUL_CEU = (113, 197, 207)
VERDE_CANO = (115, 191, 46)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

# Configurações do pássaro
TAMANHO_PASSARO = 50
passaro_x = 45
passaro_y = ALTURA_TELA // 2
velocidade_y = 0
GRAVIDADE = 0.5
FORCA_PULO = -8.5

# Configurações dos canos    
LARGURA_CANO = 60
ESPACO_ENTRE_CANOS = 160
VELOCIDADE_CANO = 3
FREQUENCIA_CANO = 1500 # Em ms
ultimo_cano = pygame.time.get_ticks()
canos = []

imagem_passaro = pygame.image.load("passaro.png").convert_alpha()

imagem_passaro = pygame.transform.scale(
    imagem_passaro, (TAMANHO_PASSARO, TAMANHO_PASSARO)
)

# Pontos e estado
pontos = 0
canos_pontuados = [] # Armazena os canos que já somaram ponto
font = pygame.font.SysFont("Arial", 32, bold=True)
game_over = False

def criar_cano():
    altura_espaco = random.randint(100, ALTURA_TELA - ESPACO_ENTRE_CANOS - 100)
    cano_topo = pygame.Rect(LARGURA_TELA, 0, LARGURA_CANO, altura_espaco)
    cano_base = pygame.Rect(
        LARGURA_TELA,
        altura_espaco + ESPACO_ENTRE_CANOS,
        LARGURA_CANO,
        ALTURA_TELA - (altura_espaco + ESPACO_ENTRE_CANOS)
    )
    return cano_topo, cano_base

def mover_canos(lista_canos):
    novos_canos = []
    for cano in lista_canos:
        cano.x -= VELOCIDADE_CANO
        if cano.right > 0:
            novos_canos.append(cano)
    return novos_canos

def checar_colisao(passaro_rect, lista_canos):
    if passaro_rect.top <= 0 or passaro_rect.bottom >= ALTURA_TELA:
        return True

    for cano in lista_canos:
        if passaro_rect.colliderect(cano):
            return True
    return False

# Start do jogo
rodando = True
while rodando:
    relogio.tick(60)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                if not game_over:
                    velocidade_y = FORCA_PULO
                else:
                    passaro_y = ALTURA_TELA // 2
                    velocidade_y = 0
                    canos.clear()
                    canos_pontuados.clear() # Limpa a lista de pontuados
                    pontos = 0
                    game_over = False

    if not game_over:
        # Atualização da física do passarinho
        velocidade_y += GRAVIDADE
        passaro_y += velocidade_y
        passaro_rect = pygame.Rect(
            passaro_x, passaro_y, TAMANHO_PASSARO, TAMANHO_PASSARO
        )

        # Gerenciamento dos canos
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - ultimo_cano > FREQUENCIA_CANO:
            cano_topo, cano_base = criar_cano()
            canos.extend([cano_topo, cano_base])
            ultimo_cano = tempo_atual

        canos = mover_canos(canos)

        # Pontuação corrigida
        for cano in canos:
            if cano.top == 0 and passaro_x > cano.right and cano not in canos_pontuados:
                pontos += 1
                canos_pontuados.append(cano)

        # Verifica a colisão
        if checar_colisao(passaro_rect, canos):
            game_over = True

    tela.fill(AZUL_CEU)

    # Desenhar os canos
    for cano in canos:
        pygame.draw.rect(tela, VERDE_CANO, cano)

    # Desenhar o pássaro
    passaro_rect = pygame.Rect(
        passaro_x, passaro_y, TAMANHO_PASSARO, TAMANHO_PASSARO
    )
    tela.blit(imagem_passaro, passaro_rect)

    # Desenhar pontuação
    texto_pontos = font.render(f"{pontos}", True, BRANCO)
    tela.blit(
        texto_pontos, (LARGURA_TELA // 2 - texto_pontos.get_width() // 2, 30)
    )

    # Mensagem de Game Over
    if game_over:
        texto_game_over = font.render("GAME OVER", True, PRETO)
        texto_reiniciar = font.render("APERTE ESPAÇO", True, PRETO)
        tela.blit(
            texto_game_over,
            (LARGURA_TELA // 2 - texto_game_over.get_width() // 2,
             ALTURA_TELA // 2 - 40)
        )

        tela.blit(
            texto_reiniciar,
            (LARGURA_TELA // 2 - texto_reiniciar.get_width() // 2,
             ALTURA_TELA // 2 + 10)
        )

    pygame.display.update()

pygame.quit()
sys.exit()