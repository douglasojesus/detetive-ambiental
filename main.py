# ==============================================================================
# DETETIVES AMBIENTAIS: POR TRÁS DA DEGRADAÇÃO (VERSÃO CORRIGIDA E APRIMORADA)
# Jogo educativo 2D de investigação socioambiental em Pygame (Single File)
#
# REQUISITOS: Python 3.8+ e Pygame (pip install pygame)
# EXECUÇÃO: python detetives_ambientais.py
# ==============================================================================

import pygame
import sys
import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

# ------------------------------------------------------------------------------
# CONFIGURAÇÕES GERAIS E PALETA DE CORES
# ------------------------------------------------------------------------------
VIRTUAL_WIDTH = 1280
VIRTUAL_HEIGHT = 720
FPS = 60

# Paleta
COLOR_BG_DARK = (16, 22, 28)
COLOR_PANEL_BG = (26, 36, 46)
COLOR_PANEL_ALT = (34, 46, 58)
COLOR_PANEL_BORDER = (55, 78, 98)
COLOR_TEXT_LIGHT = (238, 244, 250)
COLOR_TEXT_MUTED = (160, 180, 200)

COLOR_ACCENT_GOLD = (235, 180, 50)
COLOR_ACCENT_HOVER = (255, 205, 80)
COLOR_ACCENT_CYAN = (60, 185, 205)
COLOR_ACCENT_GREEN = (50, 180, 110)
COLOR_ACCENT_RED = (215, 75, 65)

# ------------------------------------------------------------------------------
# ESTRUTURAS DE DADOS E CONTEÚDO (GAMIFICAÇÃO E NARRATIVA)
# ------------------------------------------------------------------------------
@dataclass
class DialogueOption:
    question: str
    answer: str

@dataclass
class Interactable:
    id: str
    type: str # 'EVIDENCE', 'SECONDARY', 'CURIOSITY', 'FLAVOR'
    name: str
    rect: pygame.Rect
    text: str = ""
    dialogues: List[DialogueOption] = field(default_factory=list)
    inspected: bool = False
    xp_granted: bool = False
    icon: str = "magnifier"

@dataclass
class Achievement:
    id: str
    title: str
    desc: str
    unlocked: bool = False

class Gamification:
    def __init__(self):
        self.xp = 0
        self.level = 1
        self.inspected_count = 0
        self.notifications = []
        
        self.level_thresholds = [0, 150, 350, 600, 1000]
        self.level_names = ["Observador", "Explorador", "Investigador", "Analista", "Detetive Ambiental"]
        
        self.achievements = [
            Achievement("a_first", "Primeiro Contato", "Examine o primeiro objeto do cenário."),
            Achievement("a_10", "Olhar Atento", "Examine 10 objetos interativos."),
            Achievement("a_20", "Explorador da Vila", "Examine 20 objetos interativos."),
            Achievement("a_all_ev", "Investigação Completa", "Encontre as 6 evidências principais."),
            Achievement("a_curious", "Curioso por Natureza", "Descubra 5 curiosidades da região."),
            Achievement("a_voices", "Vozes da Comunidade", "Converse com 3 moradores diferentes.")
        ]
        
        self.main_objectives = [
            {"text": "Investigar a origem da contaminação do rio", "done": False},
            {"text": "Compreender os impactos sobre a comunidade", "done": False},
            {"text": "Investigar a atuação do poder público", "done": False},
            {"text": "Reunir as seis evidências principais (0/6)", "done": False}
        ]
        self.sec_objectives = [
            {"text": "Conhecer a história e curiosidades (0/5)", "done": False},
            {"text": "Examinar pelo menos 20 objetos (0/20)", "done": False}
        ]

    def add_xp(self, amount: int, reason: str):
        self.xp += amount
        self.add_notification(f"+{amount} XP: {reason}", COLOR_ACCENT_GREEN)
        self.check_level_up()

    def check_level_up(self):
        new_level = self.level
        for i, threshold in enumerate(self.level_thresholds):
            if self.xp >= threshold:
                new_level = i + 1
        if new_level > self.level:
            self.level = new_level
            self.add_notification(f"NÍVEL {self.level} ALCANÇADO: {self.level_names[self.level-1]}!", COLOR_ACCENT_GOLD)

    def unlock_achievement(self, ach_id: str):
        for a in self.achievements:
            if a.id == ach_id and not a.unlocked:
                a.unlocked = True
                self.add_notification(f"🏆 CONQUISTA: {a.title}", COLOR_ACCENT_CYAN)

    def add_notification(self, text: str, color: Tuple[int,int,int]):
        self.notifications.append({"text": text, "color": color, "time": 4.0})

    def update_notifications(self, dt: float):
        for n in self.notifications:
            n["time"] -= dt
        self.notifications = [n for n in self.notifications if n["time"] > 0]

    def get_level_progress(self):
        if self.level >= 5: return 1.0
        current_thresh = self.level_thresholds[self.level-1]
        next_thresh = self.level_thresholds[self.level]
        return (self.xp - current_thresh) / max(1, (next_thresh - current_thresh))

