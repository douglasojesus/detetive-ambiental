"""
Gera imagens das telas do jogo sem abrir janela e verifica o layout do cenário.

Uso:  python scripts/renderizar_cena.py
Saída: scripts/saida/*.png  (pasta ignorada pelo git)

Verificações automáticas:
  - nenhuma área clicável se sobrepõe a outra no mesmo período;
  - o pé de cada pessoa não fica dentro de um prédio, na água ou fora da tela;
  - toda área clicável fica abaixo do HUD e dentro da tela.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame  # noqa: E402

from jogo import config as C  # noqa: E402
from jogo.cenario import HOTSPOTS, PREDIOS, ponto_no_rio  # noqa: E402
from jogo.conteudo import NPCS  # noqa: E402
from jogo.modelos import DIA, NOITE  # noqa: E402

SAIDA = os.path.join(os.path.dirname(__file__), "saida")
CORES = {"EVIDENCE": (255, 60, 60), "SECONDARY": (60, 200, 255), "CURIOSITY": (255, 220, 60), "FLAVOR": (230, 230, 230)}


def verificar_layout(game):
    erros = []
    tela = pygame.Rect(0, C.HUD_HEIGHT, C.VIRTUAL_WIDTH, C.VIRTUAL_HEIGHT - C.HUD_HEIGHT)
    for periodo in (DIA, NOITE):
        game.estado.periodo = periodo
        itens = game.estado.itens_presentes()
        rects = [(i, game.rect_item(i)) for i in itens]
        for a in range(len(rects)):
            ia, ra = rects[a]
            if not tela.contains(ra):
                erros.append(f"[{periodo}] {ia.id} sai da tela ou entra no HUD: {ra}")
            for b in range(a + 1, len(rects)):
                ib, rb = rects[b]
                if ra.colliderect(rb):
                    erros.append(f"[{periodo}] sobreposição: {ia.id} {ra} x {ib.id} {rb}")
        for npc in NPCS.values():
            if periodo not in npc.posicoes:
                continue
            x, base = npc.posicoes[periodo]
            for nome, pr in PREDIOS.items():
                if pr.collidepoint(x, base - 1):
                    erros.append(f"[{periodo}] {npc.id} está com o pé dentro do prédio {nome}")
            if ponto_no_rio(x, base):
                erros.append(f"[{periodo}] {npc.id} está dentro do rio")
    game.estado.periodo = DIA
    for chave in HOTSPOTS:
        if chave not in {i.ancora for i in game.estado.itens}:
            erros.append(f"hotspot sem item: {chave}")
    return erros


def salvar(game, nome):
    pygame.image.save(game.virtual_surf, os.path.join(SAIDA, nome))


def main():
    os.makedirs(SAIDA, exist_ok=True)
    from jogo.jogo import Game
    from jogo.ui import BackpackUI, DialogoUI, DesafiosMenu
    from jogo.final import AudienciaUI, DossieUI, FinalUI

    g = Game()
    erros = verificar_layout(g)
    mouse = (0, 0)

    g.state = "TITLE"; g.draw_all(1.0, mouse); salvar(g, "00_titulo.png")
    g.state = "HOW"; g.draw_all(1.0, mouse); salvar(g, "01_como_jogar.png")
    g.state = "INVESTIGATION"
    for periodo in (DIA, NOITE):
        g.estado.periodo = periodo
        g.draw_all(1.0, mouse)
        salvar(g, f"10_cena_{periodo.lower()}.png")
        for item in g.estado.itens_presentes():
            r = g.rect_item(item)
            pygame.draw.rect(g.virtual_surf, CORES[item.tipo], r, 1)
            g.virtual_surf.blit(pygame.font.SysFont("arial", 10, True).render(item.id, True, CORES[item.tipo]),
                                (r.x, r.y - 11))
        salvar(g, f"11_areas_{periodo.lower()}.png")
    g.estado.periodo = DIA
    # hover num item
    r = g.rect_item(g.estado.por_id["ev5"])
    g.draw_all(1.0, r.center); salvar(g, "12_tooltip.png")
    # conversa
    g.estado.flags.add("sigilo_garantido")
    g.estado.periodo = NOITE
    g.active_modal = DialogoUI(g, "trabalhador")
    g.draw_all(1.0, mouse); salvar(g, "20_dialogo.png")
    g.estado.escolher("trabalhador", g.estado.escolhas_disponiveis("trabalhador")[1])
    g.active_modal = DialogoUI(g, "trabalhador")
    g.draw_all(1.0, mouse); salvar(g, "21_dialogo_confianca.png")
    g.estado.periodo = DIA
    for ev in ("ev2", "ev3", "ev5"):
        g.estado.registrar_evidencia(ev)
    g.estado.vistos.update({"sec1", "sec3", "sec8", "cur1"})
    g.active_modal = BackpackUI(g); g.active_modal.sel = "ev2"
    g.draw_all(1.0, mouse); salvar(g, "30_mochila.png")
    g.active_modal.tab = "OBJETIVOS"; g.draw_all(1.0, mouse); salvar(g, "31_objetivos.png")
    g.active_modal = DesafiosMenu(g); g.draw_all(1.0, mouse); salvar(g, "40_desafios.png")
    for did in ("linha", "discurso", "atores"):
        g.active_modal = g.desafio(did); g.draw_all(1.0, mouse); salvar(g, f"41_desafio_{did}.png")
    g.active_modal = None
    g.estado.flags.add("associacao_na_audiencia")
    g.iniciar_audiencia(); g.draw_all(1.0, mouse); salvar(g, "50_audiencia_intro.png")
    g.audiencia.fase = "ALEGACAO"; g.draw_all(1.0, mouse); salvar(g, "51_audiencia_alegacao.png")
    g.audiencia._responder("ev2", "Laudo"); g.draw_all(1.0, mouse); salvar(g, "52_audiencia_resposta.png")
    g.dossie = DossieUI(g); g.state = "DOSSIE"; g.dossie.q = 2; g.dossie.sel = "transicao"
    g.draw_all(1.0, mouse); salvar(g, "60_dossie.png")
    for fid in ("justica", "dividida"):
        g.finais_vistos.add(fid)
        g.tela_final = FinalUI(g, fid, 11, 5); g.state = "FINAL"
        g.draw_all(1.0, mouse); salvar(g, f"70_final_{fid}.png")
    g.tela_final.pagina = 1; g.draw_all(1.0, mouse); salvar(g, "71_reflexao.png")

    print(f"Imagens salvas em {SAIDA}")
    if erros:
        print("PROBLEMAS DE LAYOUT:")
        for e in erros:
            print("  -", e)
        sys.exit(1)
    print("Layout OK: nenhuma sobreposição de áreas clicáveis e nenhuma pessoa fora do chão.")


if __name__ == "__main__":
    main()
