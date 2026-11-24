# ==============================================================================
# CENÁRIO: LAYOUT DA VILA, DESENHO DOS OBJETOS, PESSOAS E CICLO DIA/NOITE
#
# Regra de ouro: cada objeto clicável tem UMA área definida em HOTSPOTS, e o
# desenho usa essas mesmas coordenadas. Pessoas ficam de pé no chão (x, y do pé),
# sempre em áreas livres, com sombra.
#
# Zonas (vista 3/4 frontal):
#   y   0-62   HUD
#   y  62-215  céu e morros
#   y 150-262  fileira institucional (Prefeitura, Posto, Escola, Associação) e fábrica
#   y 262-274  calçada norte | y 274-326 rua principal | y 326-340 calçada sul
#   y 330-420  fileira comunitária (casas, Mercadinho, Bar, praça)
#   y 420-720  margens e Rio das Pedras (diagonal da fábrica até o canto inferior)
# ==============================================================================
import math

import pygame

from . import config as C
from .graficos import FontManager, UIUtils, alpha_circle, alpha_ellipse, alpha_polygon, alpha_rect
from .modelos import DIA, NOITE, NPC

R = pygame.Rect

# ------------------------------------------------------------------------------
# ÁREAS CLICÁVEIS DOS OBJETOS FIXOS
# ------------------------------------------------------------------------------
HOTSPOTS = {
    # fileira institucional
    "prefeitura": R(30, 120, 180, 142),
    "aviso_posto": R(296, 218, 40, 32),
    "mural_escola": R(462, 216, 46, 40),
    "mural_festa": R(622, 216, 50, 40),
    "outdoor": R(690, 144, 100, 62),
    # fábrica
    "escritorio": R(805, 160, 82, 92),
    "galpao": R(975, 150, 160, 68),
    "quadro_empregos": R(962, 222, 44, 40),
    "caminhao": R(1060, 278, 150, 46),
    # entre a rua e o rio (lado da fábrica)
    "placa_transito": R(846, 290, 24, 58),
    "ferramentas": R(896, 356, 36, 20),
    "tambores": R(1116, 362, 78, 32),
    "tubulacao": R(935, 420, 56, 50),
    # fileira comunitária e praça
    "caixas": R(96, 410, 36, 32),
    "lixeira": R(220, 396, 22, 28),
    "foto_bar": R(258, 378, 30, 28),
    "bicicleta": R(372, 398, 36, 26),
    "flor": R(412, 376, 22, 26),
    "cachorro": R(466, 436, 40, 20),
    "arvore": R(518, 296, 78, 126),
    "pedra": R(600, 416, 32, 26),
    "banco": R(636, 412, 46, 22),
    "poste": R(684, 344, 16, 86),
    "orelhao": R(702, 386, 30, 44),
    # margem esquerda do rio
    "campo": R(560, 462, 140, 80),
    "horta": R(26, 600, 148, 94),
    "carrinho": R(180, 664, 50, 28),
    "placa_rio": R(446, 664, 54, 44),
    "barco": R(516, 648, 88, 40),
    # margem direita
    "placa_app": R(1040, 596, 52, 56),
}

# Rio das Pedras: borda de cima (da direita para a esquerda) + borda de baixo
RIO_TOPO = [(1280, 400), (1100, 440), (950, 470), (800, 520), (680, 575), (580, 640), (520, 720)]
RIO_BASE = [(800, 720), (900, 650), (1020, 590), (1150, 550), (1280, 525)]
RIO = RIO_TOPO + RIO_BASE

# Retângulos de prédios (para verificação: pessoas não podem ter o pé dentro deles)
PREDIOS = {
    "prefeitura": R(30, 172, 180, 90), "posto": R(235, 192, 110, 70), "escola": R(370, 182, 140, 80),
    "associacao": R(535, 192, 140, 70), "escritorio": R(805, 160, 82, 90), "galpao": R(975, 150, 160, 100),
    "casa_a": R(10, 365, 72, 55), "mercadinho": R(95, 350, 120, 70), "bar": R(250, 355, 120, 65),
    "casa_b": R(410, 365, 72, 55), "casa_francisca": R(290, 505, 80, 55),
}

def janelas_casa(r):
    """Janelas das casinhas: uma em cada lateral, sem encostar na porta central."""
    return [R(r.x + 7, r.y + 15, 14, 14), R(r.right - 21, r.y + 15, 14, 14)]


def porta_casa(r):
    return R(r.centerx - 9, r.bottom - 32, 18, 32)


CASA_A = R(10, 365, 72, 55)
CASA_B = R(410, 365, 72, 55)


# Janelas que acendem à noite
JANELAS = [
    # (Prefeitura e Escola ficam fechadas e apagadas à noite)
    R(818, 172, 16, 12), R(842, 172, 16, 12), R(866, 172, 12, 12),
    R(818, 196, 16, 12), R(842, 196, 16, 12), R(866, 196, 12, 12),   # escritório
    *janelas_casa(CASA_A), *janelas_casa(CASA_B),                # casinhas
    R(336, 386, 16, 12),                                         # bar (vidro da porta)
    R(305, 520, 16, 14),                                         # casa de Dona Francisca
]
JANELAS_FABRICA = [R(985 + i * 30, 192, 20, 14) for i in range(5)]