# ------------------------------------------------------------------------------
# CONTEÚDO DO JOGO (OBJETOS E DESAFIOS)
# ------------------------------------------------------------------------------
def create_interactables() -> List[Interactable]:
    items = []
    
    # --- CATEGORIA A: EVIDÊNCIAS (6) ---
    items.append(Interactable("ev1", "EVIDENCE", "Relatório Interno (Escritório)", pygame.Rect(1140, 160, 80, 70), 
        "MEMORANDO INTERNO — DIRETORIA EXECUTIVA\n\n\"Diante da necessidade de maximizar lucros, fica aprovada a redução de 65% nos custos operacionais da Estação de Tratamento. Eventuais multas devem ser tratadas como risco calculado, pois são inferiores ao custo de tratamento.\"", icon="document"))
    items.append(Interactable("ev2", "EVIDENCE", "Tubulação de Descarte", pygame.Rect(910, 370, 70, 60), 
        "LAUDO TÉCNICO DE INSPEÇÃO\n\n\"Identificada tubulação subterrânea lançando efluentes sem tratamento no rio. Amostras atestam metais pesados 14x acima do limite. A descarga ocorre à noite para burlar fiscalização visual.\"", icon="registry"))
    items.append(Interactable("ev3", "EVIDENCE", "Dona Francisca (Pescadora)", pygame.Rect(180, 520, 50, 70), 
        dialogues=[
            DialogueOption("O que aconteceu com a pesca?", "De uns meses pra cá, a água ficou pesada, com cheiro químico. Os peixes boiaram mortos. A gente não tem mais como tirar sustento daqui."),
            DialogueOption("Alguém adoeceu?", "Minha neta começou com feridas vermelhas na pele. Nós somos pobres, dependemos do rio e ficamos presos na contaminação."),
            DialogueOption("A prefeitura ajudou?", "Só promessas. Eles vêm aqui em época de eleição, mas na hora de enfrentar a fábrica, todos somem.")
        ], icon="speech"))
    items.append(Interactable("ev4", "EVIDENCE", "Trabalhador da Fábrica", pygame.Rect(900, 310, 50, 70), 
        dialogues=[
            DialogueOption("Você sabe sobre os despejos?", "Todo mundo no chão de fábrica sabe. A ordem vem direto da gerência. Desligam os filtros de madrugada."),
            DialogueOption("Por que ninguém denuncia?", "Se a gente falar, é rua. 'Tem cem na porta querendo sua vaga', eles dizem. Ficamos reféns do medo do desemprego."),
            DialogueOption("Vocês não se organizam?", "É difícil. A empresa usa nossa necessidade contra nós. Ameaçam fechar a fábrica se houver pressão ambiental.")
        ], icon="speech"))
    items.append(Interactable("ev5", "EVIDENCE", "Prefeitura (Arquivo)", pygame.Rect(190, 140, 60, 60), 
        "PROCESSO DE FISCALIZAÇÃO PARALISADO Nº 402/26\n\n\"Auto de infração propondo interdição cautelar. Processo retido no gabinete com parecer: 'Aguardando oportunidade oportuna devido ao impacto na arrecadação tributária'. Anexos mostram doações da empresa para campanhas.\"", icon="document"))
    items.append(Interactable("ev6", "EVIDENCE", "Associação de Moradores", pygame.Rect(530, 260, 60, 60), 
        "DOSSIÊ DE MOBILIZAÇÃO\n\n\"Compilado de 14 ofícios enviados aos órgãos públicos sem resposta. A comunidade formou um comitê autônomo para exigir saneamento e responsabilização, demonstrando que a solução passa pela união popular.\"", icon="news"))

    # --- CATEGORIA B: INFORMAÇÕES SECUNDÁRIAS (10) ---
    items.append(Interactable("sec1", "SECONDARY", "Mercadinho Local", pygame.Rect(350, 420, 80, 60), 
        dialogues=[DialogueOption("Como estão as vendas?", "Caíram muito. O pessoal da pesca não tem mais renda, então ninguém compra. A economia da vila inteira gira em torno do rio.")] ))
    items.append(Interactable("sec2", "SECONDARY", "Mural da Escola", pygame.Rect(70, 350, 60, 50), 
        "Trabalhos das crianças do 4º ano. Os desenhos mostram o rio escuro e peixinhos chorando. A degradação já faz parte do imaginário infantil da vila."))
    items.append(Interactable("sec3", "SECONDARY", "Aviso no Posto de Saúde", pygame.Rect(280, 300, 50, 30), 
        "\"ATENÇÃO: Devido ao aumento de casos de dermatite de contato e viroses, evitem utilizar a água do rio para banho ou lavagem de roupas.\""))
    items.append(Interactable("sec4", "SECONDARY", "Outdoor da Fábrica", pygame.Rect(780, 120, 100, 60), 
        "\"VALE DAS PEDRAS S.A. - O motor do desenvolvimento! Gerando 500 empregos diretos e construindo o futuro da nossa cidade.\""))
    items.append(Interactable("sec5", "SECONDARY", "Ponto de Ônibus (Trabalhador)", pygame.Rect(680, 350, 40, 60), 
        dialogues=[DialogueOption("Esperando condução?", "Sim, indo pro turno da fábrica. A gente reclama da poluição, mas sem essa empresa, metade da cidade passa fome. É uma armadilha.")] ))
    items.append(Interactable("sec6", "SECONDARY", "Pequena Plantação", pygame.Rect(50, 620, 80, 60), 
        "Horta comunitária. O agricultor colocou uma placa: 'Não estamos irrigando com água do rio'. As folhas de algumas hortaliças estão amareladas."))
    items.append(Interactable("sec7", "SECONDARY", "Bar da Comunidade", pygame.Rect(480, 430, 80, 60), 
        dialogues=[DialogueOption("Sobre o que conversam?", "(Morador) A gente discute como o prefeito não faz nada. Ele tem rabo preso com os donos da fábrica. O lucro fica lá, a sujeira fica aqui.")] ))
    items.append(Interactable("sec8", "SECONDARY", "Quadro de Empregos", pygame.Rect(940, 240, 50, 50), 
        "Diversas vagas para 'Auxiliar de Produção'. Os salários são baixos, mas a fila de currículos é imensa, revelando a forte dependência econômica da região."))
    items.append(Interactable("sec9", "SECONDARY", "Barco Abandonado", pygame.Rect(380, 640, 70, 40), 
        "Um barco de madeira rachado. O nome 'Esperança' está quase apagado. Há meses não entra na água por falta de peixes."))
    items.append(Interactable("sec10", "SECONDARY", "Placa de Área Verde", pygame.Rect(750, 450, 40, 40), 
        "Uma placa enferrujada do IBAMA de 15 anos atrás: 'Área de Preservação Permanente'. Hoje, o local está desmatado e coberto de resíduos sólidos."))

    # --- CATEGORIA C: CURIOSIDADES LOCAIS (8) ---
    items.append(Interactable("cur1", "CURIOSITY", "Placa do Rio", pygame.Rect(550, 680, 40, 40), "O nome 'Rio das Pedras' surgiu no século XIX, devido às grandes rochas que formavam piscinas naturais cristalinas no verão."))
    items.append(Interactable("cur2", "CURIOSITY", "Árvore Centenária", pygame.Rect(120, 430, 80, 130), "Uma imensa figueira. Os mais velhos dizem que as primeiras reuniões da comunidade aconteceram sob a sombra desta árvore."))
    items.append(Interactable("cur3", "CURIOSITY", "Pedra Fundamental", pygame.Rect(140, 220, 40, 40), "Placa de bronze: 'Vila das Águas - Fundada por pescadores artesanais em 1952'. A fundação é anterior à chegada da indústria."))
    items.append(Interactable("cur4", "CURIOSITY", "Cachorro Caramelo", pygame.Rect(250, 560, 30, 30), "Um cãozinho comunitário dormindo tranquilamente. Ele parece alheio aos problemas humanos da vila."))
    items.append(Interactable("cur5", "CURIOSITY", "Traves de Futebol", pygame.Rect(590, 520, 80, 40), "Restos de um antigo campo de terra. Com o avanço das margens degradadas, as crianças pararam de jogar bola aqui."))
    items.append(Interactable("cur6", "CURIOSITY", "Mural da Festa", pygame.Rect(590, 280, 50, 40), "Restos de cartazes da 'Festa de São Pedro', padroeiro dos pescadores. Nos últimos anos, a festa perdeu força pela falta de peixe."))
    items.append(Interactable("cur7", "CURIOSITY", "Flor do Deserto", pygame.Rect(210, 490, 20, 20), "Um pequeno vaso de Kalanchoe na janela. Alguém cuida dessa planta com carinho, utilizando adubo natural."))
    items.append(Interactable("cur8", "CURIOSITY", "Fotografia Antiga", pygame.Rect(490, 450, 30, 30), "Pendurada no bar, uma foto em preto e branco mostra dezenas de pescadores felizes segurando redes cheias. Um passado distante."))

    # --- CATEGORIA D: OBJETOS COMUNS (FLAVOR) (10) ---
    flavors = [
        ("Lixeira", pygame.Rect(315, 460, 25, 35), "Uma lixeira cheia. A coleta parece não passar por aqui há dias."),
        ("Banco da Praça", pygame.Rect(420, 460, 40, 25), "Um banco de madeira desgastado pelo tempo."),
        ("Bicicleta", pygame.Rect(530, 460, 40, 30), "Uma bicicleta antiga, principal meio de transporte local."),
        ("Poste de Luz", pygame.Rect(400, 370, 30, 90), "Poste com fios emaranhados e uma lâmpada queimada."),
        ("Caixa de Ferramentas", pygame.Rect(875, 340, 30, 25), "Equipamentos de manutenção dos operários. Nada suspeito."),
        ("Carrinho de Mão", pygame.Rect(75, 595, 40, 30), "Usado para transportar terra e vegetais da pequena horta."),
        ("Placa de Trânsito", pygame.Rect(650, 380, 30, 50), "Placa indicando limite de velocidade. Bastante enferrujada."),
        ("Tambores Industriais", pygame.Rect(1050, 350, 60, 40), "Tambores vazios empilhados no pátio da fábrica."),
        ("Caixas", pygame.Rect(300, 460, 35, 35), "Caixotes de madeira vazios perto do mercadinho."),
        ("Telefone Público", pygame.Rect(215, 360, 25, 40), "Um orelhão antigo que não funciona há anos.")
    ]
    for i, (n, r, t) in enumerate(flavors):
        items.append(Interactable(f"flav{i}", "FLAVOR", n, r, t))

    return items

