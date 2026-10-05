import os
import random
import sys
import neat
import pygame

pygame.init()

# Config da tela
LARGURA_TELA = 400
ALTURA_TELA = 600

tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Flappy Bird - NEAT AI")

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
ESPACO_ENTRE_CANOS = 140
VELOCIDADE_CANO = 5 # Padrão é 3
FREQUENCIA_CANO = 1000  # Em ms
ultimo_cano = pygame.time.get_ticks()
canos = []

imagem_passaro = pygame.image.load("passaro.png").convert_alpha()
imagem_passaro = pygame.transform.scale(
    imagem_passaro, (TAMANHO_PASSARO, TAMANHO_PASSARO)
)

font = pygame.font.SysFont("Arial", 22, bold=True)
geracao = 0


class Passaro:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade_y = 0

    def pular(self):
        self.velocidade_y = FORCA_PULO

    def mover(self):
        self.velocidade_y += GRAVIDADE
        self.y += self.velocidade_y

    def get_rect(self):
        return pygame.Rect(self.x, self.y, TAMANHO_PASSARO, TAMANHO_PASSARO)

    def desenhar(self, win):
        win.blit(imagem_passaro, (self.x, self.y))


def criar_cano():
    altura_espaco = random.randint(100, ALTURA_TELA - ESPACO_ENTRE_CANOS - 100)
    cano_topo = pygame.Rect(LARGURA_TELA, 0, LARGURA_CANO, altura_espaco)
    cano_base = pygame.Rect(
        LARGURA_TELA,
        altura_espaco + ESPACO_ENTRE_CANOS,
        LARGURA_CANO,
        ALTURA_TELA - (altura_espaco + ESPACO_ENTRE_CANOS),
    )
    return cano_topo, cano_base


def eval_genomes(genomes, config):
    global geracao
    geracao += 1

    redes = []
    ge = []
    passaros = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        redes.append(net)
        passaros.append(Passaro(45, ALTURA_TELA // 2))
        ge.append(genome)

    canos = []
    cano_topo, cano_base = criar_cano()
    canos.extend([cano_topo, cano_base])
    ultimo_cano = pygame.time.get_ticks()

    pontos = 0
    rodando = True

    while rodando and len(passaros) > 0:
        relogio.tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Define o próximo cano a frente
        indice_cano = 0
        if len(canos) > 0:
            if passaros[0].x > canos[0].right and len(canos) > 2:
                indice_cano = 2

        # Atualiza a física e passa as entradas para a rede neural
        for i, passaro in enumerate(passaros):
            ge[i].fitness += 0.1
            passaro.mover()

            cano_topo_rect = canos[indice_cano]
            cano_base_rect = canos[indice_cano + 1]

            # Entradas da rede: Posição Y, distancia até o topo e distancia até a base
            output = redes[i].activate(
                (
                    passaro.y,
                    abs(passaro.y - cano_topo_rect.height),
                    abs(passaro.y - cano_base_rect.top),
                )
            )

            # Faz ele pular se a saída for maior que 0.5. Como se fosse um sensor
            if output[0] > 0.5:
                passaro.pular()

        # Geração de canos e remoção dos que já saíram da tela
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - ultimo_cano > FREQUENCIA_CANO:
            novos_top, novos_base = criar_cano()
            canos.extend([novos_top, novos_base])
            ultimo_cano = tempo_atual

        for cano in canos:
            cano.x -= VELOCIDADE_CANO

        if len(canos) > 0 and canos[0].right < 0:
            canos.pop(0)
            canos.pop(0)
            pontos += 1

            # Recompensa para a rede
            for g in ge:
                g.fitness += 5

        # Colisões
        for i in range(len(passaros) - 1, -1, -1):
            passaro = passaros[i]
            p_rect = passaro.get_rect()

            colidiu = False
            if p_rect.top <= 0 or p_rect.bottom >= ALTURA_TELA:
                colidiu = True

            for cano in canos:
                if p_rect.colliderect(cano):
                    colidiu = True
                    break

            if colidiu:
                ge[i].fitness -= 1  # Penalidade
                passaros.pop(i)
                redes.pop(i)
                ge.pop(i)

        tela.fill(AZUL_CEU)

        for cano in canos:
            pygame.draw.rect(tela, VERDE_CANO, cano)

        for passaro in passaros:
            passaro.desenhar(tela)

        txt_pontos = font.render(f"Pontos: {pontos}", True, BRANCO)
        txt_geracao = font.render(f"Geração: {geracao}", True, BRANCO)
        txt_vivos = font.render(f"Vivos: {len(passaros)}", True, BRANCO)

        tela.blit(txt_pontos, (10, 10))
        tela.blit(txt_geracao, (10, 40))
        tela.blit(txt_vivos, (10, 70))

        pygame.display.update()


def run(caminho_config):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction, 
        neat.DefaultSpeciesSet,  
        neat.DefaultStagnation,  
        caminho_config,
    )
   
    populacao = neat.Population(config)

    populacao.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    populacao.add_reporter(stats)

    # Executa a simulação por 50 gerações
    populacao.run(eval_genomes, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    caminho_config = os.path.join(local_dir, "config-feedforward.txt")
    run(caminho_config)