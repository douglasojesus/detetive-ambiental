# ==============================================================================
# JANELAS DA INVESTIGAÇÃO: INSPEÇÃO, CONVERSA, MOCHILA E DESAFIOS
# Cada janela tem draw(surf, mouse_pos) e handle_event(event, mouse_pos), que
# retorna "KEEP", "CLOSE" ou ("OPEN", outra_janela).
# ==============================================================================
import random

import pygame

from . import config as C
from .cenario import retrato
from .conteudo import NPCS
from .graficos import Button, FontManager, UIUtils, alpha_rect, is_left_click


class UIWindow:
    def __init__(self, title, width=1000, height=600):
        self.rect = pygame.Rect((C.VIRTUAL_WIDTH - width) // 2, (C.VIRTUAL_HEIGHT - height) // 2 + 20, width, height)
        self.title = title
        self.btn_close = Button((self.rect.right - 120, self.rect.y + 15, 100, 35), "FECHAR", C.COLOR_ACCENT_RED,
                                font_size=14)

    def draw_base(self, surf, mouse_pos):
        alpha_rect(surf, (5, 10, 15, 200), (0, 0, C.VIRTUAL_WIDTH, C.VIRTUAL_HEIGHT))
        UIUtils.draw_rounded_rect(surf, self.rect, C.COLOR_PANEL_BG, radius=12, border_width=2,
                                  border_color=C.COLOR_PANEL_BORDER)
        ts = FontManager.get(24, True).render(self.title, True, C.COLOR_ACCENT_GOLD)
        surf.blit(ts, (self.rect.x + 30, self.rect.y + 20))
        pygame.draw.line(surf, C.COLOR_PANEL_BORDER, (self.rect.x, self.rect.y + 60),
                         (self.rect.right, self.rect.y + 60), 2)
        self.btn_close.draw(surf, mouse_pos)


# ------------------------------------------------------------------------------
# INSPEÇÃO DE OBJETOS
# ------------------------------------------------------------------------------
class InspecaoModal:
    TIPOS = {"EVIDENCE": "EVIDÊNCIA PRINCIPAL", "SECONDARY": "INFORMAÇÃO SECUNDÁRIA",
             "CURIOSITY": "CURIOSIDADE LOCAL", "FLAVOR": "OBSERVAÇÃO"}

    def __init__(self, resultado):
        self.res = resultado
        self.bloqueado = resultado.tipo == "BLOQUEADO"
        font = FontManager.get(16)
        h = UIUtils.text_height(resultado.texto, 640, font, line_spacing=6)
        self.rect = pygame.Rect((C.VIRTUAL_WIDTH - 700) // 2, 0, 700, min(560, 150 + h))
        self.rect.centery = C.VIRTUAL_HEIGHT // 2 + 25

    def draw(self, surf, mouse_pos):
        alpha_rect(surf, (5, 8, 12, 180), (0, 0, C.VIRTUAL_WIDTH, C.VIRTUAL_HEIGHT))
        r = self.rect
        borda = C.COLOR_TEXT_MUTED if self.bloqueado else C.COLOR_ACCENT_GOLD
        UIUtils.draw_rounded_rect(surf, r, C.COLOR_PANEL_BG, 12, 2, borda)
        item = self.res.item
        if self.bloqueado:
            UIUtils.draw_icon(surf, "lock", (r.x + 38, r.y + 30), 16, C.COLOR_TEXT_MUTED)
            tag, cor = "AINDA NÃO É POSSÍVEL EXAMINAR (nenhuma ação gasta)", C.COLOR_TEXT_MUTED
            UIUtils.draw_text(surf, tag, pygame.Rect(r.x + 52, r.y + 22, 600, 20), FontManager.get(12, True), cor)
        else:
            custo = f"   (-{self.res.custo} ação)" if self.res.custo else ""
            UIUtils.draw_text(surf, self.TIPOS[item.tipo] + custo, pygame.Rect(r.x + 30, r.y + 22, 600, 20),
                              FontManager.get(12, True), C.COLOR_ACCENT_GREEN)
        UIUtils.draw_text(surf, item.nome, pygame.Rect(r.x + 30, r.y + 42, 640, 40), FontManager.get(22, True),
                          C.COLOR_TEXT_LIGHT)
        pygame.draw.line(surf, C.COLOR_PANEL_BORDER, (r.x + 30, r.y + 80), (r.right - 30, r.y + 80))
        UIUtils.draw_text(surf, self.res.texto, pygame.Rect(r.x + 30, r.y + 96, 640, r.height - 130),
                          FontManager.get(16), C.COLOR_TEXT_LIGHT if not self.bloqueado else C.COLOR_TEXT_MUTED,
                          line_spacing=6)
        UIUtils.draw_text(surf, "(Clique para fechar)", pygame.Rect(r.x, r.bottom - 28, r.width, 20),
                          FontManager.get(12), (120, 130, 140), center=True)

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key in
                                                   (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE)):
            return "CLOSE"
        return "KEEP"


# ------------------------------------------------------------------------------
# CONVERSAS COM ESCOLHAS
# ------------------------------------------------------------------------------
class DialogoUI(UIWindow):
    def __init__(self, game, npc_id, custo=0):
        self.npc = NPCS[npc_id]
        super().__init__(f"CONVERSA: {self.npc.nome.upper()}", 1040, 620)
        self.game = game
        self.estado = game.estado
        self.npc_id = npc_id
        self.fala = self.npc.saudacao
        self.pergunta = ""
        self.retrato = retrato(self.npc, (180, 216))
        self.custo = custo
        self.encerrada = False
        self._montar_botoes()

    def _montar_botoes(self):
        self.botoes = []
        x, w = self.rect.x + 260, self.rect.width - 290
        y = self.rect.y + 262
        if not self.encerrada:
            for esc in self.estado.escolhas_disponiveis(self.npc_id):
                h = 44 if FontManager.get(14, True).size(esc.texto)[0] > w - 30 else 32
                b = Button((x, y, w, h), "> " + esc.texto, font_size=14, align="left")
                b.escolha = esc
                self.botoes.append(b)
                y += h + 5
        sair = Button((self.rect.right - 290, self.rect.bottom - 50, 260, 36), "ENCERRAR CONVERSA",
                      C.COLOR_PANEL_ALT, font_size=14)
        sair.escolha = None
        self.botoes.append(sair)

    def draw(self, surf, mouse_pos):
        self.draw_base(surf, mouse_pos)
        r = self.rect
        # retrato e identificação
        port = pygame.Rect(r.x + 30, r.y + 80, 200, 240)
        UIUtils.draw_rounded_rect(surf, port, (40, 55, 70), 10)
        surf.blit(self.retrato, (port.x + 10, port.y + 12))
        UIUtils.draw_text(surf, self.npc.nome, pygame.Rect(r.x + 30, r.y + 330, 200, 24), FontManager.get(18, True),
                          C.COLOR_ACCENT_GOLD)
        UIUtils.draw_text(surf, self.npc.papel, pygame.Rect(r.x + 30, r.y + 356, 200, 40), FontManager.get(13),
                          C.COLOR_TEXT_MUTED)
        if self.npc.mostra_confianca:
            conf = self.estado.confianca[self.npc_id]
            UIUtils.draw_text(surf, "CONFIANÇA", pygame.Rect(r.x + 30, r.y + 410, 200, 20), FontManager.get(12, True),
                              C.COLOR_TEXT_MUTED)
            for i in range(C.CONFIANCA_DOCUMENTO):
                cor = C.COLOR_ACCENT_GREEN if conf > i else (50, 60, 70)
                pygame.draw.rect(surf, cor, (r.x + 30 + i * 46, r.y + 432, 40, 12), border_radius=4)
            if conf < 0:
                UIUtils.draw_text(surf, "Desconfiado", pygame.Rect(r.x + 30, r.y + 450, 200, 20), FontManager.get(12),
                                  C.COLOR_ACCENT_RED)
        # balão de fala
        balao = pygame.Rect(r.x + 260, r.y + 80, r.width - 290, 170)
        UIUtils.draw_rounded_rect(surf, balao, C.COLOR_PANEL_ALT, 10, 1, C.COLOR_PANEL_BORDER)
        y = balao.y + 14
        if self.pergunta:
            y += UIUtils.draw_text(surf, "Você: " + self.pergunta, pygame.Rect(balao.x + 18, y, balao.width - 36, 60),
                                   FontManager.get(14, True), C.COLOR_ACCENT_CYAN) + 8
        UIUtils.draw_text(surf, self.fala, pygame.Rect(balao.x + 18, y, balao.width - 36, balao.bottom - y),
                          FontManager.get(16), C.COLOR_TEXT_LIGHT, line_spacing=5)
        if self.encerrada:
            UIUtils.draw_text(surf, "(Ele foi embora. Talvez em outra noite ele aceite conversar de novo.)",
                              pygame.Rect(r.x + 260, r.y + 270, r.width - 290, 40), FontManager.get(14),
                              C.COLOR_TEXT_MUTED)
        for b in self.botoes:
            b.draw(surf, mouse_pos)

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "CLOSE"
        if not is_left_click(event):
            return "KEEP"
        if self.btn_close.rect.collidepoint(mouse_pos):
            return "CLOSE"
        for b in self.botoes:
            if b.rect.collidepoint(mouse_pos):
                if b.escolha is None:
                    return "CLOSE"
                esc = self.estado.escolher(self.npc_id, b.escolha)
                self.pergunta = esc.texto
                self.fala = esc.resposta
                if esc.encerra:
                    self.encerrada = True
                self._montar_botoes()
                return "KEEP"
        return "KEEP"


# ------------------------------------------------------------------------------
# MOCHILA
# ------------------------------------------------------------------------------
class BackpackUI(UIWindow):
    TABS = [("EVIDENCE", "Evidências"), ("SECONDARY", "Informações"), ("CURIOSITY", "Curiosidades"),
            ("CONVERSAS", "Conversas"), ("OBJETIVOS", "Objetivos"), ("CONQUISTAS", "Conquistas")]

    def __init__(self, game):
        super().__init__("MOCHILA E REGISTROS", 1160, 620)
        self.game = game
        self.estado = game.estado
        self.tab = "EVIDENCE"
        self.sel = None
        self.scroll = 0

    def _entradas(self):
        """Lista de (chave, título, texto) da aba atual."""
        e = self.estado
        if self.tab == "EVIDENCE":
            return [(ev, *e.registro_evidencia(ev)) for ev in e.evidencias]
        if self.tab in ("SECONDARY", "CURIOSITY"):
            saida = []
            for it in e.itens:
                if it.tipo == self.tab and it.id in e.vistos:
                    if it.npc:
                        txt = self._transcricao(it.npc) or "(Você ainda não fez perguntas.)"
                    else:
                        txt = it.texto
                    saida.append((it.id, it.nome, txt))
            return saida
        if self.tab == "CONVERSAS":
            return [(n, NPCS[n].nome, self._transcricao(n) or "(Você ainda não fez perguntas.)")
                    for n in NPCS if n in e.conversados]
        return []

    def _transcricao(self, npc_id):
        return "\n\n".join(f"Você: {p}\n{NPCS[npc_id].nome}: {r}" for p, r in self.estado.transcricoes[npc_id])

    def _tab_rect(self, i):
        return pygame.Rect(self.rect.x + 30 + i * 180, self.rect.y + 70, 170, 34)

    def draw(self, surf, mouse_pos):
        self.draw_base(surf, mouse_pos)
        for i, (tid, nome) in enumerate(self.TABS):
            tr = self._tab_rect(i)
            ativo = self.tab == tid
            pygame.draw.rect(surf, C.COLOR_PANEL_ALT if ativo else C.COLOR_PANEL_BG, tr, border_radius=4)
            if ativo:
                pygame.draw.rect(surf, C.COLOR_ACCENT_GOLD, (tr.x, tr.bottom - 2, tr.width, 2))
            ts = FontManager.get(14, True).render(nome, True, C.COLOR_ACCENT_GOLD if ativo else C.COLOR_TEXT_MUTED)
            surf.blit(ts, ts.get_rect(center=tr.center))
        if self.tab == "OBJETIVOS":
            self._draw_objetivos(surf)
            return
        if self.tab == "CONQUISTAS":
            self._draw_conquistas(surf)
            return

        entradas = self._entradas()
        lista = pygame.Rect(self.rect.x + 30, self.rect.y + 118, 340, 476)
        pygame.draw.rect(surf, (20, 28, 36), lista, border_radius=6)
        if not entradas:
            UIUtils.draw_text(surf, "Nada registrado ainda.", lista.inflate(-30, -30), FontManager.get(14),
                              C.COLOR_TEXT_MUTED)
        for idx, (chave, titulo, _) in enumerate(entradas):
            r = pygame.Rect(lista.x + 5, lista.y + 5 + idx * 42, lista.width - 10, 38)
            sel = self.sel == chave
            hov = r.collidepoint(mouse_pos)
            pygame.draw.rect(surf, (45, 58, 70) if sel or hov else (25, 35, 45), r, border_radius=4)
            UIUtils.draw_text(surf, titulo, pygame.Rect(r.x + 10, r.y + 10, r.width - 20, 20), FontManager.get(13),
                              C.COLOR_ACCENT_GOLD if sel else C.COLOR_TEXT_LIGHT)

        det = pygame.Rect(self.rect.x + 390, self.rect.y + 118, self.rect.width - 420, 476)
        UIUtils.draw_rounded_rect(surf, det, C.COLOR_PANEL_ALT, radius=6, border_width=1,
                                  border_color=C.COLOR_PANEL_BORDER)
        atual = next((x for x in entradas if x[0] == self.sel), None)
        if not atual:
            UIUtils.draw_text(surf, "Selecione um registro na lista ao lado.", pygame.Rect(det.x, det.centery - 10,
                              det.width, 30), FontManager.get(16), C.COLOR_TEXT_MUTED, center=True)
            return
        UIUtils.draw_text(surf, atual[1], pygame.Rect(det.x + 20, det.y + 16, det.width - 40, 30),
                          FontManager.get(20, True), C.COLOR_ACCENT_GOLD)
        pygame.draw.line(surf, C.COLOR_PANEL_BORDER, (det.x + 20, det.y + 50), (det.right - 20, det.y + 50))
        area = pygame.Rect(det.x + 20, det.y + 60, det.width - 40, det.height - 70)
        font = FontManager.get(15)
        altura = UIUtils.text_height(atual[2], area.width - 10, font, 5)
        self.scroll = max(0, min(self.scroll, altura - area.height + 10))
        clip = surf.get_clip()
        surf.set_clip(area)
        UIUtils.draw_text(surf, atual[2], pygame.Rect(area.x, area.y - self.scroll, area.width - 10, altura + 20),
                          font, C.COLOR_TEXT_LIGHT, line_spacing=5)
        surf.set_clip(clip)
        if altura > area.height:
            barra_h = max(30, area.height * area.height // altura)
            barra_y = area.y + (area.height - barra_h) * self.scroll // max(1, altura - area.height)
            pygame.draw.rect(surf, C.COLOR_PANEL_BORDER, (det.right - 10, barra_y, 5, barra_h), border_radius=3)

    def _draw_objetivos(self, surf):
        principais, secundarios = self.estado.objetivos()
        y = self.rect.y + 130
        for titulo, lista in (("OBJETIVOS PRINCIPAIS", principais), ("OBJETIVOS SECUNDÁRIOS", secundarios)):
            surf.blit(FontManager.get(16, True).render(titulo, True, C.COLOR_ACCENT_GOLD), (self.rect.x + 50, y))
            y += 34
            for texto, feito in lista:
                cor = C.COLOR_ACCENT_GREEN if feito else C.COLOR_TEXT_MUTED
                pygame.draw.rect(surf, cor, (self.rect.x + 54, y + 2, 16, 16), 2, border_radius=3)
                if feito:
                    UIUtils.draw_icon(surf, "check", (self.rect.x + 61, y + 9), 12, cor)
                surf.blit(FontManager.get(15).render(texto, True, C.COLOR_TEXT_LIGHT if not feito else cor),
                          (self.rect.x + 84, y))
                y += 28
            y += 16
        e = self.estado
        resumo = (f"Dia {e.dia} de {C.TOTAL_DIAS}   •   Evidências: {len(e.evidencias)}/6   •   "
                  f"Registros examinados: {len(e.vistos)}   •   XP: {e.gamif.xp}")
        surf.blit(FontManager.get(14).render(resumo, True, C.COLOR_TEXT_MUTED), (self.rect.x + 50, self.rect.bottom - 40))

    def _draw_conquistas(self, surf):
        for i, a in enumerate(self.estado.gamif.achievements):
            col, row = i % 2, i // 2
            r = pygame.Rect(self.rect.x + 40 + col * 545, self.rect.y + 125 + row * 80, 530, 70)
            UIUtils.draw_rounded_rect(surf, r, C.COLOR_PANEL_ALT if a.unlocked else (28, 36, 44), 8, 1,
                                      C.COLOR_ACCENT_CYAN if a.unlocked else C.COLOR_PANEL_BORDER)
            cor = C.COLOR_ACCENT_CYAN if a.unlocked else (80, 95, 110)
            UIUtils.draw_icon(surf, "trophy" if a.unlocked else "lock", (r.x + 32, r.centery), 22, cor)
            surf.blit(FontManager.get(16, True).render(a.title, True, C.COLOR_TEXT_LIGHT if a.unlocked else cor),
                      (r.x + 60, r.y + 14))
            surf.blit(FontManager.get(13).render(a.desc, True, C.COLOR_TEXT_MUTED), (r.x + 60, r.y + 40))

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, self.scroll - event.y * 30)
            return "KEEP"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "CLOSE"
        if not is_left_click(event):
            return "KEEP"
        if self.btn_close.rect.collidepoint(mouse_pos):
            return "CLOSE"
        for i, (tid, _) in enumerate(self.TABS):
            if self._tab_rect(i).collidepoint(mouse_pos):
                self.tab, self.sel, self.scroll = tid, None, 0
                return "KEEP"
        lista_y = self.rect.y + 118
        for idx, (chave, _, _) in enumerate(self._entradas()):
            if pygame.Rect(self.rect.x + 35, lista_y + 5 + idx * 42, 330, 38).collidepoint(mouse_pos):
                self.sel, self.scroll = chave, 0
                return "KEEP"
        return "KEEP"


# ------------------------------------------------------------------------------
# DESAFIOS
# ------------------------------------------------------------------------------
class DesafiosMenu(UIWindow):
    INFO = [
        ("linha", "Linha do Tempo", "Organize os acontecimentos em ordem e entenda como o dano foi sendo produzido."),
        ("discurso", "Análise do Discurso", "Confronte a propaganda da empresa com as evidências que você reuniu."),
        ("atores", "Mapa de Atores", "Quem lucra, quem sofre, quem deveria fiscalizar e quem se organiza?"),
    ]

    def __init__(self, game):
        super().__init__("DESAFIOS DE INTERPRETAÇÃO", 860, 470)
        self.game = game
        self.botoes = []
        for i, (did, _, _) in enumerate(self.INFO):
            b = Button((self.rect.right - 200, self.rect.y + 100 + i * 110, 160, 40), "ABRIR", C.COLOR_ACCENT_GOLD,
                       text_color=(0, 0, 0), font_size=15)
            b.did = did
            self.botoes.append(b)

    def draw(self, surf, mouse_pos):
        self.draw_base(surf, mouse_pos)
        for i, (did, nome, desc) in enumerate(self.INFO):
            r = pygame.Rect(self.rect.x + 30, self.rect.y + 80, self.rect.width - 60, 90)
            r.y += i * 110
            ok = did in self.game.estado.desafios_ok
            UIUtils.draw_rounded_rect(surf, r, C.COLOR_PANEL_ALT, 8, 1, C.COLOR_ACCENT_GREEN if ok else C.COLOR_PANEL_BORDER)
            surf.blit(FontManager.get(18, True).render(nome, True, C.COLOR_TEXT_LIGHT), (r.x + 20, r.y + 14))
            UIUtils.draw_text(surf, desc, pygame.Rect(r.x + 20, r.y + 42, r.width - 260, 40), FontManager.get(14),
                              C.COLOR_TEXT_MUTED)
            status = "CONCLUÍDO" if ok else "PENDENTE"
            surf.blit(FontManager.get(12, True).render(status, True, C.COLOR_ACCENT_GREEN if ok else C.COLOR_TEXT_MUTED),
                      (r.right - 170, r.y + 64))
        for b in self.botoes:
            b.draw(surf, mouse_pos)
        UIUtils.draw_text(surf, "Desafios não gastam ações. Cada desafio concluído dá +1 de preparo na audiência.",
                          pygame.Rect(self.rect.x, self.rect.bottom - 40, self.rect.width, 20), FontManager.get(13),
                          C.COLOR_TEXT_MUTED, center=True)

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "CLOSE"
        if not is_left_click(event):
            return "KEEP"
        if self.btn_close.rect.collidepoint(mouse_pos):
            return "CLOSE"
        for b in self.botoes:
            if b.rect.collidepoint(mouse_pos):
                return ("OPEN", self.game.desafio(b.did))
        return "KEEP"


class _DesafioBase(UIWindow):
    ID = ""

    def __init__(self, game, title, w, h):
        super().__init__(title, w, h)
        self.game = game
        self.btn_voltar = Button((self.rect.right - 240, self.rect.y + 15, 110, 35), "VOLTAR", font_size=14)

    @property
    def solved(self):
        return self.ID in self.game.estado.desafios_ok

    def draw_base(self, surf, mouse_pos):
        super().draw_base(surf, mouse_pos)
        self.btn_voltar.draw(surf, mouse_pos)

    def _navegacao(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "CLOSE"
        if not is_left_click(event):
            return "KEEP"
        if self.btn_close.rect.collidepoint(mouse_pos):
            return "CLOSE"
        if self.btn_voltar.rect.collidepoint(mouse_pos):
            return ("OPEN", DesafiosMenu(self.game))
        return None

    def _concluir(self):
        self.game.estado.concluir_desafio(self.ID)

    def _draw_concluido(self, surf, texto):
        UIUtils.draw_icon(surf, "check", (self.rect.centerx, self.rect.y + 130), 30, C.COLOR_ACCENT_GREEN)
        UIUtils.draw_text(surf, texto, pygame.Rect(self.rect.x + 60, self.rect.y + 170, self.rect.width - 120, 300),
                          FontManager.get(18, True), C.COLOR_ACCENT_GREEN, center=True, line_spacing=8)


class Challenge1(_DesafioBase):
    ID = "linha"
    EVENTOS = [
        "A Vila das Águas é fundada por pescadores artesanais (1952).",
        "A Vale das Pedras expande suas atividades industriais na região.",
        "A diretoria corta 65% do orçamento da estação de tratamento.",
        "Começam os despejos irregulares noturnos no rio.",
        "Peixes morrem e surgem problemas de pele na comunidade.",
        "O processo de fiscalização é engavetado na Prefeitura.",
    ]

    def __init__(self, game):
        super().__init__(game, "DESAFIO: LINHA DO TEMPO", 820, 560)
        self.current = list(self.EVENTOS)
        while self.current == self.EVENTOS:
            random.shuffle(self.current)
        self.selected_idx = -1
        self.tentativas = 0
        self.btn_check = Button((self.rect.centerx - 100, self.rect.bottom - 60, 200, 40), "VERIFICAR",
                                C.COLOR_ACCENT_GOLD, text_color=(0, 0, 0))

    def _rect(self, i):
        return pygame.Rect(self.rect.x + 80, self.rect.y + 120 + i * 58, 660, 48)

    def draw(self, surf, mouse_pos):
        self.draw_base(surf, mouse_pos)
        if self.solved:
            self._draw_concluido(surf, "Linha do tempo organizada!\n\nA vila existia antes da fábrica, e a contaminação "
                                       "começou com uma decisão da diretoria. A cronologia mostra que o dano não foi "
                                       "acidental: foi uma escolha econômica, tolerada pelo poder público.")
            return
        UIUtils.draw_text(surf, "Clique em dois eventos para trocar suas posições. Organize do mais antigo ao mais recente:",
                          pygame.Rect(self.rect.x + 40, self.rect.y + 80, 740, 30), FontManager.get(15), C.COLOR_TEXT_LIGHT)
        for i, ev in enumerate(self.current):
            r = self._rect(i)
            sel = i == self.selected_idx
            hov = r.collidepoint(mouse_pos)
            UIUtils.draw_rounded_rect(surf, r, (55, 68, 80) if sel or hov else C.COLOR_PANEL_ALT, 6,
                                      2 if sel else 1, C.COLOR_ACCENT_GOLD if sel else C.COLOR_PANEL_BORDER)
            UIUtils.draw_text(surf, f"{i + 1}. {ev}", pygame.Rect(r.x + 15, r.y + 14, r.width - 30, r.height),
                              FontManager.get(15), C.COLOR_TEXT_LIGHT)
        self.btn_check.draw(surf, mouse_pos)

    def handle_event(self, event, mouse_pos):
        nav = self._navegacao(event, mouse_pos)
        if nav is not None:
            return nav
        if self.solved:
            return "KEEP"
        for i in range(len(self.current)):
            if self._rect(i).collidepoint(mouse_pos):
                if self.selected_idx == -1:
                    self.selected_idx = i
                else:
                    a = self.selected_idx
                    self.current[a], self.current[i] = self.current[i], self.current[a]
                    self.selected_idx = -1
                return "KEEP"
        if self.btn_check.rect.collidepoint(mouse_pos):
            certos = sum(1 for a, b in zip(self.current, self.EVENTOS) if a == b)
            if certos == len(self.EVENTOS):
                self._concluir()
            else:
                self.game.estado.gamif.add_notification(f"{certos} de {len(self.EVENTOS)} na posição certa. "
                                                        "Tente de novo.", C.COLOR_ACCENT_RED)
        return "KEEP"


class Challenge2(_DesafioBase):
    ID = "discurso"
    CLAIMS = [
        ("\"A empresa atua com responsabilidade ambiental e tratamento adequado.\"", ("ev2", "ev1")),
        ("\"As atividades da fábrica trazem prosperidade para toda a população.\"", ("ev3",)),
        ("\"A empresa tem uma relação ética e transparente com a cidade.\"", ("ev5",)),
    ]

    def __init__(self, game):
        super().__init__(game, "DESAFIO: ANÁLISE DO DISCURSO", 1000, 600)
        self.matches = [False] * len(self.CLAIMS)
        self.selected_claim = -1

    def _claim_rect(self, i):
        return pygame.Rect(self.rect.x + 30, self.rect.y + 130 + i * 140, 400, 120)

    def _ev_rect(self, i):
        col, row = i % 2, i // 2
        return pygame.Rect(self.rect.x + 460 + col * 260, self.rect.y + 130 + row * 140, 250, 120)

    def draw(self, surf, mouse_pos):
        self.draw_base(surf, mouse_pos)
        if self.solved:
            self._draw_concluido(surf, "Análise concluída!\n\nA propaganda institucional destaca empregos e progresso, "
                                       "mas esconde os custos ambientais e sociais, que são empurrados para a "
                                       "comunidade e para o rio.")
            return
        UIUtils.draw_text(surf, "Selecione uma frase do outdoor (à esquerda) e depois a evidência que a desmente (à direita):",
                          pygame.Rect(self.rect.x + 30, self.rect.y + 80, 940, 30), FontManager.get(15), C.COLOR_TEXT_LIGHT)
        for i, (claim, _) in enumerate(self.CLAIMS):
            r = self._claim_rect(i)
            col = C.COLOR_ACCENT_GREEN if self.matches[i] else ((60, 72, 85) if i == self.selected_claim else C.COLOR_PANEL_ALT)
            UIUtils.draw_rounded_rect(surf, r, col, 8, 2 if i == self.selected_claim else 1,
                                      C.COLOR_ACCENT_GOLD if i == self.selected_claim else C.COLOR_PANEL_BORDER)
            UIUtils.draw_text(surf, claim, r.inflate(-24, -24), FontManager.get(15, True),
                              (0, 0, 0) if self.matches[i] else C.COLOR_TEXT_LIGHT)
        evs = self.game.estado.evidencias
        if not evs:
            UIUtils.draw_text(surf, "Você ainda não tem evidências. Investigue a vila e volte depois.",
                              pygame.Rect(self.rect.x + 460, self.rect.y + 200, 500, 60), FontManager.get(15),
                              C.COLOR_TEXT_MUTED)
        for i, ev in enumerate(evs):
            r = self._ev_rect(i)
            hov = r.collidepoint(mouse_pos) and self.selected_claim != -1
            UIUtils.draw_rounded_rect(surf, r, (55, 68, 80) if hov else C.COLOR_PANEL_ALT, 8, 1, C.COLOR_PANEL_BORDER)
            titulo, texto = self.game.estado.registro_evidencia(ev)
            UIUtils.draw_text(surf, titulo, pygame.Rect(r.x + 12, r.y + 10, r.width - 24, 40), FontManager.get(13, True),
                              C.COLOR_ACCENT_GOLD)
            resumo = texto.split("O que revela: ")[-1]
            UIUtils.draw_text(surf, resumo, pygame.Rect(r.x + 12, r.y + 48, r.width - 24, 70), FontManager.get(12),
                              C.COLOR_TEXT_MUTED, line_spacing=2)

    def handle_event(self, event, mouse_pos):
        nav = self._navegacao(event, mouse_pos)
        if nav is not None:
            return nav
        if self.solved:
            return "KEEP"
        for i in range(len(self.CLAIMS)):
            if not self.matches[i] and self._claim_rect(i).collidepoint(mouse_pos):
                self.selected_claim = i
                return "KEEP"
        if self.selected_claim != -1:
            for i, ev in enumerate(self.game.estado.evidencias):
                if self._ev_rect(i).collidepoint(mouse_pos):
                    g = self.game.estado.gamif
                    if ev in self.CLAIMS[self.selected_claim][1]:
                        self.matches[self.selected_claim] = True
                        g.add_notification("Contradição revelada!", C.COLOR_ACCENT_GREEN)
                        if all(self.matches):
                            self._concluir()
                    else:
                        g.add_notification("Essa evidência não desmente diretamente essa frase.", C.COLOR_ACCENT_RED)
                    self.selected_claim = -1
                    return "KEEP"
        return "KEEP"


class Challenge3(_DesafioBase):
    ID = "atores"
    CATEGORIAS = ["Quem lucra", "Quem sofre os danos", "Quem deveria fiscalizar", "Quem se organiza"]
    ATORES = [
        ("Vale das Pedras S.A.", 0, "A empresa economiza ao não tratar o efluente: o lucro fica com ela, o custo vai para o rio."),
        ("Pescadores ribeirinhos", 1, "Perderam a pesca, a renda e a saúde. São os primeiros atingidos."),
        ("Operários da fábrica", 1, "Não lucram com o corte: ficam reféns do medo da demissão e expostos aos riscos."),
        ("Comerciantes da vila", 1, "Sem renda dos pescadores, as vendas caem. O dano se espalha pela economia local."),
        ("Prefeitura", 2, "Tem o dever legal de fiscalizar, mas engavetou o processo por interesse econômico."),
        ("Associação de Moradores", 3, "Reúne denúncias e pressiona os órgãos públicos: é a força da organização coletiva."),
    ]

    def __init__(self, game):
        super().__init__(game, "DESAFIO: MAPA DE ATORES", 1080, 600)
        self.colocados = {}
        self.sel = -1
        self.feedback = "Clique em um ator e depois na coluna que melhor descreve seu papel no conflito."
        self.feedback_cor = C.COLOR_TEXT_MUTED

    def _ator_rect(self, i):
        return pygame.Rect(self.rect.x + 30 + i * 172, self.rect.y + 80, 162, 54)

    def _col_rect(self, j):
        return pygame.Rect(self.rect.x + 30 + j * 258, self.rect.y + 200, 246, 320)

    def draw(self, surf, mouse_pos):
        self.draw_base(surf, mouse_pos)
        if self.solved:
            self._draw_concluido(surf, "Mapa completo!\n\nOs benefícios da degradação ficam concentrados em poucos, "
                                       "enquanto os danos se espalham por quem tem menos poder. Isso é o que se chama "
                                       "de injustiça ambiental. A saída passa pela fiscalização pública e pela "
                                       "organização coletiva.")
            return
        for i, (nome, _, _) in enumerate(self.ATORES):
            if i in self.colocados:
                continue
            r = self._ator_rect(i)
            sel = i == self.sel
            UIUtils.draw_rounded_rect(surf, r, (60, 72, 85) if sel or r.collidepoint(mouse_pos) else C.COLOR_PANEL_ALT,
                                      8, 2 if sel else 1, C.COLOR_ACCENT_GOLD if sel else C.COLOR_PANEL_BORDER)
            f = FontManager.get(14, True)
            th = UIUtils.text_height(nome, r.width - 16, f, 2)
            UIUtils.draw_text(surf, nome, pygame.Rect(r.x + 8, r.centery - th // 2, r.width - 16, th), f,
                              C.COLOR_TEXT_LIGHT, center=True, line_spacing=2)
        UIUtils.draw_text(surf, self.feedback, pygame.Rect(self.rect.x + 30, self.rect.y + 148, self.rect.width - 60, 44),
                          FontManager.get(14), self.feedback_cor)
        for j, cat in enumerate(self.CATEGORIAS):
            r = self._col_rect(j)
            hov = r.collidepoint(mouse_pos) and self.sel != -1
            UIUtils.draw_rounded_rect(surf, r, (40, 55, 68) if hov else (22, 30, 38), 8, 1, C.COLOR_PANEL_BORDER)
            surf.blit(FontManager.get(16, True).render(cat, True, C.COLOR_ACCENT_GOLD), (r.x + 14, r.y + 12))
            y = r.y + 46
            for i, col in self.colocados.items():
                if col == j:
                    UIUtils.draw_rounded_rect(surf, pygame.Rect(r.x + 10, y, r.width - 20, 36), C.COLOR_ACCENT_GREEN, 6)
                    UIUtils.draw_text(surf, self.ATORES[i][0], pygame.Rect(r.x + 18, y + 9, r.width - 36, 20),
                                      FontManager.get(14, True), (0, 0, 0))
                    y += 44

    def handle_event(self, event, mouse_pos):
        nav = self._navegacao(event, mouse_pos)
        if nav is not None:
            return nav
        if self.solved:
            return "KEEP"
        for i in range(len(self.ATORES)):
            if i not in self.colocados and self._ator_rect(i).collidepoint(mouse_pos):
                self.sel = i
                return "KEEP"
        if self.sel != -1:
            for j in range(len(self.CATEGORIAS)):
                if self._col_rect(j).collidepoint(mouse_pos):
                    nome, certo, explic = self.ATORES[self.sel]
                    if j == certo:
                        self.colocados[self.sel] = j
                        self.feedback, self.feedback_cor = f"Correto! {explic}", C.COLOR_ACCENT_GREEN
                        if len(self.colocados) == len(self.ATORES):
                            self._concluir()
                    else:
                        self.feedback = f"Pense de novo sobre \"{nome}\": essa coluna não descreve seu papel."
                        self.feedback_cor = C.COLOR_ACCENT_RED
                    self.sel = -1
                    return "KEEP"
        return "KEEP"


DESAFIOS = {"linha": Challenge1, "discurso": Challenge2, "atores": Challenge3}