def ponto_no_rio(x, y):
    """Teste ponto-em-polígono (usado na verificação e nas manchas d'água)."""
    dentro = False
    n = len(RIO)
    j = n - 1
    for i in range(n):
        xi, yi = RIO[i]
        xj, yj = RIO[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
            dentro = not dentro
        j = i
    return dentro


def rect_npc(x, base, escala=1.0):
    w, h = int(24 * escala), int(46 * escala)
    return R(x - w // 2, base - h, w, h)


# ------------------------------------------------------------------------------
# PESSOAS
# ------------------------------------------------------------------------------
def desenhar_pessoa(surf, x, base, npc: NPC, t=0.0, escala=1.0, sombra=True):
    """Desenha uma pessoa com o pé em (x, base). Escala 1 = ~44 px de altura."""
    s = escala
    resp = math.sin(t * 2.2 + x * 0.05) * 1.0 * s   # respiração
    if sombra:
        alpha_ellipse(surf, (0, 0, 0, 90), (x - 12 * s, base - 4 * s, 24 * s, 8 * s))
    # pernas
    if npc.saia:
        pygame.draw.rect(surf, npc.pele, (x - 5 * s, base - 9 * s, 3 * s, 9 * s))
        pygame.draw.rect(surf, npc.pele, (x + 2 * s, base - 9 * s, 3 * s, 9 * s))
        pygame.draw.polygon(surf, npc.calca, [(x - 8 * s, base - 8 * s), (x + 8 * s, base - 8 * s),
                                              (x + 6 * s, base - 22 * s), (x - 6 * s, base - 22 * s)])
    else:
        pygame.draw.rect(surf, npc.calca, (x - 6 * s, base - 18 * s, 5 * s, 18 * s))
        pygame.draw.rect(surf, npc.calca, (x + 1 * s, base - 18 * s, 5 * s, 18 * s))
    # sapatos
    pygame.draw.rect(surf, (35, 30, 28), (x - 7 * s, base - 3 * s, 6 * s, 3 * s))
    pygame.draw.rect(surf, (35, 30, 28), (x + 1 * s, base - 3 * s, 6 * s, 3 * s))
    # tronco e braços
    topo = base - 34 * s + resp
    pygame.draw.rect(surf, npc.camisa, (x - 7 * s, topo, 14 * s, 17 * s), border_radius=int(3 * s))
    pygame.draw.rect(surf, npc.camisa, (x - 10 * s, topo + 1 * s, 4 * s, 11 * s), border_radius=int(2 * s))
    pygame.draw.rect(surf, npc.camisa, (x + 6 * s, topo + 1 * s, 4 * s, 11 * s), border_radius=int(2 * s))
    pygame.draw.circle(surf, npc.pele, (x - 8 * s, topo + 13 * s), 2 * s)
    pygame.draw.circle(surf, npc.pele, (x + 8 * s, topo + 13 * s), 2 * s)
    # pescoço e cabeça
    pygame.draw.rect(surf, npc.pele, (x - 2 * s, topo - 3 * s, 4 * s, 4 * s))
    cy = topo - 8 * s
    pygame.draw.circle(surf, npc.pele, (x, cy), 6 * s)
    pygame.draw.arc(surf, npc.cabelo, (x - 7 * s, cy - 7 * s, 14 * s, 12 * s), 0.2, math.pi - 0.2, max(1, int(3 * s)))
    if npc.saia:  # cabelo preso
        pygame.draw.circle(surf, npc.cabelo, (x + 5 * s, cy - 3 * s), 3 * s)
    if npc.chapeu:
        pygame.draw.ellipse(surf, npc.chapeu, (x - 8 * s, cy - 9 * s, 16 * s, 8 * s))
        pygame.draw.rect(surf, npc.chapeu, (x - 9 * s, cy - 5 * s, 18 * s, 2 * s))
    # olhos
    pygame.draw.circle(surf, (30, 25, 25), (x - 2 * s, cy), max(1, s))
    pygame.draw.circle(surf, (30, 25, 25), (x + 2 * s, cy), max(1, s))


def retrato(npc: NPC, tamanho=(150, 180)):
    """Retrato ampliado de um personagem, para as janelas de conversa."""
    base = pygame.Surface((50, 60), pygame.SRCALPHA)
    desenhar_pessoa(base, 25, 58, npc, t=0, escala=1.2, sombra=False)
    return pygame.transform.scale(base, tamanho)


# ------------------------------------------------------------------------------
# RENDERIZADOR
# ------------------------------------------------------------------------------
class ScenarioRenderer:
    def __init__(self):
        self.bg_surf = pygame.Surface((C.VIRTUAL_WIDTH, C.VIRTUAL_HEIGHT))
        self._desenhar_fundo(self.bg_surf)
        self.noite_overlay = pygame.Surface((C.VIRTUAL_WIDTH, C.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        self.noite_overlay.fill((8, 14, 40, 165))
        self.estrelas = [((i * 97) % C.VIRTUAL_WIDTH, 66 + (i * 53) % 52, 1 + (i % 3 == 0)) for i in range(60)]

    # ============================================================ fundo estático
    def _desenhar_fundo(self, s):
        # céu e morros
        s.fill((120, 170, 205))
        for i in range(8):
            pygame.draw.rect(s, (130 + i * 6, 180 + i * 4, 210), (0, 62 + i * 18, C.VIRTUAL_WIDTH, 18))
        pygame.draw.polygon(s, (95, 135, 110), [(0, 175), (180, 140), (380, 170), (600, 128), (820, 165),
                                                (1050, 120), (1280, 150), (1280, 230), (0, 230)])
        pygame.draw.polygon(s, (80, 120, 90), [(0, 200), (250, 175), (520, 195), (760, 170), (1000, 190),
                                               (1280, 175), (1280, 240), (0, 240)])
        # chão
        pygame.draw.rect(s, (98, 140, 72), (0, 215, C.VIRTUAL_WIDTH, C.VIRTUAL_HEIGHT - 215))
        for i in range(140):   # textura de grama
            gx, gy = (i * 89) % 1280, 430 + (i * 41) % 290
            pygame.draw.line(s, (80, 120, 60), (gx, gy), (gx + 2, gy - 4), 1)

        # árvores do fundo (atrás dos prédios)
        for tx, ty in [(222, 196), (355, 186), (520, 200), (940, 140), (1250, 140)]:
            self._arvore(s, tx, ty, 0.8)

        # calçadas e rua principal
        pygame.draw.rect(s, (175, 170, 160), (0, 262, C.VIRTUAL_WIDTH, 12))
        pygame.draw.rect(s, (70, 72, 78), (0, 274, C.VIRTUAL_WIDTH, 52))
        for x in range(10, C.VIRTUAL_WIDTH, 60):
            pygame.draw.rect(s, (220, 210, 120), (x, 298, 30, 4))
        pygame.draw.rect(s, (175, 170, 160), (0, 326, C.VIRTUAL_WIDTH, 12))
        # trilha de terra até o rio
        pygame.draw.polygon(s, (160, 135, 95), [(380, 338), (420, 338), (470, 560), (430, 560)])
        # margem degradada (terra) ao redor do rio
        margem = [(1280, 380), (1100, 420), (950, 448), (800, 498), (660, 556), (556, 630), (490, 720),
                  (840, 720), (930, 664), (1040, 608), (1160, 572), (1280, 548)]
        pygame.draw.polygon(s, (130, 112, 80), margem)
        # rio
        pygame.draw.polygon(s, (60, 92, 88), RIO)
        pygame.draw.lines(s, (90, 80, 60), False, RIO_TOPO, 3)
        pygame.draw.lines(s, (90, 80, 60), False, RIO_BASE, 3)

        # fileira institucional (base y=262)
        self._prefeitura(s)
        self._posto(s)
        self._escola(s)
        self._associacao(s)
        self._outdoor(s)
        self._fabrica(s)

        # fileira comunitária (base y=420)
        self._casa(s, CASA_A, (190, 150, 110), (150, 60, 45))
        self._mercadinho(s)
        self._bar(s)
        self._casa(s, CASA_B, (200, 180, 130), (140, 70, 50))
        jan = janelas_casa(CASA_B)[0]                                # vaso da flor (cur7) no peitoril
        vaso_x, vaso_y = jan.centerx, jan.bottom
        pygame.draw.rect(s, (150, 80, 60), (vaso_x - 8, vaso_y, 16, 6))
        pygame.draw.line(s, (60, 130, 60), (vaso_x, vaso_y), (vaso_x, vaso_y - 6), 2)
        for dx, dy in [(-4, -7), (0, -10), (4, -7)]:
            pygame.draw.circle(s, (240, 110, 70), (vaso_x + dx, vaso_y + dy), 3)

        # entre a rua e o rio, lado da fábrica
        self._ponto_onibus(s)
        self._placa_transito(s)
        self._bueiro_e_ferramentas(s)
        self._tambores(s)
        self._saida_tubulacao(s)

        # praça (ordenado por base y)
        self._arvore_centenaria(s)
        self._lixeira(s)
        self._caixas(s)
        self._bicicleta(s)
        self._poste(s)
        self._orelhao(s)
        self._banco(s)
        self._pedra(s)
        self._cachorro(s)
        self._mesa_bar(s)

        # margem esquerda
        self._arvore(s, 60, 540, 1.0)
        self._arvore(s, 230, 590, 0.9)
        self._campo(s)
        self._casa_francisca(s)
        self._rede(s)
        self._horta(s)
        self._carrinho(s)
        self._placa_rio(s)
        self._barco(s)

        # margem direita (APP degradada)
        self._app(s)
        self._arvore(s, 880, 712, 0.9)
        self._arvore(s, 1230, 700, 1.0)

    # ---------------------------------------------------------- peças do fundo
    def _arvore(self, s, x, base, k=1.0):
        pygame.draw.rect(s, (90, 60, 35), (x - 4 * k, base - 30 * k, 8 * k, 30 * k))
        pygame.draw.circle(s, (45, 100, 55), (x, base - 40 * k), 22 * k)
        pygame.draw.circle(s, (60, 120, 65), (x - 10 * k, base - 46 * k), 16 * k)
        pygame.draw.circle(s, (38, 88, 48), (x + 11 * k, base - 36 * k), 15 * k)

    def _placa_texto(self, s, rect, texto, fundo, cor, tam):
        pygame.draw.rect(s, fundo, rect, border_radius=3)
        f = FontManager.get(tam, True)
        ts = f.render(texto, True, cor)
        s.blit(ts, ts.get_rect(center=R(rect).center))

    def _prefeitura(self, s):
        pygame.draw.rect(s, (200, 200, 192), (30, 172, 180, 90))
        pygame.draw.polygon(s, (120, 130, 140), [(20, 172), (120, 128), (220, 172)])
        pygame.draw.polygon(s, (150, 158, 165), [(36, 168), (120, 134), (204, 168)])
        self._placa_texto(s, R(75, 150, 90, 16), "PREFEITURA", (60, 70, 80), (240, 240, 240), 10)
        for cx in range(40, 205, 28):
            pygame.draw.rect(s, (230, 230, 225), (cx, 176, 10, 86))
        pygame.draw.rect(s, (90, 60, 40), (104, 214, 32, 48))           # porta
        pygame.draw.rect(s, (110, 150, 180), (48, 200, 18, 22))
        pygame.draw.rect(s, (110, 150, 180), (174, 200, 18, 22))
        pygame.draw.rect(s, (160, 160, 155), (24, 258, 192, 6))         # degrau
        pygame.draw.line(s, (210, 210, 210), (120, 128), (120, 92), 2)  # mastro
        pygame.draw.rect(s, (40, 140, 70), (121, 94, 22, 13))

    def _posto(self, s):
        pygame.draw.rect(s, (235, 242, 246), (235, 192, 110, 70))
        pygame.draw.rect(s, (110, 120, 130), (230, 186, 120, 8))
        self._placa_texto(s, R(244, 197, 92, 15), "POSTO DE SAÚDE", (40, 100, 180), (255, 255, 255), 9)
        pygame.draw.rect(s, (205, 215, 225), (250, 222, 26, 40))        # porta
        pygame.draw.rect(s, (255, 250, 200), (300, 222, 32, 24))        # aviso (sec3)
        for i in range(4):
            pygame.draw.line(s, (120, 110, 90), (304, 227 + i * 5), (328, 227 + i * 5), 1)
        pygame.draw.rect(s, (200, 50, 50), (283, 226, 10, 4))           # cruz
        pygame.draw.rect(s, (200, 50, 50), (286, 223, 4, 10))

    def _escola(self, s):
        pygame.draw.rect(s, (230, 205, 135), (370, 182, 140, 80))
        pygame.draw.polygon(s, (170, 75, 55), [(362, 182), (376, 166), (504, 166), (518, 182)])
        self._placa_texto(s, R(405, 188, 70, 15), "ESCOLA", (255, 255, 255), (20, 20, 20), 10)
        pygame.draw.rect(s, (110, 160, 205), (380, 210, 22, 20))
        pygame.draw.rect(s, (80, 55, 40), (418, 222, 30, 40))
        pygame.draw.rect(s, (235, 235, 235), (465, 220, 40, 32))        # mural (sec2)
        pygame.draw.rect(s, (120, 90, 60), (465, 220, 40, 32), 2)
        pygame.draw.rect(s, (60, 70, 90), (470, 236, 30, 6))            # rio escuro desenhado
        pygame.draw.circle(s, (230, 120, 60), (476, 228), 3)
        pygame.draw.circle(s, (250, 210, 60), (494, 227), 4)

    def _associacao(self, s):
        pygame.draw.rect(s, (110, 145, 120), (535, 192, 140, 70))
        pygame.draw.polygon(s, (130, 65, 50), [(525, 192), (605, 156), (685, 192)])
        self._placa_texto(s, R(545, 197, 120, 15), "ASSOC. DE MORADORES", (235, 235, 225), (20, 20, 20), 9)
        pygame.draw.rect(s, (85, 55, 40), (560, 222, 28, 40))
        pygame.draw.rect(s, (160, 130, 90), (622, 218, 50, 36))         # cartazes (cur6)
        pygame.draw.rect(s, (230, 200, 60), (626, 222, 13, 17))
        pygame.draw.rect(s, (70, 160, 210), (642, 222, 12, 14))
        pygame.draw.rect(s, (220, 100, 90), (657, 224, 12, 16))
        pygame.draw.rect(s, (240, 240, 230), (634, 241, 22, 10))

    def _outdoor(self, s):
        pygame.draw.rect(s, (80, 80, 85), (708, 200, 5, 66))
        pygame.draw.rect(s, (80, 80, 85), (768, 200, 5, 66))
        pygame.draw.rect(s, (30, 100, 60), (690, 146, 100, 56), border_radius=3)
        pygame.draw.rect(s, (240, 240, 230), (690, 146, 100, 56), 2, border_radius=3)
        s.blit(FontManager.get(9, True).render("VALE DAS PEDRAS", True, (255, 220, 80)), (696, 152))
        s.blit(FontManager.get(9).render("O motor do", True, (255, 255, 255)), (697, 168))
        s.blit(FontManager.get(9).render("desenvolvimento!", True, (255, 255, 255)), (697, 180))
        pygame.draw.circle(s, (120, 200, 120), (775, 186), 8)

    def _fabrica(self, s):
        # pátio
        pygame.draw.rect(s, (120, 120, 118), (800, 150, 480, 112))
        # chaminés (origem da fumaça)
        for cx in (1152, 1188):
            pygame.draw.rect(s, (150, 90, 80), (cx, 84, 22, 170))
            for k in range(4):
                pygame.draw.rect(s, (230, 230, 230), (cx, 96 + k * 36, 22, 8))
            pygame.draw.rect(s, (90, 60, 55), (cx - 2, 82, 26, 6))
        # galpão principal
        pygame.draw.rect(s, (95, 105, 118), (975, 150, 160, 100))
        pygame.draw.polygon(s, (75, 85, 98), [(968, 150), (1055, 112), (1142, 150)])
        self._placa_texto(s, R(990, 160, 130, 18), "VALE DAS PEDRAS S.A.", (30, 40, 50), C.COLOR_ACCENT_GOLD, 10)
        for j in JANELAS_FABRICA:
            pygame.draw.rect(s, (60, 70, 80), j)
        pygame.draw.rect(s, (60, 65, 72), (1030, 210, 50, 40))           # portão do galpão
        # escritório (ev1)
        pygame.draw.rect(s, (175, 180, 190), (805, 160, 82, 90))
        pygame.draw.rect(s, (130, 135, 145), (801, 154, 90, 8))
        for row in (172, 196):
            for col in (818, 842, 866):
                pygame.draw.rect(s, (90, 120, 150), (col, row, 16 if col < 866 else 12, 12))
        self._placa_texto(s, R(810, 217, 72, 12), "ADMINISTRAÇÃO", (50, 60, 70), (230, 230, 230), 7)
        pygame.draw.rect(s, (70, 60, 55), (834, 232, 22, 18))
        # tanques
        for tx in (1220, 1250):
            pygame.draw.rect(s, (200, 205, 210), (tx - 2, 172, 28, 80), border_radius=12)
            pygame.draw.rect(s, (160, 165, 170), (tx - 2, 200, 28, 4))
        # estação de tratamento (desligada)
        pygame.draw.rect(s, (110, 130, 120), (900, 214, 54, 36))
        pygame.draw.rect(s, (80, 100, 90), (906, 220, 42, 6))
        # cerca com portão aberto (x 900-960)
        for x in range(800, C.VIRTUAL_WIDTH, 10):
            if 900 <= x < 960:
                continue
            pygame.draw.line(s, (150, 150, 155), (x, 238), (x, 262), 1)
        pygame.draw.line(s, (150, 150, 155), (800, 240), (900, 240), 2)
        pygame.draw.line(s, (150, 150, 155), (960, 240), (1280, 240), 2)
        pygame.draw.rect(s, (90, 90, 95), (896, 232, 6, 32))
        pygame.draw.rect(s, (90, 90, 95), (958, 232, 6, 32))
        # quadro de empregos (sec8), preso na cerca
        pygame.draw.rect(s, (110, 85, 60), (964, 224, 40, 32))
        for i, (bx, by) in enumerate([(968, 228), (980, 228), (992, 228), (972, 241), (986, 241)]):
            pygame.draw.rect(s, (250, 250, 240), (bx, by, 9, 10))
        pygame.draw.rect(s, (90, 90, 95), (982, 256, 4, 8))

    def _casa(self, s, r, parede, telhado):
        pygame.draw.rect(s, parede, r)
        pygame.draw.polygon(s, telhado, [(r.x - 8, r.y), (r.centerx, r.y - 30), (r.right + 8, r.y)])
        pygame.draw.rect(s, (80, 55, 40), porta_casa(r))
        pygame.draw.circle(s, (200, 170, 80), (porta_casa(r).right - 4, porta_casa(r).centery), 2)
        for j in janelas_casa(r):
            pygame.draw.rect(s, (110, 150, 180), j)
            pygame.draw.rect(s, (235, 225, 205), j, 1)

    def _mercadinho(self, s):
        pygame.draw.rect(s, (150, 190, 160), (95, 350, 120, 70))
        for i in range(12):
            pygame.draw.rect(s, (200, 55, 55) if i % 2 == 0 else (245, 245, 245), (95 + i * 10, 350, 10, 16))
        self._placa_texto(s, R(110, 332, 90, 16), "MERCADINHO", (255, 255, 255), (20, 20, 20), 10)
        pygame.draw.rect(s, (110, 160, 205), (104, 374, 34, 28))
        pygame.draw.rect(s, (70, 55, 40), (178, 378, 26, 42))

    def _bar(self, s):
        pygame.draw.rect(s, (190, 155, 105), (250, 355, 120, 65))
        pygame.draw.polygon(s, (110, 55, 40), [(242, 355), (310, 328), (378, 355)])
        self._placa_texto(s, R(290, 360, 40, 16), "BAR", (30, 30, 30), (255, 230, 60), 11)
        pygame.draw.rect(s, (70, 40, 25), (332, 380, 24, 40))
        pygame.draw.rect(s, (230, 225, 210), (260, 380, 26, 24))          # moldura (cur8)
        pygame.draw.rect(s, (120, 120, 120), (263, 383, 20, 18))
        for k in range(4):
            pygame.draw.circle(s, (60, 60, 60), (266 + k * 5, 393), 2)

    def _mesa_bar(self, s):
        pygame.draw.rect(s, (120, 80, 50), (322, 424, 28, 5))
        pygame.draw.rect(s, (100, 65, 40), (334, 429, 4, 10))
        pygame.draw.rect(s, (230, 200, 70), (328, 418, 4, 6))

    def _ponto_onibus(self, s):
        pygame.draw.rect(s, (120, 125, 135), (766, 300, 4, 46))
        pygame.draw.rect(s, (120, 125, 135), (834, 300, 4, 46))
        pygame.draw.rect(s, (90, 95, 105), (760, 294, 84, 8))
        alpha_rect(s, (180, 210, 230, 120), (770, 302, 64, 30))
        pygame.draw.rect(s, (160, 110, 70), (774, 330, 56, 5))
        pygame.draw.rect(s, (40, 120, 220), (836, 304, 12, 12))

    def _placa_transito(self, s):
        pygame.draw.rect(s, (110, 110, 110), (856, 302, 4, 44))
        pygame.draw.circle(s, (200, 40, 40), (858, 300), 10)
        pygame.draw.circle(s, (255, 255, 255), (858, 300), 7)
        s.blit(FontManager.get(8, True).render("40", True, (0, 0, 0)), (852, 295))

    def _bueiro_e_ferramentas(self, s):
        pygame.draw.ellipse(s, (60, 60, 60), (992, 350, 26, 10))
        pygame.draw.ellipse(s, (90, 90, 90), (992, 350, 26, 10), 2)
        pygame.draw.rect(s, (200, 45, 45), (898, 362, 30, 12), border_radius=2)
        pygame.draw.line(s, (50, 50, 50), (906, 358), (920, 358), 2)
        pygame.draw.line(s, (50, 50, 50), (906, 358), (906, 362), 2)
        pygame.draw.line(s, (50, 50, 50), (920, 358), (920, 362), 2)

    def _tambores(self, s):
        for dx in (1120, 1145, 1170):
            pygame.draw.rect(s, (40, 80, 150), (dx, 368, 20, 24), border_radius=2)
            pygame.draw.line(s, (220, 200, 50), (dx, 374), (dx + 20, 374), 2)
            pygame.draw.line(s, (220, 200, 50), (dx, 384), (dx + 20, 384), 2)
        pygame.draw.ellipse(s, (50, 60, 45), (1150, 390, 40, 8))         # vazamento

    def _saida_tubulacao(self, s):
        pygame.draw.rect(s, (150, 150, 145), (940, 430, 46, 30))
        pygame.draw.rect(s, (120, 120, 115), (940, 430, 46, 30), 2)
        pygame.draw.circle(s, (40, 40, 40), (963, 452), 9)
        pygame.draw.circle(s, (90, 90, 90), (963, 452), 9, 2)
        pygame.draw.ellipse(s, (45, 55, 45), (948, 462, 32, 8))          # mancha escura
        for gx in (932, 990):
            pygame.draw.line(s, (70, 120, 60), (gx, 460), (gx + 4, 440), 2)

    def _arvore_centenaria(self, s):
        pygame.draw.rect(s, (85, 55, 30), (545, 350, 22, 72))
        pygame.draw.polygon(s, (85, 55, 30), [(545, 422), (528, 426), (545, 410)])
        pygame.draw.polygon(s, (85, 55, 30), [(567, 422), (586, 426), (567, 410)])
        pygame.draw.circle(s, (40, 95, 50), (556, 336), 44)
        pygame.draw.circle(s, (55, 115, 60), (530, 352), 32)
        pygame.draw.circle(s, (35, 85, 45), (584, 352), 32)
        pygame.draw.circle(s, (60, 125, 65), (556, 312), 26)

    def _lixeira(self, s):
        pygame.draw.rect(s, (90, 100, 95), (223, 404, 16, 20), border_radius=2)
        pygame.draw.rect(s, (70, 80, 75), (221, 400, 20, 5))
        pygame.draw.circle(s, (200, 60, 60), (227, 398), 3)
        pygame.draw.circle(s, (60, 180, 60), (235, 397), 3)

    def _caixas(self, s):
        pygame.draw.rect(s, (165, 115, 70), (98, 424, 22, 18))
        pygame.draw.rect(s, (185, 135, 85), (108, 410, 22, 16))
        pygame.draw.rect(s, (120, 80, 50), (98, 424, 22, 18), 1)
        pygame.draw.rect(s, (120, 80, 50), (108, 410, 22, 16), 1)

    def _bicicleta(self, s):
        pygame.draw.circle(s, (40, 40, 40), (380, 416), 7, 2)
        pygame.draw.circle(s, (40, 40, 40), (400, 416), 7, 2)
        pygame.draw.polygon(s, (200, 50, 50), [(380, 416), (390, 416), (397, 406), (386, 406)], 2)
        pygame.draw.line(s, (200, 200, 200), (397, 406), (399, 400), 2)
        pygame.draw.line(s, (40, 40, 40), (384, 404), (388, 404), 3)

    def _poste(self, s):
        pygame.draw.rect(s, (80, 80, 85), (690, 346, 4, 82))
        pygame.draw.line(s, (80, 80, 85), (692, 348), (674, 350), 3)
        pygame.draw.circle(s, (150, 150, 140), (673, 352), 4)            # lâmpada queimada
        pygame.draw.line(s, (40, 40, 40), (692, 360), (740, 340), 1)     # fios
        pygame.draw.line(s, (40, 40, 40), (692, 362), (640, 344), 1)

    def _orelhao(self, s):
        pygame.draw.rect(s, (110, 110, 110), (716, 400, 4, 28))
        pygame.draw.ellipse(s, (240, 140, 40), (704, 386, 28, 24))
        pygame.draw.ellipse(s, (60, 60, 60), (710, 394, 16, 14))

    def _banco(self, s):
        pygame.draw.rect(s, (140, 95, 55), (638, 416, 42, 5))
        pygame.draw.rect(s, (140, 95, 55), (638, 424, 42, 5))
        pygame.draw.line(s, (60, 60, 60), (642, 429), (642, 434), 2)
        pygame.draw.line(s, (60, 60, 60), (676, 429), (676, 434), 2)

    def _pedra(self, s):
        pygame.draw.polygon(s, (150, 150, 145), [(602, 442), (606, 424), (616, 418), (628, 424), (630, 442)])
        pygame.draw.rect(s, (190, 150, 60), (609, 428, 14, 8))

    def _cachorro(self, s):
        alpha_ellipse(s, (0, 0, 0, 70), (468, 448, 36, 7))
        pygame.draw.ellipse(s, (210, 150, 60), (470, 440, 26, 12))
        pygame.draw.circle(s, (210, 150, 60), (497, 444), 6)
        pygame.draw.polygon(s, (170, 110, 40), [(495, 438), (499, 434), (501, 440)])
        pygame.draw.line(s, (30, 30, 30), (497, 444), (500, 444), 1)
        pygame.draw.line(s, (210, 150, 60), (470, 444), (464, 440), 3)

    def _campo(self, s):
        pygame.draw.ellipse(s, (170, 150, 105), (560, 470, 140, 70))
        pygame.draw.line(s, (235, 235, 235), (612, 512), (612, 482), 3)
        pygame.draw.line(s, (235, 235, 235), (648, 512), (648, 482), 3)
        pygame.draw.line(s, (235, 235, 235), (610, 482), (650, 482), 3)
        pygame.draw.line(s, (200, 200, 200), (612, 482), (618, 488), 1)
        pygame.draw.line(s, (200, 200, 200), (648, 482), (642, 488), 1)

    def _casa_francisca(self, s):
        # casa de madeira sobre palafitas
        for px in (296, 330, 362):
            pygame.draw.rect(s, (80, 55, 35), (px, 556, 5, 10))
        pygame.draw.rect(s, (150, 110, 75), (290, 505, 80, 52))
        for yy in range(510, 556, 8):
            pygame.draw.line(s, (125, 90, 60), (290, yy), (370, yy), 1)
        pygame.draw.polygon(s, (120, 90, 70), [(282, 505), (330, 478), (378, 505)])
        pygame.draw.rect(s, (110, 150, 180), (305, 520, 16, 14))
        pygame.draw.rect(s, (80, 55, 40), (340, 525, 18, 32))

    def _rede(self, s):
        pygame.draw.line(s, (90, 65, 40), (384, 600), (384, 566), 3)
        pygame.draw.line(s, (90, 65, 40), (428, 600), (428, 566), 3)
        for k in range(5):
            pygame.draw.line(s, (200, 200, 190), (384, 570 + k * 5), (428, 572 + k * 5), 1)
        for k in range(6):
            pygame.draw.line(s, (200, 200, 190), (388 + k * 8, 568), (386 + k * 8, 594), 1)

    def _horta(self, s):
        for row in range(3):
            y = 610 + row * 28
            pygame.draw.rect(s, (95, 65, 40), (30, y, 140, 20), border_radius=3)
            for px in range(40, 165, 16):
                cor = (190, 200, 80) if row == 1 else (90, 170, 75)   # fileira amarelada
                pygame.draw.circle(s, cor, (px, y + 8), 6)
        pygame.draw.rect(s, (160, 130, 90), (150, 596, 22, 12))           # plaquinha
        pygame.draw.line(s, (110, 80, 50), (161, 608), (161, 616), 2)

    def _carrinho(self, s):
        pygame.draw.polygon(s, (60, 150, 90), [(186, 672), (214, 672), (220, 684), (192, 684)])
        pygame.draw.circle(s, (30, 30, 30), (222, 688), 5)
        pygame.draw.line(s, (150, 150, 150), (182, 668), (196, 676), 2)

    def _placa_rio(self, s):
        pygame.draw.rect(s, (110, 75, 45), (471, 684, 5, 22))
        pygame.draw.rect(s, (150, 115, 70), (448, 666, 50, 20), border_radius=2)
        s.blit(FontManager.get(8, True).render("RIO DAS", True, (40, 30, 20)), (455, 667))
        s.blit(FontManager.get(8, True).render("PEDRAS", True, (40, 30, 20)), (457, 676))

    def _barco(self, s):
        pygame.draw.polygon(s, (120, 85, 55), [(518, 660), (602, 656), (592, 682), (530, 686)])
        pygame.draw.polygon(s, (90, 60, 40), [(518, 660), (602, 656), (600, 662), (522, 666)])
        pygame.draw.line(s, (60, 40, 25), (540, 662), (580, 680), 2)       # rachadura
        s.blit(FontManager.get(8, True).render("ESPERANÇA", True, (200, 190, 170)), (536, 670))

    def _app(self, s):
        for tx, ty in [(980, 640), (1010, 672), (1120, 628), (1150, 668), (1190, 612), (1080, 690)]:
            pygame.draw.rect(s, (110, 75, 45), (tx, ty - 8, 12, 8))
            pygame.draw.ellipse(s, (150, 115, 75), (tx, ty - 11, 12, 5))
        for lx, ly, c in [(1000, 610, (220, 220, 220)), (1100, 655, (60, 120, 200)), (1170, 690, (200, 60, 60))]:
            pygame.draw.rect(s, c, (lx, ly, 8, 5))
        pygame.draw.rect(s, (110, 110, 110), (1064, 616, 4, 34))
        pygame.draw.rect(s, (60, 110, 75), (1042, 598, 48, 22), border_radius=2)
        pygame.draw.rect(s, (200, 200, 190), (1044, 600, 44, 18), 1)
        s.blit(FontManager.get(8, True).render("APP", True, (230, 230, 220)), (1056, 603))

    # =========================================================== partes dinâmicas
    def desenhar(self, surf, estado, t):
        """Desenha o cenário completo para o período atual (sem HUD)."""
        noite = estado.periodo == NOITE
        surf.blit(self.bg_surf, (0, 0))
        self._agua(surf, t, noite)
        if noite:
            self._caminhao(surf)
            self._efluente(surf, t)
        self._pessoas(surf, estado, t)
        if noite:
            self._aplicar_noite(surf, t)
        self._fumaca(surf, t, noite)

    def _agua(self, surf, t, noite):
        # reflexos e manchas na água (pontos garantidos dentro do rio)
        for i, (x, y) in enumerate([(1180, 470), (1050, 510), (930, 550), (820, 600), (720, 650), (640, 700)]):
            ox = x + math.cos(t * 0.8 + i) * 10
            oy = y + math.sin(t * 1.3 + i) * 4
            alpha_ellipse(surf, (90, 130, 120, 70), (ox - 30, oy - 6, 60, 12))
            alpha_ellipse(surf, (40, 60, 50, 90), (ox - 10, oy + 8, 30, 6))

    def _efluente(self, surf, t):
        # jato escuro saindo da tubulação e mancha se espalhando no rio
        for k in range(6):
            fase = (t * 1.5 + k / 6) % 1
            alpha_circle(surf, (30, 40, 25, int(200 * (1 - fase))), (963 + math.sin(t * 5 + k) * 3, 456 + fase * 26),
                         4 + fase * 10)
        alpha_ellipse(surf, (25, 35, 25, 150), (900 + math.sin(t) * 6, 476, 150, 40))
        alpha_ellipse(surf, (60, 70, 40, 90), (930, 486 + math.cos(t) * 3, 60, 10))

    def _caminhao(self, surf):
        r = HOTSPOTS["caminhao"]
        pygame.draw.rect(surf, (170, 175, 180), (r.x, r.y + 6, 100, 30), border_radius=12)
        pygame.draw.rect(surf, (60, 60, 70), (r.x + 102, r.y + 10, 42, 26), border_radius=3)
        pygame.draw.rect(surf, (90, 110, 130), (r.x + 120, r.y + 14, 18, 10))
        for wx in (r.x + 18, r.x + 70, r.x + 125):
            pygame.draw.circle(surf, (20, 20, 20), (wx, r.y + 38), 7)

    def _pessoas(self, surf, estado, t):
        from .conteudo import NPCS
        presentes = [n for n in NPCS.values() if estado.npc_presente(n.id)]
        for npc in sorted(presentes, key=lambda n: n.posicoes[estado.periodo][1]):
            x, base = npc.posicoes[estado.periodo]
            desenhar_pessoa(surf, x, base, npc, t)
        if estado.periodo == NOITE:   # figurante no bar à noite
            figurante = NPC("fig", "", "", {}, (90, 120, 160), (50, 50, 60), (180, 130, 95), (40, 30, 25), "")
            desenhar_pessoa(surf, 345, 446, figurante, t)

    def _aplicar_noite(self, surf, t):
        surf.blit(self.noite_overlay, (0, 0))
        for x, y, r in self.estrelas:
            if (x + int(t * 3)) % 7:
                pygame.draw.circle(surf, (230, 230, 255), (x, y), r)
        pygame.draw.circle(surf, (240, 240, 220), (1080, 92), 14)
        pygame.draw.circle(surf, (40, 50, 80), (1087, 88), 12)
        for j in JANELAS:
            alpha_rect(surf, (255, 210, 110, 70), j.inflate(10, 10), radius=4)
            pygame.draw.rect(surf, (255, 220, 130), j)
        for j in JANELAS_FABRICA:
            alpha_rect(surf, (255, 255, 200, 60), j.inflate(12, 12), radius=4)
            pygame.draw.rect(surf, (255, 250, 210), j)
        # holofote da fábrica
        alpha_polygon(surf, (255, 255, 200, 35), [(1135, 150), (1100, 262), (1210, 262)])
        # luz do bar
        alpha_circle(surf, (255, 200, 100, 22), (330, 425), 55)

    def _fumaca(self, surf, t, noite):
        dens = 6 if noite else 4
        for chamine in (1163, 1199):
            for i in range(dens):
                fase = ((t * 0.35) + i / dens + chamine * 0.01) % 1
                x = chamine + math.sin(t * 1.5 + i) * 6 + fase * 40
                y = 80 - fase * 70
                cor = (70, 70, 75) if noite else (150, 150, 155)
                alpha_circle(surf, (*cor, int(170 * (1 - fase))), (x, y), 8 + fase * 18)


def desenhar_rio_final(surf, rect, cor_rio, renderer: ScenarioRenderer, peixes=False, t=0.0):
    """Miniatura do cenário com o rio recolorido conforme o final."""
    mini = pygame.Surface((C.VIRTUAL_WIDTH, C.VIRTUAL_HEIGHT))
    mini.blit(renderer.bg_surf, (0, 0))
    pygame.draw.polygon(mini, cor_rio, RIO)
    if peixes:
        for i, (x, y) in enumerate([(1100, 480), (950, 540), (800, 610), (700, 680)]):
            dx = math.sin(t * 2 + i) * 12
            pygame.draw.ellipse(mini, (230, 160, 70), (x + dx, y, 22, 9))
            pygame.draw.polygon(mini, (230, 160, 70), [(x + dx, y + 4), (x + dx - 8, y - 1), (x + dx - 8, y + 9)])
    surf.blit(pygame.transform.smoothscale(mini, rect.size), rect.topleft)
    pygame.draw.rect(surf, C.COLOR_PANEL_BORDER, rect, 2, border_radius=4)