# ------------------------------------------------------------------------------
# GERENCIADOR DE FONTES E DESENHOS (UI/VETORIAL)
# ------------------------------------------------------------------------------
class FontManager:
    _fonts = {}
    @classmethod
    def get(cls, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in cls._fonts:
            try:
                cls._fonts[key] = pygame.font.SysFont("arial", size, bold=bold)
            except:
                cls._fonts[key] = pygame.font.Font(None, size)
        return cls._fonts[key]

class UIUtils:
    @staticmethod
    def draw_rounded_rect(surf, rect, color, radius=8, border_width=0, border_color=None):
        pygame.draw.rect(surf, color, rect, border_radius=radius)
        if border_width > 0 and border_color:
            pygame.draw.rect(surf, border_color, rect, width=border_width, border_radius=radius)

    @staticmethod
    def draw_text(surf, text, rect, font, color, line_spacing=4, center=False):
        if not text: return
        words = text.replace('\n', ' \n ').split(' ')
        lines, current = [], []
        for word in words:
            if word == '\n':
                lines.append(" ".join(current))
                current = []
            else:
                if font.size(" ".join(current + [word]))[0] <= rect.width:
                    current.append(word)
                else:
                    lines.append(" ".join(current))
                    current = [word]
        if current: lines.append(" ".join(current))
        
        y = rect.y
        for line in lines:
            if not line.strip():
                y += font.get_linesize()
                continue
            ts = font.render(line, True, color)
            x = rect.x + (rect.width - ts.get_width())//2 if center else rect.x
            surf.blit(ts, (x, y))
            y += font.get_linesize() + line_spacing

    @staticmethod
    def draw_icon(surf, icon_type, pos, size, color):
        cx, cy = pos
        hs = size // 2
        if icon_type == "magnifier":
            pygame.draw.circle(surf, color, (cx-3, cy-3), hs-2, 2)
            pygame.draw.line(surf, color, (cx+1, cy+1), (cx+hs, cy+hs), 3)
        elif icon_type == "document":
            pygame.draw.rect(surf, color, (cx-hs+2, cy-hs, size-4, size), 2, 2)
            pygame.draw.line(surf, color, (cx-hs+6, cy-hs+6), (cx+hs-6, cy-hs+6), 2)
            pygame.draw.line(surf, color, (cx-hs+6, cy-hs+12), (cx+hs-6, cy-hs+12), 2)
        elif icon_type == "speech":
            pygame.draw.rect(surf, color, (cx-hs, cy-hs, size, size-4), 2, 3)
            pygame.draw.polygon(surf, color, [(cx-4, cy+hs-4), (cx-8, cy+hs), (cx+2, cy+hs-4)])
        elif icon_type == "registry":
            pygame.draw.rect(surf, color, (cx-hs, cy-hs, size, size), 2, 2)
            pygame.draw.line(surf, color, (cx-4, cy-2), (cx, cy+4), 2)
            pygame.draw.line(surf, color, (cx, cy+4), (cx+6, cy-4), 2)
        elif icon_type == "news":
            pygame.draw.rect(surf, color, (cx-hs, cy-hs, size, size), 2, 2)
            pygame.draw.rect(surf, color, (cx-hs+4, cy-hs+4, 6, 6))
            pygame.draw.line(surf, color, (cx+2, cy-hs+6), (cx+hs-4, cy-hs+6), 2)
        elif icon_type == "check":
            pygame.draw.line(surf, color, (cx-6, cy), (cx-2, cy+6), 3)
            pygame.draw.line(surf, color, (cx-2, cy+6), (cx+8, cy-6), 3)
        else:
            pygame.draw.circle(surf, color, (cx, cy), hs-2, 2)

class Button:
    def __init__(self, rect, text, bg_color=COLOR_PANEL_ALT, hover_color=COLOR_PANEL_BORDER, 
                 text_color=COLOR_TEXT_LIGHT, font_size=16):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.is_hovered = False

    def draw(self, surf, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if self.is_hovered else self.bg_color
        UIUtils.draw_rounded_rect(surf, self.rect, color, radius=6, border_width=2, border_color=COLOR_ACCENT_GOLD if self.is_hovered else COLOR_PANEL_BORDER)
        ts = FontManager.get(self.font_size, True).render(self.text, True, COLOR_ACCENT_GOLD if self.is_hovered else self.text_color)
        surf.blit(ts, ts.get_rect(center=self.rect.center))

    def clicked(self, event, mouse_pos):
        # GARANTE QUE CLIQUE FANTASMA NÃO OCORRA! Ação apenas no botão físico pressionado.
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(mouse_pos)

# ------------------------------------------------------------------------------
# RENDERIZADOR DO CENÁRIO COMPLETO COM TODOS OS OBJETOS DESENHADOS
# ------------------------------------------------------------------------------
class ScenarioRenderer:
    def __init__(self):
        self.bg_surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        self.draw_static_background()

    def draw_static_background(self):
        surf = self.bg_surf
        surf.fill((20, 28, 38)) # Céu
        
        # 1. Montanhas/Relevo ao fundo
        pygame.draw.polygon(surf, (30, 40, 48), [(0,250), (400,180), (800,220), (1280,150), (1280,300), (0,300)])
        
        # 2. Solo principal e ruas
        pygame.draw.polygon(surf, (45, 55, 42), [(0, 280), (1280, 280), (1280, 720), (0, 720)])
        pygame.draw.polygon(surf, (60, 60, 65), [(0, 400), (600, 400), (750, 280), (1280, 280), (1280, 360), (700, 480), (0, 480)])
        pygame.draw.polygon(surf, (55, 55, 60), [(200, 480), (300, 720), (220, 720), (120, 480)])

        # 3. Rio das Pedras e margens degradadas
        river_pts = [(1280, 380), (950, 450), (600, 520), (400, 650), (450, 720), (700, 720), (850, 600), (1100, 500), (1280, 450)]
        pygame.draw.polygon(surf, (35, 60, 65), river_pts)
        pygame.draw.polygon(surf, (100, 90, 70), river_pts, 4) 
        
        # 4. ÁREA INDUSTRIAL (Direita/Topo)
        pygame.draw.rect(surf, (40, 45, 50), (850, 100, 400, 240)) # Pátio fábrica
        pygame.draw.rect(surf, (60, 65, 75), (920, 160, 120, 120)) # Galpão 1
        pygame.draw.polygon(surf, (50, 55, 65), [(900, 160), (980, 110), (1060, 160)])
        pygame.draw.rect(surf, (55, 60, 70), (1050, 180, 150, 100)) # Galpão 2
        # Placa Fábrica
        pygame.draw.rect(surf, (30, 40, 50), (930, 175, 100, 25), border_radius=4)
        UIUtils.draw_text(surf, "VALE DAS PEDRAS", pygame.Rect(930, 182, 100, 25), FontManager.get(9, True), COLOR_ACCENT_GOLD, center=True)
        for tx in [870, 920]: pygame.draw.rect(surf, (150, 160, 170), (tx, 200, 40, 80), border_radius=10) # Tanques
        # Caminhão
        pygame.draw.rect(surf, (180, 40, 40), (1000, 300, 60, 30), border_radius=4)
        pygame.draw.rect(surf, (200, 200, 200), (1060, 290, 80, 40), border_radius=2)
        pygame.draw.circle(surf, (20,20,20), (1020, 330), 10)
        pygame.draw.circle(surf, (20,20,20), (1080, 330), 10)
        pygame.draw.circle(surf, (20,20,20), (1120, 330), 10)
        # Tubulação de esgoto (ev2)
        pygame.draw.rect(surf, (50, 50, 55), (920, 340, 20, 80))
        pygame.draw.polygon(surf, (30, 45, 40), [(915, 420), (945, 420), (960, 480), (900, 480)])
        # Quadro de Empregos (sec8)
        pygame.draw.rect(surf, (80, 90, 100), (940, 240, 50, 30))
        for x in [945, 958, 971, 950]: pygame.draw.rect(surf, (255, 255, 255), (x, 245 if x!=950 else 255, 8, 10))
        # Tambores Industriais (flav7)
        for dx in [1050, 1070, 1090]:
            pygame.draw.rect(surf, (40, 80, 150), (dx, 360, 15, 20))
            pygame.draw.line(surf, (200, 200, 50), (dx, 365), (dx+15, 365), 2)
            pygame.draw.line(surf, (200, 200, 50), (dx, 375), (dx+15, 375), 2)
            
        # 5. ÁRVORES (incluindo Árvore Centenária)
        trees = [(50,350), (100,320), (400,250), (450,220), (700,200), (800,250), (750, 400), (150,600)]
        for tx, ty in trees:
            pygame.draw.rect(surf, (60, 40, 20), (tx-5, ty, 10, 30))
            pygame.draw.circle(surf, (30, 70, 40), (tx, ty-10), 25)
            pygame.draw.circle(surf, (40, 80, 50), (tx-10, ty-20), 20)
            pygame.draw.circle(surf, (20, 60, 30), (tx+10, ty-15), 18)
        # Árvore Centenária (cur2)
        pygame.draw.rect(surf, (50, 35, 20), (140, 470, 20, 90)) # Tronco espesso
        pygame.draw.polygon(surf, (50, 35, 20), [(140, 560), (120, 580), (150, 560)]) # Raiz esq
        pygame.draw.polygon(surf, (50, 35, 20), [(160, 560), (180, 575), (150, 560)]) # Raiz dir
        pygame.draw.circle(surf, (25, 60, 35), (150, 440), 55) # Copa enorme
        pygame.draw.circle(surf, (35, 75, 45), (125, 470), 45)
        pygame.draw.circle(surf, (20, 50, 30), (175, 465), 45)

        # 6. EDIFÍCIOS INSTITUCIONAIS
        # Prefeitura (ev5)
        pygame.draw.rect(surf, (190, 190, 185), (150, 120, 140, 100))
        pygame.draw.polygon(surf, (110, 120, 130), [(140, 120), (220, 60), (300, 120)])
        for cx in range(160, 280, 25): pygame.draw.rect(surf, (220, 220, 215), (cx, 120, 12, 100))
        pygame.draw.rect(surf, (60, 40, 30), (205, 170, 30, 50)) # Porta
        pygame.draw.rect(surf, (50, 60, 70), (175, 95, 90, 20)) # Placa
        UIUtils.draw_text(surf, "PREFEITURA", pygame.Rect(175, 98, 90, 20), FontManager.get(10, True), COLOR_TEXT_LIGHT, center=True)
        pygame.draw.line(surf, (200, 200, 200), (220, 60), (220, 20), 2) # Bandeira mastro
        pygame.draw.rect(surf, (40, 120, 60), (220, 25, 25, 15)) # Bandeira

        # Escola (sec2)
        pygame.draw.rect(surf, (220, 200, 130), (60, 320, 120, 80))
        pygame.draw.rect(surf, (160, 70, 50), (50, 310, 140, 15)) # Telhado
        pygame.draw.rect(surf, (255, 255, 255), (85, 325, 70, 18)) # Placa
        UIUtils.draw_text(surf, "ESCOLA", pygame.Rect(85, 327, 70, 18), FontManager.get(11, True), (0,0,0), center=True)
        pygame.draw.rect(surf, (100, 150, 200), (70, 355, 25, 25)) # Janelas
        pygame.draw.rect(surf, (100, 150, 200), (145, 355, 25, 25))
        pygame.draw.rect(surf, (60, 40, 30), (105, 360, 30, 40)) # Porta
        pygame.draw.rect(surf, (200, 200, 200), (70, 385, 30, 15)) # Mural da escola (sec2 fixo visual)
        pygame.draw.rect(surf, (255, 100, 100), (72, 387, 8, 8))
        pygame.draw.rect(surf, (100, 255, 100), (85, 387, 8, 8))

        # Posto de Saúde (sec3)
        pygame.draw.rect(surf, (230, 240, 245), (280, 270, 90, 60))
        pygame.draw.rect(surf, (100, 110, 120), (275, 260, 100, 10))
        pygame.draw.rect(surf, (40, 100, 180), (290, 275, 70, 15)) # Placa
        UIUtils.draw_text(surf, "POSTO SAÚDE", pygame.Rect(290, 277, 70, 15), FontManager.get(9, True), (255,255,255), center=True)
        pygame.draw.rect(surf, (200, 40, 40), (315, 295, 20, 8)) # Cruz
        pygame.draw.rect(surf, (200, 40, 40), (321, 289, 8, 20))
        pygame.draw.rect(surf, (200, 210, 220), (290, 300, 20, 30)) # Porta
        pygame.draw.rect(surf, (255, 255, 200), (285, 305, 10, 15)) # Aviso do posto

        # Associação de Moradores (ev6)
        pygame.draw.rect(surf, (100, 130, 110), (500, 250, 120, 70))
        pygame.draw.polygon(surf, (120, 60, 50), [(490, 250), (560, 210), (630, 250)])
        pygame.draw.rect(surf, (230, 230, 220), (510, 255, 100, 15)) # Placa
        UIUtils.draw_text(surf, "ASSOC. MORADORES", pygame.Rect(510, 257, 100, 15), FontManager.get(9, True), (0,0,0), center=True)
        pygame.draw.rect(surf, (80, 50, 40), (545, 285, 30, 35)) # Porta
        pygame.draw.rect(surf, (200, 200, 50), (515, 290, 10, 15)) # Cartazes
        pygame.draw.rect(surf, (50, 150, 200), (585, 280, 15, 20))

        # 7. ÁREA COMUNITÁRIA E COMERCIAL
        # Casas
        house_pos = [(50, 400), (150, 380), (50, 480), (120, 520), (250, 420)]
        for hx, hy in house_pos:
            pygame.draw.rect(surf, (150, 130, 100), (hx, hy, 60, 50))
            pygame.draw.polygon(surf, (120, 50, 40), [(hx-10, hy), (hx+30, hy-30), (hx+70, hy)])
            pygame.draw.rect(surf, (60, 40, 30), (hx+20, hy+20, 20, 30))
        # Flor do Deserto (cur7) numa das casas
        pygame.draw.rect(surf, (150, 80, 60), (215, 495, 10, 10))
        pygame.draw.circle(surf, (255, 100, 150), (220, 492), 4)

        # Mercadinho (sec1)
        pygame.draw.rect(surf, (140, 180, 150), (330, 410, 100, 70))
        for i in range(10): # Toldo listrado
            pygame.draw.rect(surf, (200,50,50) if i%2==0 else (240,240,240), (330+i*10, 410, 10, 20))
        pygame.draw.rect(surf, (255, 255, 255), (340, 390, 80, 18))
        UIUtils.draw_text(surf, "MERCADINHO", pygame.Rect(340, 392, 80, 18), FontManager.get(10, True), (0,0,0), center=True)
        pygame.draw.rect(surf, (50, 40, 30), (370, 440, 25, 40)) # Porta
        pygame.draw.rect(surf, (100, 150, 200), (340, 440, 25, 25)) # Janela vitrine

        # Bar da Comunidade (sec7)
        pygame.draw.rect(surf, (180, 150, 100), (460, 420, 90, 60))
        pygame.draw.polygon(surf, (100, 50, 40), [(450, 420), (505, 390), (560, 420)])
        pygame.draw.rect(surf, (30, 30, 30), (480, 425, 50, 18))
        UIUtils.draw_text(surf, "BAR", pygame.Rect(480, 427, 50, 18), FontManager.get(12, True), (255, 255, 0), center=True)
        pygame.draw.rect(surf, (60, 30, 20), (510, 445, 25, 35))
        pygame.draw.rect(surf, (80, 40, 30), (475, 445, 25, 25))
        pygame.draw.rect(surf, (200, 200, 200), (490, 450, 15, 15), 1) # Fotografia Antiga (cur8)
        pygame.draw.rect(surf, (100, 100, 100), (492, 452, 11, 11))
        pygame.draw.rect(surf, (120, 80, 50), (450, 470, 20, 5)) # Mesa rua
        pygame.draw.rect(surf, (120, 80, 50), (458, 475, 4, 10))

        # 8. OBJETOS DIVERSOS DO CENÁRIO COMPLETO
        # Traves de Futebol (cur5)
        pygame.draw.line(surf, (220, 220, 220), (600, 560), (600, 520), 3) 
        pygame.draw.line(surf, (220, 220, 220), (660, 560), (660, 520), 3) 
        pygame.draw.line(surf, (220, 220, 220), (598, 520), (662, 520), 3) 
        pygame.draw.ellipse(surf, (150, 130, 100), (590, 545, 80, 20), 2) # Terra batida

        # Barco Abandonado (sec9)
        pygame.draw.polygon(surf, (100, 70, 50), [(380, 640), (440, 640), (450, 670), (390, 680)])
        pygame.draw.line(surf, (60, 40, 20), (380, 640), (450, 670), 2) 
        pygame.draw.polygon(surf, (80, 50, 30), [(390, 680), (450, 670), (450, 675), (390, 685)]) 

        # Ponto de Ônibus (sec5)
        pygame.draw.rect(surf, (150, 150, 160), (680, 350, 40, 60), 3) # Estrutura
        pygame.draw.rect(surf, (100, 100, 110), (675, 345, 50, 10)) # Teto
        pygame.draw.rect(surf, (180, 120, 80), (685, 385, 30, 5)) # Banco
        pygame.draw.rect(surf, (50, 150, 255), (710, 355, 10, 10)) # Placa bus

        # Placa do Rio (cur1) e Pedra Fundamental (cur3)
        pygame.draw.rect(surf, (100, 70, 40), (565, 680, 5, 20)) 
        pygame.draw.rect(surf, (130, 100, 60), (555, 680, 25, 15)) 
        pygame.draw.line(surf, (0,0,0), (558, 687), (577, 687))
        pygame.draw.polygon(surf, (150, 150, 150), [(140, 260), (160, 240), (180, 260)]) # Pedra
        pygame.draw.rect(surf, (180, 150, 50), (155, 250, 10, 8)) 

        # Cachorro Caramelo (cur4)
        pygame.draw.ellipse(surf, (210, 150, 50), (250, 570, 25, 15)) 
        pygame.draw.ellipse(surf, (210, 150, 50), (265, 575, 12, 10)) 
        pygame.draw.circle(surf, (0,0,0), (275, 580), 2) 
        pygame.draw.line(surf, (210, 150, 50), (250, 575), (240, 585), 3) 

        # Mural da Festa (cur6)
        pygame.draw.rect(surf, (120, 90, 60), (590, 280, 40, 30))
        for mx in [595, 610, 602]: pygame.draw.rect(surf, (random.randint(100,255), random.randint(100,255), 100), (mx, 285, 8, 12))

        # Horta Comunitária (sec6)
        pygame.draw.rect(surf, (80, 50, 30), (50, 620, 70, 40)) 
        pygame.draw.rect(surf, (80, 50, 30), (50, 665, 70, 20)) 
        for px in range(55, 115, 15):
            pygame.draw.circle(surf, (100, 180, 80), (px, 630), 6)
            pygame.draw.circle(surf, (180, 200, 80), (px, 645), 5) # Amarelado da contaminação
            pygame.draw.circle(surf, (80, 160, 60), (px, 675), 6)
        pygame.draw.rect(surf, (150, 120, 80), (110, 635, 15, 10)) # Plaquinha
        pygame.draw.line(surf, (100, 70, 40), (117, 645), (117, 655), 2)

        # Placa de Preservação Área Verde (sec10)
        pygame.draw.rect(surf, (100, 100, 100), (765, 460, 4, 30))
        pygame.draw.rect(surf, (50, 120, 80), (755, 450, 24, 15)) 
        pygame.draw.rect(surf, (200, 200, 200), (757, 452, 20, 11), 1) 

        # Objetos "Flavors" (Lixeira, Banco, Bicicleta, Poste, Ferramentas, etc)
        pygame.draw.rect(surf, (100, 100, 100), (315, 460, 15, 20)) # Lixeira
        pygame.draw.line(surf, (200, 50, 50), (317, 458), (323, 462), 3) 
        pygame.draw.line(surf, (50, 200, 50), (325, 455), (320, 460), 2)
        pygame.draw.rect(surf, (130, 90, 50), (420, 460, 30, 5)) # Banco
        pygame.draw.rect(surf, (130, 90, 50), (420, 468, 30, 5))
        pygame.draw.line(surf, (50, 50, 50), (425, 473), (425, 480), 2)
        pygame.draw.line(surf, (50, 50, 50), (445, 473), (445, 480), 2)
        pygame.draw.circle(surf, (50, 50, 50), (540, 480), 8, 2) # Bicicleta
        pygame.draw.circle(surf, (50, 50, 50), (565, 480), 8, 2) 
        pygame.draw.polygon(surf, (200, 50, 50), [(540, 480), (552, 480), (560, 470), (548, 470)], 2)
        pygame.draw.line(surf, (200, 200, 200), (560, 470), (562, 460), 2) 
        pygame.draw.rect(surf, (80, 80, 80), (408, 370, 4, 90)) # Poste
        pygame.draw.line(surf, (80, 80, 80), (410, 370), (425, 370), 3)
        pygame.draw.circle(surf, (255, 255, 100), (425, 372), 4) 
        pygame.draw.rect(surf, (200, 40, 40), (875, 340, 20, 10)) # Ferramentas
        pygame.draw.line(surf, (50, 50, 50), (880, 335), (890, 335), 2) 
        pygame.draw.line(surf, (50, 50, 50), (880, 335), (880, 340), 2)
        pygame.draw.line(surf, (50, 50, 50), (890, 335), (890, 340), 2)
        pygame.draw.polygon(surf, (50, 150, 80), [(80, 605), (100, 605), (105, 615), (85, 615)]) # Carrinho
        pygame.draw.circle(surf, (30, 30, 30), (105, 620), 5) 
        pygame.draw.line(surf, (150, 150, 150), (70, 600), (85, 610), 2) 
        pygame.draw.rect(surf, (100, 100, 100), (658, 390, 4, 30)) # Placa transito
        pygame.draw.circle(surf, (200, 40, 40), (660, 385), 10)
        pygame.draw.circle(surf, (255, 255, 255), (660, 385), 7)
        pygame.draw.line(surf, (0, 0, 0), (656, 385), (664, 385), 2)
        pygame.draw.rect(surf, (160, 110, 70), (300, 470, 20, 20)) # Caixas perto mercadinho
        pygame.draw.rect(surf, (180, 130, 80), (310, 460, 20, 20))
        pygame.draw.rect(surf, (100, 100, 100), (225, 370, 4, 30)) # Orelhão
        pygame.draw.ellipse(surf, (50, 180, 80), (218, 360, 18, 22)) 

    def draw_dynamic(self, surf, time_sec):
        # Água animada (manchas)
        for i in range(5):
            ox = 1000 - i*120 + math.cos(time_sec+i)*10
            oy = 480 + i*40 + math.sin(time_sec*2+i)*5
            pygame.draw.ellipse(surf, (45, 80, 75), (ox, oy, 60, 20))
        
        # Fumaça
        for i in range(4):
            sx = 930 + i*40
            sy = 120 - (time_sec * 40 + i*20) % 80
            alpha = max(0, 150 - int(((120-sy)/80)*150))
            pygame.draw.circle(surf, (80,85,90,alpha), (sx + math.sin(time_sec*3+i)*15, sy), 20 + ((120-sy)/3))
            
        # NPCs (cabeças balançando levemente). Coordenadas baseadas nas interações para encaixe perfeito
        npcs = [(910, 340, COLOR_ACCENT_GOLD), # Trabalhador Fábrica ev4
                (690, 380, (150,100,50)),      # Trabalhador Ponto sec5
                (200, 550, (200,150,150)),     # Dona Francisca ev3
                (380, 450, (100,150,200)),     # Morador 1 (Aleatorio perto mercado)
                (500, 460, (180,80,80))]       # Morador Bar sec7
        for nx, ny, c in npcs:
            bob = abs(math.sin(time_sec*4 + nx)) * 4
            pygame.draw.rect(surf, c, (nx-5, ny-15-bob, 10, 20), border_radius=4)
            pygame.draw.circle(surf, (220,180,150), (nx, ny-20-bob), 6)

# ------------------------------------------------------------------------------
# UI DOS MINIGAMES E PAINEIS
# ------------------------------------------------------------------------------
class UIWindow:
    def __init__(self, title, width=1000, height=600):
        self.rect = pygame.Rect((VIRTUAL_WIDTH-width)//2, (VIRTUAL_HEIGHT-height)//2, width, height)
        self.title = title
        self.btn_close = Button((self.rect.right-120, self.rect.y+15, 100, 35), "FECHAR", COLOR_ACCENT_RED, font_size=14)

    def draw_base(self, surf, mouse_pos):
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5,10,15, 200))
        surf.blit(overlay, (0,0))
        UIUtils.draw_rounded_rect(surf, self.rect, COLOR_PANEL_BG, radius=12, border_width=2, border_color=COLOR_PANEL_BORDER)
        ts = FontManager.get(24, True).render(self.title, True, COLOR_ACCENT_GOLD)
        surf.blit(ts, (self.rect.x + 30, self.rect.y + 20))
        pygame.draw.line(surf, COLOR_PANEL_BORDER, (self.rect.x, self.rect.y+60), (self.rect.right, self.rect.y+60), 2)
        self.btn_close.draw(surf, mouse_pos)

class Challenge1(UIWindow):
    def __init__(self, game):
        super().__init__("DESAFIO: LINHA DO TEMPO", 800, 500)
        self.game = game
        self.events = [
            "Expansão das atividades industriais.",
            "Redução dos investimentos no tratamento de resíduos.",
            "Início dos despejos irregulares noturnos no rio.",
            "Primeiras mortandades de peixes e problemas de saúde.",
            "Paralisação do processo de fiscalização na Prefeitura."
        ]
        self.current = list(self.events)
        random.shuffle(self.current)
        self.selected_idx = -1
        self.solved = False
        self.btn_check = Button((self.rect.centerx-100, self.rect.bottom-60, 200, 40), "VERIFICAR", COLOR_ACCENT_GOLD, text_color=(0,0,0))

    def draw(self, surf, mouse_pos):
        self.draw_base(surf, mouse_pos)
        if self.solved:
            UIUtils.draw_text(surf, "✅ Linha do tempo organizada corretamente!\n\nCompreender a cronologia prova que o dano não foi acidental, mas um projeto econômico.", 
                              pygame.Rect(self.rect.x+50, self.rect.y+100, 700, 300), FontManager.get(18, True), COLOR_ACCENT_GREEN, center=True)
            return

        UIUtils.draw_text(surf, "Clique em dois eventos para trocar suas posições e organize-os cronologicamente:", 
                          pygame.Rect(self.rect.x+40, self.rect.y+80, 720, 30), FontManager.get(16), COLOR_TEXT_LIGHT)
        
        for i, ev in enumerate(self.current):
            r = pygame.Rect(self.rect.x+100, self.rect.y+130 + i*55, 600, 45)
            is_sel = (i == self.selected_idx)
            UIUtils.draw_rounded_rect(surf, r, (50,60,70) if is_sel else COLOR_PANEL_ALT, border_width=2 if is_sel else 1, border_color=COLOR_ACCENT_GOLD if is_sel else COLOR_PANEL_BORDER)
            UIUtils.draw_text(surf, f"{i+1}. {ev}", pygame.Rect(r.x+15, r.y+12, r.width-30, r.height), FontManager.get(14), COLOR_TEXT_LIGHT)
        
        self.btn_check.draw(surf, mouse_pos)

    def handle_event(self, event, mouse_pos):
        # Proteção contra Ghost Clicks (Ações somente no clique físico esquerdo)
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1: return "KEEP"
        if self.btn_close.rect.collidepoint(mouse_pos): return "CLOSE"
        if self.solved: return "KEEP"
        
        for i in range(5):
            r = pygame.Rect(self.rect.x+100, self.rect.y+130 + i*55, 600, 45)
            if r.collidepoint(mouse_pos):
                if self.selected_idx == -1: self.selected_idx = i
                else:
                    self.current[self.selected_idx], self.current[i] = self.current[i], self.current[self.selected_idx]
                    self.selected_idx = -1
                return "KEEP"
                
        if self.btn_check.rect.collidepoint(mouse_pos):
            if self.current == self.events:
                self.solved = True
                self.game.gamif.add_xp(100, "Desafio Concluído")
            else:
                self.game.gamif.add_notification("A ordem ainda não está correta.", COLOR_ACCENT_RED)
        return "KEEP"

class Challenge2(UIWindow):
    def __init__(self, game):
        super().__init__("DESAFIO: ANÁLISE DO DISCURSO", 900, 550)
        self.game = game
        self.claims = [
            ("A empresa atua com responsabilidade ambiental e tratamento adequado.", "ev2"),
            ("As atividades da fábrica trazem prosperidade para toda a população.", "ev3"),
            ("A empresa possui uma relação ética e transparente com a cidade.", "ev5")
        ]
        self.matches = [False, False, False]
        self.selected_claim = -1
        self.solved = False

    def draw(self, surf, mouse_pos):
        self.draw_base(surf, mouse_pos)
        if self.solved:
            UIUtils.draw_text(surf, "✅ Análise concluída!\n\nAs propagandas institucionais frequentemente ocultam a externalização dos custos ambientais e sociais.", 
                              pygame.Rect(self.rect.x+50, self.rect.y+200, 800, 300), FontManager.get(18, True), COLOR_ACCENT_GREEN, center=True)
            return

        UIUtils.draw_text(surf, "Selecione uma afirmação da propaganda à esquerda e conecte com a evidência que a desmente à direita:", 
                          pygame.Rect(self.rect.x+30, self.rect.y+80, 840, 30), FontManager.get(15), COLOR_TEXT_LIGHT)
        
        # Left Side (Claims)
        for i, (claim, _) in enumerate(self.claims):
            r = pygame.Rect(self.rect.x+30, self.rect.y+130 + i*100, 380, 80)
            col = COLOR_ACCENT_GREEN if self.matches[i] else ((50,60,70) if i == self.selected_claim else COLOR_PANEL_ALT)
            UIUtils.draw_rounded_rect(surf, r, col, border_width=1, border_color=COLOR_PANEL_BORDER)
            UIUtils.draw_text(surf, claim, pygame.Rect(r.x+10, r.y+10, r.width-20, r.height-20), FontManager.get(14, True), (0,0,0) if self.matches[i] else COLOR_TEXT_LIGHT)

        # Right Side (Evidences)
        evs = [e for e in self.game.items if e.type == "EVIDENCE" and e.inspected]
        for i, ev in enumerate(evs):
            r = pygame.Rect(self.rect.centerx+20, self.rect.y+130 + (i%4)*90, 400, 70)
            UIUtils.draw_rounded_rect(surf, r, COLOR_PANEL_ALT, border_width=1, border_color=COLOR_PANEL_BORDER)
            UIUtils.draw_text(surf, ev.name, pygame.Rect(r.x+10, r.y+10, r.width-20, r.height-20), FontManager.get(12, True), COLOR_TEXT_MUTED)
            UIUtils.draw_text(surf, ev.text[:60]+"...", pygame.Rect(r.x+10, r.y+30, r.width-20, 30), FontManager.get(11), COLOR_TEXT_MUTED)

    def handle_event(self, event, mouse_pos):
        # Proteção contra Ghost Clicks
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1: return "KEEP"
        if self.btn_close.rect.collidepoint(mouse_pos): return "CLOSE"
        if self.solved: return "KEEP"
        
        for i in range(3):
            if not self.matches[i] and pygame.Rect(self.rect.x+30, self.rect.y+130 + i*100, 380, 80).collidepoint(mouse_pos):
                self.selected_claim = i
                return "KEEP"
                
        evs = [e for e in self.game.items if e.type == "EVIDENCE" and e.inspected]
        if self.selected_claim != -1:
            for i, ev in enumerate(evs):
                if pygame.Rect(self.rect.centerx+20, self.rect.y+130 + (i%4)*90, 400, 70).collidepoint(mouse_pos):
                    if ev.id == self.claims[self.selected_claim][1]:
                        self.matches[self.selected_claim] = True
                        self.selected_claim = -1
                        self.game.gamif.add_notification("Contradição revelada!", COLOR_ACCENT_GREEN)
                        if all(self.matches):
                            self.solved = True
                            self.game.gamif.add_xp(100, "Desafio Concluído")
                    else:
                        self.game.gamif.add_notification("Essa evidência não desmente diretamente a afirmação.", COLOR_ACCENT_RED)
                        self.selected_claim = -1
                    return "KEEP"
        return "KEEP"

class BackpackUI(UIWindow):
    def __init__(self, game):
        super().__init__("MOCHILA E REGISTROS", 1100, 620)
        self.game = game
        self.tab = "EVIDENCE"
        self.tabs = [("EVIDENCE", "Evidências"), ("SECONDARY", "Info Secundária"), ("CURIOSITY", "Curiosidades")]
        self.selected_item = None

    def draw(self, surf, mouse_pos):
        self.draw_base(surf, mouse_pos)
        
        # Draw Tabs
        tx = self.rect.x + 30
        for tid, tname in self.tabs:
            tr = pygame.Rect(tx, self.rect.y+70, 160, 35)
            is_sel = (self.tab == tid)
            pygame.draw.rect(surf, COLOR_PANEL_ALT if is_sel else COLOR_PANEL_BG, tr, border_radius=4)
            if is_sel: pygame.draw.rect(surf, COLOR_ACCENT_GOLD, (tr.x, tr.bottom-2, tr.width, 2))
            UIUtils.draw_text(surf, tname, tr, FontManager.get(14, True), COLOR_ACCENT_GOLD if is_sel else COLOR_TEXT_MUTED, center=True)
            tx += 170

        # Draw Items List
        items = [i for i in self.game.items if i.type == self.tab and i.inspected]
        iy = self.rect.y + 120
        pygame.draw.rect(surf, (20,28,36), (self.rect.x+30, iy, 350, 460), border_radius=6)
        
        for idx, item in enumerate(items):
            r = pygame.Rect(self.rect.x+35, iy + 5 + idx*45, 340, 40)
            is_sel = (self.selected_item == item)
            pygame.draw.rect(surf, (40,50,60) if is_sel else (25,35,45), r, border_radius=4)
            UIUtils.draw_text(surf, item.name, pygame.Rect(r.x+10, r.y+10, r.width-20, 20), FontManager.get(13), COLOR_TEXT_LIGHT)
            
        # Draw Details
        det_rect = pygame.Rect(self.rect.x+400, iy, 660, 460)
        UIUtils.draw_rounded_rect(surf, det_rect, COLOR_PANEL_ALT, radius=6, border_width=1, border_color=COLOR_PANEL_BORDER)
        if self.selected_item:
            UIUtils.draw_text(surf, self.selected_item.name, pygame.Rect(det_rect.x+20, det_rect.y+20, 620, 40), FontManager.get(22, True), COLOR_ACCENT_GOLD)
            pygame.draw.line(surf, COLOR_PANEL_BORDER, (det_rect.x+20, det_rect.y+60), (det_rect.right-20, det_rect.y+60))
            if self.selected_item.text:
                UIUtils.draw_text(surf, self.selected_item.text, pygame.Rect(det_rect.x+20, det_rect.y+80, 620, 360), FontManager.get(16), COLOR_TEXT_LIGHT, line_spacing=6)
            elif self.selected_item.dialogues:
                dy = det_rect.y+80
                for d in self.selected_item.dialogues:
                    UIUtils.draw_text(surf, f"P: {d.question}", pygame.Rect(det_rect.x+20, dy, 620, 20), FontManager.get(14, True), COLOR_ACCENT_CYAN)
                    dy += 25
                    UIUtils.draw_text(surf, f"R: {d.answer}", pygame.Rect(det_rect.x+20, dy, 620, 50), FontManager.get(14), COLOR_TEXT_MUTED)
                    dy += 55
        else:
            UIUtils.draw_text(surf, "Selecione um registro na lista ao lado.", det_rect, FontManager.get(16), COLOR_TEXT_MUTED, center=True)

    def handle_event(self, event, mouse_pos):
        # Proteção rigorosa contra Ghost Clicks na mochila
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1: return "KEEP"
        if self.btn_close.rect.collidepoint(mouse_pos): return "CLOSE"
        
        tx = self.rect.x + 30
        for tid, _ in self.tabs:
            if pygame.Rect(tx, self.rect.y+70, 160, 35).collidepoint(mouse_pos):
                self.tab = tid
                self.selected_item = None
                return "KEEP"
            tx += 170
            
        items = [i for i in self.game.items if i.type == self.tab and i.inspected]
        iy = self.rect.y + 120
        for idx, item in enumerate(items):
            if pygame.Rect(self.rect.x+35, iy + 5 + idx*45, 340, 40).collidepoint(mouse_pos):
                self.selected_item = item
                return "KEEP"
        return "KEEP"

# ------------------------------------------------------------------------------
# CLASSE PRINCIPAL DO JOGO E HUD
# ------------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Detetives Ambientais: Por Trás da Degradação")
        self.clock = pygame.time.Clock()
        self.virtual_surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        
        self.renderer = ScenarioRenderer()
        self.reset_data()
        
        self.btn_start = Button((VIRTUAL_WIDTH//2-140, 420, 280, 50), "INICIAR", COLOR_ACCENT_GOLD, text_color=(0,0,0), font_size=18)
        self.btn_how = Button((VIRTUAL_WIDTH//2-140, 490, 280, 44), "COMO JOGAR")
        self.btn_cred = Button((VIRTUAL_WIDTH//2-140, 550, 280, 44), "CRÉDITOS")
        self.btn_decision = Button((VIRTUAL_WIDTH//2-150, 10, 300, 40), "TOMAR DECISÃO FINAL", COLOR_ACCENT_GREEN, text_color=(0,0,0))
        
        # HUD sem as Conexões e ajustado
        self.hud_btns = [
            Button((20, 20, 120, 35), "MOCHILA"),
            Button((150, 20, 120, 35), "DESAFIOS")
        ]

    def reset_data(self):
        self.state = "TITLE"
        self.gamif = Gamification()
        self.items = create_interactables()
        self.active_modal = None
        self.active_item = None
        self.chosen_decision = None

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            time_sec = pygame.time.get_ticks() / 1000.0
            mouse_pos = self.get_mouse_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                self.handle_event(event, mouse_pos)
                
            self.update_logic(dt)
            self.draw_all(time_sec, mouse_pos)
            
            win_w, win_h = self.screen.get_size()
            self.screen.blit(pygame.transform.smoothscale(self.virtual_surf, (win_w, win_h)), (0, 0))
            pygame.display.flip()

    def get_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()
        sw, sh = self.screen.get_size()
        return (int(mx * VIRTUAL_WIDTH / max(1, sw)), int(my * VIRTUAL_HEIGHT / max(1, sh)))

    def handle_event(self, event, mouse_pos):
        if self.state == "TITLE":
            if self.btn_start.clicked(event, mouse_pos): self.state = "INVESTIGATION"
            if self.btn_how.clicked(event, mouse_pos): self.state = "HOW"
            if self.btn_cred.clicked(event, mouse_pos): self.state = "CREDITS"
        elif self.state in ["HOW", "CREDITS"]:
            if event.type == pygame.MOUSEBUTTONDOWN: self.state = "TITLE"
        elif self.state == "INVESTIGATION":
            if self.active_modal:
                res = self.active_modal.handle_event(event, mouse_pos)
                if res == "CLOSE": self.active_modal = None
            elif self.active_item:
                if event.type == pygame.MOUSEBUTTONDOWN: self.active_item = None # Fecha modal de inspeção com clique
            else:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # HUD
                    if self.hud_btns[0].rect.collidepoint(mouse_pos): self.active_modal = BackpackUI(self)
                    elif self.hud_btns[1].rect.collidepoint(mouse_pos): 
                        self.active_modal = Challenge1(self) if random.random() > 0.5 else Challenge2(self)
                    # Tomar Decisão
                    elif self.get_ev_count() == 6 and self.btn_decision.rect.collidepoint(mouse_pos):
                        self.state = "DECISION"
                    else:
                        # Items
                        for item in reversed(self.items):
                            if item.rect.collidepoint(mouse_pos):
                                self.active_item = item
                                self.inspect_item(item)
                                break
        elif self.state == "DECISION":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.state = "ENDING"
        elif self.state == "ENDING":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.reset_data()

    def inspect_item(self, item):
        if not item.inspected:
            item.inspected = True
            self.gamif.inspected_count += 1
            if item.type == "EVIDENCE": self.gamif.add_xp(100, "Evidência Principal Encontrada")
            elif item.type == "SECONDARY": self.gamif.add_xp(40, "Informação Descoberta")
            elif item.type == "CURIOSITY": self.gamif.add_xp(20, "Curiosidade Encontrada")
            elif item.type == "FLAVOR": self.gamif.add_xp(5, "Exploração")
            
            # Checa conquistas
            if self.gamif.inspected_count == 1: self.gamif.unlock_achievement("a_first")
            if self.gamif.inspected_count == 10: self.gamif.unlock_achievement("a_10")
            if self.gamif.inspected_count == 20: self.gamif.unlock_achievement("a_20")
            if self.get_ev_count() == 6: self.gamif.unlock_achievement("a_all_ev")

    def get_ev_count(self):
        return sum(1 for i in self.items if i.type == "EVIDENCE" and i.inspected)

    def update_logic(self, dt):
        self.gamif.update_notifications(dt)

    def draw_all(self, time_sec, mouse_pos):
        surf = self.virtual_surf
        if self.state == "TITLE":
            surf.blit(self.renderer.bg_surf, (0,0))
            overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10,15,22,210))
            surf.blit(overlay, (0,0))
            ts = FontManager.get(44, True).render("DETETIVES AMBIENTAIS", True, COLOR_ACCENT_GOLD)
            surf.blit(ts, ((VIRTUAL_WIDTH-ts.get_width())//2, 160))
            self.btn_start.draw(surf, mouse_pos)
            self.btn_how.draw(surf, mouse_pos)
            self.btn_cred.draw(surf, mouse_pos)
            
        elif self.state == "HOW":
            surf.fill(COLOR_BG_DARK)
            r = pygame.Rect(200, 100, 880, 500)
            UIUtils.draw_rounded_rect(surf, r, COLOR_PANEL_BG, border_width=2, border_color=COLOR_ACCENT_GOLD)
            UIUtils.draw_text(surf, "COMO JOGAR\n\nO cenário inteiro está visível. Passe o mouse para encontrar objetos e pessoas.\nExistem evidências, informações secundárias e curiosidades.\nGanhe XP e suba de nível, mas acima de tudo, encontre as 6 evidências \nprincipais para formar a acusação.\n\nClique para voltar.", 
                              pygame.Rect(250, 150, 780, 400), FontManager.get(18), COLOR_TEXT_LIGHT, line_spacing=10)
                              
        elif self.state == "CREDITS":
            surf.fill(COLOR_BG_DARK)
            r = pygame.Rect(200, 50, 880, 600)
            UIUtils.draw_rounded_rect(surf, r, COLOR_PANEL_BG, border_width=2, border_color=COLOR_ACCENT_GOLD)
            ctext = ("DETETIVES AMBIENTAIS: POR TRÁS DA DEGRADAÇÃO\n\nDesenvolvimento:\n- Douglas Oliveira de Jesus\n- Antonio Vitor Costa da Silva\n\n"
                     "Atividade acadêmica:\nAtividade avaliativa da segunda unidade da disciplina BIO 606 – Educação Ambiental (2026.2).\n"
                     "Docente:\nProfa. Viviane Souza Martins.\n\nTecnologia:\nPython 3 e Pygame.\n\n"
                     "Uso de inteligência artificial:\nIA generativa (Gemini) utilizada parcialmente como ferramenta de apoio à codificação do jogo.\n\n"
                     "Abordagem pedagógica:\nEducação Ambiental Crítica e Justiça Socioambiental.\n\n(Clique para voltar)")
            UIUtils.draw_text(surf, ctext, pygame.Rect(250, 80, 780, 500), FontManager.get(16), COLOR_TEXT_LIGHT, line_spacing=6)

        elif self.state == "INVESTIGATION":
            surf.blit(self.renderer.bg_surf, (0,0))
            self.renderer.draw_dynamic(surf, time_sec)
            
            hovered = None
            if not self.active_modal and not self.active_item:
                for item in reversed(self.items):
                    if item.rect.collidepoint(mouse_pos):
                        hovered = item
                        break
            
            # Desenha interativos (Marca sutil se já inspecionado)
            for item in self.items:
                if item == hovered:
                    pygame.draw.rect(surf, COLOR_ACCENT_HOVER, item.rect, 2, 4)
                    UIUtils.draw_icon(surf, item.icon, (item.rect.centerx, item.rect.y-15), 20, COLOR_ACCENT_GOLD)
                    # Tooltip
                    ts = FontManager.get(12, True).render(item.name, True, (0,0,0))
                    t_rect = ts.get_rect(center=(item.rect.centerx, item.rect.y-35))
                    pygame.draw.rect(surf, COLOR_ACCENT_HOVER, t_rect.inflate(10,6), border_radius=3)
                    surf.blit(ts, t_rect)
                elif item.inspected:
                    # Marca bem sutil para itens já vistos
                    pygame.draw.circle(surf, COLOR_ACCENT_CYAN, (item.rect.centerx, item.rect.bottom-5), 3)

            self.draw_hud(surf, mouse_pos)
            self.draw_notifications(surf)

            if self.get_ev_count() == 6:
                self.btn_decision.draw(surf, mouse_pos)

            if self.active_item:
                self.draw_inspection_modal(surf, self.active_item)
            elif self.active_modal:
                self.active_modal.draw(surf, mouse_pos)

        elif self.state == "DECISION":
            surf.fill(COLOR_BG_DARK)
            UIUtils.draw_text(surf, "TOMADA DE DECISÃO\n(Comunidade Mobilizada para exigir reparação e mudança estrutural.)\n\nClique para ver o desfecho.", 
                              pygame.Rect(200, 300, 880, 200), FontManager.get(20), COLOR_TEXT_LIGHT, center=True)
        elif self.state == "ENDING":
            surf.fill(COLOR_BG_DARK)
            UIUtils.draw_text(surf, "FIM DA INVESTIGAÇÃO\n\nVocê conectou os fatos e expôs o problema estrutural.\nA justiça ambiental exige participação coletiva.\n\nClique para reiniciar.", 
                              pygame.Rect(200, 300, 880, 200), FontManager.get(20), COLOR_ACCENT_GREEN, center=True)

    def draw_hud(self, surf, mouse_pos):
        # Top Bar Background
        pygame.draw.rect(surf, (20,28,36, 230), (0,0, VIRTUAL_WIDTH, 65))
        pygame.draw.line(surf, COLOR_PANEL_BORDER, (0,65), (VIRTUAL_WIDTH, 65), 2)
        
        for b in self.hud_btns: b.draw(surf, mouse_pos)
        
        # Level & XP (Posicionado dinamicamente após os botões)
        lx = 300
        ts = FontManager.get(14, True).render(f"NÍVEL {self.gamif.level}: {self.gamif.level_names[self.gamif.level-1]}", True, COLOR_ACCENT_GOLD)
        surf.blit(ts, (lx, 15))
        pygame.draw.rect(surf, (40,50,60), (lx, 35, 200, 10), border_radius=5)
        pygame.draw.rect(surf, COLOR_ACCENT_CYAN, (lx, 35, int(200 * self.gamif.get_level_progress()), 10), border_radius=5)
        
        # Progresso Principal
        ev_count = self.get_ev_count()
        ev_color = COLOR_ACCENT_GREEN if ev_count == 6 else COLOR_TEXT_LIGHT
        ts = FontManager.get(14, True).render(f"EVIDÊNCIAS: {ev_count}/6", True, ev_color)
        surf.blit(ts, (lx+250, 25))

    def draw_notifications(self, surf):
        y = 80
        for n in self.gamif.notifications:
            ts = FontManager.get(14, True).render(n["text"], True, n["color"])
            r = ts.get_rect(topright=(VIRTUAL_WIDTH-20, y))
            pygame.draw.rect(surf, (20,28,36,200), r.inflate(20,10), border_radius=4)
            surf.blit(ts, r)
            y += 40

    def draw_inspection_modal(self, surf, item):
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5,8,12, 180))
        surf.blit(overlay, (0,0))
        
        r = pygame.Rect((VIRTUAL_WIDTH-700)//2, 150, 700, 400)
        UIUtils.draw_rounded_rect(surf, r, COLOR_PANEL_BG, 12, 2, COLOR_ACCENT_GOLD)
        
        type_str = {"EVIDENCE":"EVIDÊNCIA PRINCIPAL", "SECONDARY":"INFORMAÇÃO SECUNDÁRIA", "CURIOSITY":"CURIOSIDADE LOCAL", "FLAVOR":"OBSERVAÇÃO"}[item.type]
        UIUtils.draw_text(surf, f"{type_str} (+XP)", pygame.Rect(r.x+30, r.y+20, 600, 20), FontManager.get(12, True), COLOR_ACCENT_GREEN)
        UIUtils.draw_text(surf, item.name, pygame.Rect(r.x+30, r.y+40, 640, 40), FontManager.get(22, True), COLOR_TEXT_LIGHT)
        pygame.draw.line(surf, COLOR_PANEL_BORDER, (r.x+30, r.y+80), (r.right-30, r.y+80))
        
        if item.text:
            UIUtils.draw_text(surf, item.text, pygame.Rect(r.x+30, r.y+100, 640, 250), FontManager.get(16), COLOR_TEXT_MUTED, line_spacing=6)
        elif item.dialogues:
            dy = r.y+100
            for d in item.dialogues:
                UIUtils.draw_text(surf, f"P: {d.question}", pygame.Rect(r.x+30, dy, 640, 20), FontManager.get(14, True), COLOR_ACCENT_CYAN)
                dy += 25
                UIUtils.draw_text(surf, f"R: {d.answer}", pygame.Rect(r.x+30, dy, 640, 50), FontManager.get(14), COLOR_TEXT_MUTED)
                dy += 55

        UIUtils.draw_text(surf, "(Clique para fechar)", pygame.Rect(r.x, r.bottom-30, r.width, 20), FontManager.get(12), (100,100,100), center=True)

if __name__ == "__main__":
    Game().run()