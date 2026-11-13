# ==============================================================================
# CONFIGURAÇÕES GERAIS, PALETA E BALANCEAMENTO
# Ajuste aqui a duração da investigação, custos e limiares dos finais.
# ==============================================================================

VIRTUAL_WIDTH = 1280
VIRTUAL_HEIGHT = 720
FPS = 60
HUD_HEIGHT = 62

# --- Paleta da interface ---
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

# --- Tempo da investigação ---
TOTAL_DIAS = 3            # a audiência pública acontece na manhã do dia seguinte
ACOES_DIA = 5             # ações disponíveis durante o dia
ACOES_NOITE = 3           # ações disponíveis à noite

# Custo (em ações) para examinar algo pela primeira vez. Rever é sempre grátis.
CUSTO_POR_TIPO = {
    "EVIDENCE": 1,
    "SECONDARY": 1,
    "CURIOSITY": 1,
    "FLAVOR": 0,
}

# --- XP por tipo de descoberta ---
XP_POR_TIPO = {
    "EVIDENCE": 100,
    "SECONDARY": 40,
    "CURIOSITY": 20,
    "FLAVOR": 5,
}
XP_DESAFIO = 100

# --- Confiança necessária com o trabalhador ---
CONFIANCA_DEPOIMENTO = 2   # para ele contar sobre os despejos (evidência 4)
CONFIANCA_DOCUMENTO = 3    # para ele revelar onde está o memorando (evidência 1)

# --- Audiência pública ---
CRED_ACERTO = 2            # evidência que desmente a alegação
CRED_PARCIAL = 1           # informação secundária que ajuda, mas não prova
CRED_ERRO = -1             # registro que não tem relação com a alegação
CRED_BONUS_DESAFIO = 1     # cada desafio concluído = +1 de preparo
CRED_BONUS_ASSOCIACAO = 1  # Associação presente na audiência

CRED_MINIMA = 4            # abaixo disso o caso é arquivado
CRED_ALTA = 10             # necessário para o final de Justiça Socioambiental
EVID_MINIMAS = 4           # menos que isso: caso arquivado
