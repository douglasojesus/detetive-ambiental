# ==============================================================================
# DETETIVES AMBIENTAIS: POR TRÁS DA DEGRADAÇÃO
# Jogo educativo 2D de investigação socioambiental em Pygame.
#
# REQUISITOS: Python 3.10+ e pygame-ce (pip install -r requirements.txt)
# EXECUÇÃO:   python main.py   (rode dentro da pasta do projeto)
#             Passo a passo completo, inclusive para Windows, no README.md.
#
# Organização do código (pasta jogo/):
#   config.py   -> tamanho da tela, cores e balanceamento (dias, ações, finais)
#   conteudo.py -> TODOS os textos: objetos, diálogos, audiência e finais
#   modelos.py  -> estruturas de dados do conteúdo
#   estado.py   -> regras: tempo, pistas, confiança, evidências, XP
#   cenario.py  -> desenho da vila, das pessoas e do ciclo dia/noite
#   ui.py       -> mochila, conversas, inspeção e desafios
#   final.py    -> audiência pública, dossiê e os 5 finais
#   jogo.py     -> loop principal, HUD e máquina de estados
# ==============================================================================
from jogo.jogo import Game

if __name__ == "__main__":
    Game().run()
