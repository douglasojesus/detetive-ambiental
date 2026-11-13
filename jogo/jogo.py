# ==============================================================================
# CLASSE PRINCIPAL: LOOP, MÁQUINA DE ESTADOS, HUD E INTERAÇÃO COM O CENÁRIO
#
# Estados: TITLE, HOW, CREDITS, INTRO, INVESTIGATION, TRANSICAO,
#          AUDIENCIA, DOSSIE, FINAL
# ==============================================================================
import sys

import pygame

from . import config as C
from .cenario import HOTSPOTS, ScenarioRenderer, rect_npc
from .conteudo import COMO_JOGAR, CREDITOS, INTRO, NPCS
from .estado import Estado
from .final import AudienciaUI, DossieUI, FinalUI, calcular_final
from .graficos import Button, FontManager, UIUtils, alpha_rect, is_left_click
from .modelos import DIA, NOITE
from .ui import DESAFIOS, BackpackUI, DesafiosMenu, DialogoUI, InspecaoModal


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((C.VIRTUAL_WIDTH, C.VIRTUAL_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Detetives Ambientais: Por Trás da Degradação")
        self.clock = pygame.time.Clock()
        self.virtual_surf = pygame.Surface((C.VIRTUAL_WIDTH, C.VIRTUAL_HEIGHT))
        self.renderer = ScenarioRenderer()
        self.finais_vistos = set()     # vale para a sessão inteira (várias partidas)

        cx = C.VIRTUAL_WIDTH // 2
        self.btn_start = Button((cx - 140, 400, 280, 50), "INICIAR", C.COLOR_ACCENT_GOLD, text_color=(0, 0, 0),
                                font_size=18)
        self.btn_how = Button((cx - 140, 466, 280, 44), "COMO JOGAR")
        self.btn_cred = Button((cx - 140, 522, 280, 44), "CRÉDITOS")
        self.btn_mochila = Button((14, 13, 110, 36), "MOCHILA", font_size=14)
        self.btn_desafios = Button((132, 13, 110, 36), "DESAFIOS", font_size=14)
        self.btn_tempo = Button((878, 13, 180, 36), "", font_size=13)
        self.btn_audiencia = Button((1066, 13, 200, 36), "CONVOCAR AUDIÊNCIA", C.COLOR_ACCENT_GREEN,
                                    text_color=(0, 0, 0), font_size=13)
        self._cursor_mao = False
        self.reset_data()

    def reset_data(self):
        self.state = "TITLE"
        self.estado = Estado()
        self.active_modal = None
        self.desafios = {}
        self.transicao = None
        self.audiencia = None
        self.dossie = None
        self.tela_final = None
        self.confirmar_tempo_ate = 0

    def desafio(self, did):
        """Desafios guardam o progresso durante a partida."""
        if did not in self.desafios:
            self.desafios[did] = DESAFIOS[did](self)
        return self.desafios[did]

    # ------------------------------------------------------------------ loop
    def run(self):
        while True:
            dt = self.clock.tick(C.FPS) / 1000.0
            t = pygame.time.get_ticks() / 1000.0
            mouse_pos = self.get_mouse_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_event(event, mouse_pos)
            self.estado.gamif.update_notifications(dt)
            if self.transicao:
                self.transicao["t"] += dt
            self.draw_all(t, mouse_pos)
            win_w, win_h = self.screen.get_size()
            if (win_w, win_h) == (C.VIRTUAL_WIDTH, C.VIRTUAL_HEIGHT):
                self.screen.blit(self.virtual_surf, (0, 0))
            else:
                self.screen.blit(pygame.transform.smoothscale(self.virtual_surf, (win_w, win_h)), (0, 0))
            pygame.display.flip()

    def get_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()
        sw, sh = self.screen.get_size()
        return int(mx * C.VIRTUAL_WIDTH / max(1, sw)), int(my * C.VIRTUAL_HEIGHT / max(1, sh))

    # ------------------------------------------------------------- cenário
    def rect_item(self, item):
        if item.npc:
            x, base = NPCS[item.npc].posicoes[self.estado.periodo]
            return rect_npc(x, base)
        return HOTSPOTS[item.ancora]

    def item_sob_mouse(self, mouse_pos):
        if mouse_pos[1] < C.HUD_HEIGHT:
            return None
        # pessoas têm prioridade sobre objetos
        presentes = sorted(self.estado.itens_presentes(), key=lambda i: 0 if i.npc else 1)
        for item in presentes:
            if self.rect_item(item).collidepoint(mouse_pos):
                return item
        return None

    def clicar_item(self, item):
        res = self.estado.examinar(item)
        if res.tipo == "DIALOGO":
            self.active_modal = DialogoUI(self, item.npc, res.custo)
        else:
            self.active_modal = InspecaoModal(res)

    def fechar_modal(self):
        self.active_modal = None
        if self.estado.acoes <= 0 and self.state == "INVESTIGATION":
            self.iniciar_transicao()

    def iniciar_transicao(self):
        e = self.estado
        evento = e.avancar_periodo()
        if evento == NOITE:
            texto = f"Anoitece em Vila das Águas.\n\nDia {e.dia} de {C.TOTAL_DIAS} — noite"
            sub = "Prefeitura, escola e mercadinho fecham. Mas algumas coisas só acontecem no escuro..."
        elif evento == DIA:
            texto = f"Amanhece.\n\nDia {e.dia} de {C.TOTAL_DIAS}"
            sub = "Falta pouco para a audiência pública." if e.dia == C.TOTAL_DIAS else "Um novo dia de investigação."
        else:
            texto = "O prazo acabou."
            sub = "A audiência pública começa hoje de manhã, com as provas que você reuniu."
        self.transicao = {"texto": texto, "sub": sub, "t": 0.0, "fim": evento == "FIM"}
        self.state = "TRANSICAO"

    def iniciar_audiencia(self):
        self.active_modal = None
        self.estado.gamif.notifications.clear()
        self.audiencia = AudienciaUI(self)
        self.state = "AUDIENCIA"

    # -------------------------------------------------------------- eventos
    def handle_event(self, event, mouse_pos):
        st = self.state
        if st == "TITLE":
            if self.btn_start.clicked(event, mouse_pos):
                self.state = "INTRO"
            elif self.btn_how.clicked(event, mouse_pos):
                self.state = "HOW"
            elif self.btn_cred.clicked(event, mouse_pos):
                self.state = "CREDITS"
        elif st in ("HOW", "CREDITS"):
            if is_left_click(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.state = "TITLE" if not self.tela_final else "FINAL"
        elif st == "INTRO":
            if is_left_click(event) or (event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE)):
                self.state = "INVESTIGATION"
        elif st == "INVESTIGATION":
            self._evento_investigacao(event, mouse_pos)
        elif st == "TRANSICAO":
            if self.transicao["t"] > 0.6 and (is_left_click(event) or event.type == pygame.KEYDOWN):
                fim = self.transicao["fim"]
                self.transicao = None
                if fim:
                    self.iniciar_audiencia()
                else:
                    self.state = "INVESTIGATION"
        elif st == "AUDIENCIA":
            if self.audiencia.handle_event(event, mouse_pos) == "DOSSIE":
                self.dossie = DossieUI(self)
                self.state = "DOSSIE"
        elif st == "DOSSIE":
            respostas = self.dossie.handle_event(event, mouse_pos)
            if respostas:
                e = self.estado
                fid = calcular_final(len(e.evidencias), self.audiencia.credibilidade, respostas, e.flags)
                if fid == "justica":
                    e.gamif.unlock("a_justica")
                self.finais_vistos.add(fid)
                self.tela_final = FinalUI(self, fid, self.audiencia.credibilidade, self.audiencia.acertos)
                self.state = "FINAL"
        elif st == "FINAL":
            acao = self.tela_final.handle_event(event, mouse_pos)
            if acao == "NOVO":
                self.reset_data()
            elif acao == "CREDITOS":
                self.state = "CREDITS"

    def _evento_investigacao(self, event, mouse_pos):
        if self.active_modal:
            res = self.active_modal.handle_event(event, mouse_pos)
            if res == "CLOSE":
                self.fechar_modal()
            elif isinstance(res, tuple) and res[0] == "OPEN":
                self.active_modal = res[1]
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            self.active_modal = BackpackUI(self)
            return
        if not is_left_click(event):
            return
        if self.btn_mochila.clicked(event, mouse_pos):
            self.active_modal = BackpackUI(self)
        elif self.btn_desafios.clicked(event, mouse_pos):
            self.active_modal = DesafiosMenu(self)
        elif self.btn_tempo.clicked(event, mouse_pos):
            agora = pygame.time.get_ticks()
            if self.estado.acoes > 0 and agora > self.confirmar_tempo_ate:
                self.confirmar_tempo_ate = agora + 3000   # pede um segundo clique
            else:
                self.confirmar_tempo_ate = 0
                self.iniciar_transicao()
        elif len(self.estado.evidencias) == 6 and self.btn_audiencia.clicked(event, mouse_pos):
            self.iniciar_audiencia()
        else:
            item = self.item_sob_mouse(mouse_pos)
            if item:
                self.clicar_item(item)

    # -------------------------------------------------------------- desenho
    def draw_all(self, t, mouse_pos):
        surf = self.virtual_surf
        st = self.state
        mao = False
        if st == "TITLE":
            surf.blit(self.renderer.bg_surf, (0, 0))
            alpha_rect(surf, (10, 15, 22, 200), (0, 0, C.VIRTUAL_WIDTH, C.VIRTUAL_HEIGHT))
            ts = FontManager.get(52, True).render("DETETIVES AMBIENTAIS", True, C.COLOR_ACCENT_GOLD)
            surf.blit(ts, ts.get_rect(center=(C.VIRTUAL_WIDTH // 2, 210)))
            ts = FontManager.get(24).render("Por Trás da Degradação", True, C.COLOR_TEXT_LIGHT)
            surf.blit(ts, ts.get_rect(center=(C.VIRTUAL_WIDTH // 2, 265)))
            ts = FontManager.get(15).render("Uma investigação socioambiental em Vila das Águas", True, C.COLOR_TEXT_MUTED)
            surf.blit(ts, ts.get_rect(center=(C.VIRTUAL_WIDTH // 2, 300)))
            for b in (self.btn_start, self.btn_how, self.btn_cred):
                b.draw(surf, mouse_pos)
            if self.finais_vistos:
                ts = FontManager.get(14).render(f"Finais descobertos nesta sessão: {len(self.finais_vistos)}/5", True,
                                                C.COLOR_TEXT_MUTED)
                surf.blit(ts, ts.get_rect(center=(C.VIRTUAL_WIDTH // 2, 600)))
        elif st in ("HOW", "CREDITS", "INTRO"):
            surf.fill(C.COLOR_BG_DARK)
            r = pygame.Rect(160, 40, 960, 640)
            UIUtils.draw_rounded_rect(surf, r, C.COLOR_PANEL_BG, border_width=2, border_color=C.COLOR_ACCENT_GOLD)
            texto = {"HOW": COMO_JOGAR, "CREDITS": CREDITOS, "INTRO": INTRO}[st]
            tam = 17 if st != "INTRO" else 21
            UIUtils.draw_text(surf, texto, r.inflate(-90, -70), FontManager.get(tam), C.COLOR_TEXT_LIGHT,
                              line_spacing=6 if st != "INTRO" else 10)
        elif st in ("INVESTIGATION", "TRANSICAO"):
            mao = self._draw_investigacao(surf, t, mouse_pos)
            if st == "TRANSICAO":
                self._draw_transicao(surf)
        elif st == "AUDIENCIA":
            self.audiencia.draw(surf, mouse_pos, t)
            self.draw_notifications(surf, modo="embaixo")
        elif st == "DOSSIE":
            self.dossie.draw(surf, mouse_pos, t)
        elif st == "FINAL":
            self.tela_final.draw(surf, mouse_pos, t)
            self.draw_notifications(surf, modo="embaixo")
        if mao != self._cursor_mao:
            self._cursor_mao = mao
            try:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if mao else pygame.SYSTEM_CURSOR_ARROW)
            except pygame.error:
                pass

    def _draw_investigacao(self, surf, t, mouse_pos):
        e = self.estado
        self.renderer.desenhar(surf, e, t)
        hovered = None
        if not self.active_modal and self.state == "INVESTIGATION":
            hovered = self.item_sob_mouse(mouse_pos)
        # marcas discretas em itens já examinados
        for item in e.itens_presentes():
            if item is hovered:
                continue
            visto = item.id in e.vistos
            if visto:
                r = self.rect_item(item)
                pygame.draw.circle(surf, C.COLOR_ACCENT_CYAN, (r.centerx, r.bottom - 3), 3)
        if hovered:
            self._draw_tooltip(surf, hovered)
        self.draw_hud(surf, mouse_pos)
        if self.active_modal:
            self.active_modal.draw(surf, mouse_pos)
            self.draw_notifications(surf, modo="hud")
        else:
            self.draw_notifications(surf)
        return hovered is not None

    def _draw_tooltip(self, surf, item):
        e = self.estado
        r = self.rect_item(item)
        pygame.draw.rect(surf, C.COLOR_ACCENT_HOVER, r.inflate(4, 4), 2, 4)
        nome = item.nome
        custo = e.custo(item)
        bloqueado = e.periodo not in item.periodos or any(f not in e.flags for f in item.requer)
        if e.periodo not in item.periodos:
            info = "fechado / indisponível neste horário"
        elif bloqueado:
            info = "você precisa de uma pista"
        elif custo:
            info = f"{custo} ação"
        else:
            info = "grátis" if item.id not in e.vistos else "já examinado"
        f1, f2 = FontManager.get(13, True), FontManager.get(11)
        t1 = f1.render(nome, True, (0, 0, 0))
        t2 = f2.render(info, True, (60, 40, 0))
        w = max(t1.get_width(), t2.get_width()) + 34
        box = pygame.Rect(0, 0, w, 38)
        box.midbottom = (r.centerx, r.y - 6)
        box.clamp_ip(pygame.Rect(4, C.HUD_HEIGHT + 4, C.VIRTUAL_WIDTH - 8, C.VIRTUAL_HEIGHT - 8))
        if box.colliderect(r):
            box.top = r.bottom + 6
            box.clamp_ip(pygame.Rect(4, C.HUD_HEIGHT + 4, C.VIRTUAL_WIDTH - 8, C.VIRTUAL_HEIGHT - 8))
        pygame.draw.rect(surf, C.COLOR_ACCENT_HOVER, box, border_radius=4)
        UIUtils.draw_icon(surf, "lock" if bloqueado else item.icone, (box.x + 14, box.centery), 16, (60, 40, 0))
        surf.blit(t1, (box.x + 26, box.y + 4))
        surf.blit(t2, (box.x + 26, box.y + 21))

    def _draw_transicao(self, surf):
        tr = self.transicao
        a = min(235, int(tr["t"] * 500))
        alpha_rect(surf, (6, 10, 20, a), (0, 0, C.VIRTUAL_WIDTH, C.VIRTUAL_HEIGHT))
        if tr["t"] > 0.3:
            UIUtils.draw_text(surf, tr["texto"], pygame.Rect(0, 250, C.VIRTUAL_WIDTH, 120), FontManager.get(30, True),
                              C.COLOR_ACCENT_GOLD, center=True)
            UIUtils.draw_text(surf, tr["sub"], pygame.Rect(240, 390, C.VIRTUAL_WIDTH - 480, 60), FontManager.get(18),
                              C.COLOR_TEXT_LIGHT, center=True)
        if tr["t"] > 0.6:
            UIUtils.draw_text(surf, "(Clique para continuar)", pygame.Rect(0, 480, C.VIRTUAL_WIDTH, 30),
                              FontManager.get(14), C.COLOR_TEXT_MUTED, center=True)

    def draw_hud(self, surf, mouse_pos):
        e = self.estado
        g = e.gamif
        alpha_rect(surf, (16, 22, 30, 225), (0, 0, C.VIRTUAL_WIDTH, C.HUD_HEIGHT))
        pygame.draw.line(surf, C.COLOR_PANEL_BORDER, (0, C.HUD_HEIGHT), (C.VIRTUAL_WIDTH, C.HUD_HEIGHT), 2)
        self.btn_mochila.draw(surf, mouse_pos)
        self.btn_desafios.draw(surf, mouse_pos)
        # nível
        lx = 262
        ts = FontManager.get(13, True).render(f"NÍVEL {g.level}: {g.level_names[g.level - 1]}", True, C.COLOR_ACCENT_GOLD)
        surf.blit(ts, (lx, 12))
        pygame.draw.rect(surf, (40, 50, 60), (lx, 34, 180, 9), border_radius=5)
        pygame.draw.rect(surf, C.COLOR_ACCENT_CYAN, (lx, 34, int(180 * g.get_level_progress()), 9), border_radius=5)
        # evidências
        n = len(e.evidencias)
        ts = FontManager.get(13, True).render(f"EVIDÊNCIAS: {n}/6", True,
                                              C.COLOR_ACCENT_GREEN if n == 6 else C.COLOR_TEXT_LIGHT)
        surf.blit(ts, (466, 12))
        for i in range(6):
            pygame.draw.rect(surf, C.COLOR_ACCENT_GOLD if i < n else (50, 60, 70), (466 + i * 19, 34, 15, 9),
                             border_radius=3)
        # tempo
        tx = 610
        noite = e.periodo == NOITE
        UIUtils.draw_icon(surf, "moon" if noite else "sun", (tx + 12, 31), 22,
                          (200, 210, 255) if noite else C.COLOR_ACCENT_GOLD)
        ts = FontManager.get(13, True).render(f"DIA {e.dia}/{C.TOTAL_DIAS} — {'NOITE' if noite else 'DIA'}", True,
                                              C.COLOR_TEXT_LIGHT)
        surf.blit(ts, (tx + 30, 12))
        surf.blit(FontManager.get(12).render("Ações:", True, C.COLOR_TEXT_MUTED), (tx + 30, 33))
        for i in range(e.acoes_max):
            cor = C.COLOR_ACCENT_CYAN if i < e.acoes else (50, 60, 70)
            pygame.draw.circle(surf, cor, (tx + 82 + i * 16, 41), 6)
        # botões de tempo e audiência
        if pygame.time.get_ticks() < self.confirmar_tempo_ate:
            self.btn_tempo.text = f"CONFIRMAR? ({e.acoes} ações sobrando)"
        elif noite:
            self.btn_tempo.text = "DORMIR (PRÓX. DIA)" if e.dia < C.TOTAL_DIAS else "IR À AUDIÊNCIA"
        else:
            self.btn_tempo.text = "ESPERAR A NOITE"
        self.btn_tempo.draw(surf, mouse_pos)
        if n == 6:
            self.btn_audiencia.draw(surf, mouse_pos)
        else:
            ts = FontManager.get(11).render("Audiência: reúna as 6 evidências", True, C.COLOR_TEXT_MUTED)
            surf.blit(ts, ts.get_rect(center=self.btn_audiencia.rect.center))

    def draw_notifications(self, surf, modo="topo"):
        """Notificações: 'topo' (abaixo do HUD), 'hud' (sobre o HUD, com janela aberta)
        ou 'embaixo' (só conquistas, acima dos botões das telas cheias)."""
        notifs = self.estado.gamif.notifications
        if modo == "embaixo":
            notifs = [n for n in notifs if n["icon"] == "trophy"][-3:]
            y = 600 - 36 * len(notifs)
        elif modo == "hud":
            notifs = notifs[-1:]
            y = 18
        else:
            y = C.HUD_HEIGHT + 12
        for n in notifs:
            ts = FontManager.get(14, True).render(n["text"], True, n["color"])
            pad = 26 if n["icon"] else 0
            r = ts.get_rect(topright=(C.VIRTUAL_WIDTH - 20, y))
            caixa = r.inflate(20 + pad, 12)
            caixa.right = C.VIRTUAL_WIDTH - 10
            alpha = min(220, int(n["time"] * 300))
            alpha_rect(surf, (16, 22, 30, alpha), caixa, radius=5)
            if n["icon"]:
                UIUtils.draw_icon(surf, n["icon"], (caixa.x + 16, caixa.centery), 16, n["color"])
            surf.blit(ts, (caixa.x + 10 + pad, r.y))
            y += 36
