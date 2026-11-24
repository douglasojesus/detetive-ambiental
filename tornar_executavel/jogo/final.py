# ==============================================================================
# ETAPA FINAL: AUDIÊNCIA PÚBLICA, DOSSIÊ E OS 5 FINAIS
# ==============================================================================
import pygame

from . import config as C
from .cenario import desenhar_pessoa, desenhar_rio_final, retrato
from .conteudo import ALEGACOES, FINAIS, MENSAGEM_CENTRAL, ORDEM_FINAIS, PERGUNTAS_DOSSIE
from .graficos import Button, FontManager, UIUtils, is_left_click
from .modelos import NPC


# ------------------------------------------------------------------------------
# CÁLCULO DO FINAL (função pura, testável sem janela)
# ------------------------------------------------------------------------------
def calcular_final(n_evidencias: int, credibilidade: int, respostas: dict, flags=frozenset()) -> str:
    resp = respostas.get("responsaveis")
    enc = respostas.get("encaminhamento")
    trab = respostas.get("trabalhadores")
    if resp in ("trabalhadores", "acidente") or n_evidencias < C.EVID_MINIMAS or credibilidade < C.CRED_MINIMA:
        return "arquivado"
    if enc == "acordo" or trab == "expor":
        return "silenciamento"
    if enc == "fechar" or trab == "ignorar":
        return "dividida"
    if (resp == "empresa_poder" and enc == "mp" and trab == "transicao" and n_evidencias == 6
            and credibilidade >= C.CRED_ALTA and "associacao_na_audiencia" in flags):
        return "justica"
    return "multa"


def bonus_preparo(estado):
    """Credibilidade inicial: desafios concluídos + presença da Associação."""
    itens = []
    for d in sorted(estado.desafios_ok):
        nomes = {"linha": "Linha do Tempo", "discurso": "Análise do Discurso", "atores": "Mapa de Atores"}
        itens.append((f"Desafio concluído: {nomes.get(d, d)}", C.CRED_BONUS_DESAFIO))
    if "associacao_na_audiencia" in estado.flags:
        itens.append(("A Associação de Moradores lotou a Câmara", C.CRED_BONUS_ASSOCIACAO))
    return itens


def avaliar_resposta(alegacao, registro_id):
    """Retorna (delta de credibilidade, tipo) para um registro apresentado."""
    if registro_id is None:
        return 0, "silencio"
    if registro_id == alegacao.correta:
        return C.CRED_ACERTO, "acerto"
    if registro_id in alegacao.parciais:
        return C.CRED_PARCIAL, "parcial"
    return C.CRED_ERRO, "erro"


ADVOGADO = NPC("adv", "Dr. Mendonça", "", {}, (40, 45, 60), (35, 38, 50), (225, 185, 150), (60, 50, 40), "")
SECRETARIO = NPC("sec", "Sr. Valdemar", "", {}, (120, 110, 90), (60, 55, 50), (200, 160, 120), (170, 170, 170), "")
PUBLICO = [NPC("p", "", "", {}, c, (60, 60, 70), p, h, "") for c, p, h in [
    ((170, 90, 120), (150, 105, 75), (200, 200, 200)), ((60, 130, 90), (95, 65, 45), (25, 20, 20)),
    ((220, 220, 210), (200, 150, 110), (90, 70, 50)), ((70, 120, 170), (170, 120, 85), (20, 20, 20)),
    ((180, 70, 60), (110, 75, 50), (150, 150, 150)), ((230, 170, 40), (120, 80, 55), (30, 25, 20)),
    ((140, 160, 90), (190, 140, 100), (60, 40, 30)), ((90, 90, 140), (140, 95, 65), (40, 30, 20))]]


def desenhar_camara(surf, n_publico, t):
    surf.fill((52, 44, 40))
    pygame.draw.rect(surf, (88, 70, 58), (0, 0, C.VIRTUAL_WIDTH, 300))
    for x in range(40, C.VIRTUAL_WIDTH, 160):
        pygame.draw.rect(surf, (100, 82, 68), (x, 30, 90, 200), border_radius=6)
    pygame.draw.rect(surf, (40, 120, 70), (C.VIRTUAL_WIDTH // 2 - 30, 20, 60, 36))
    pygame.draw.rect(surf, (120, 85, 55), (0, 300, C.VIRTUAL_WIDTH, 10))
    # público ao fundo
    for i in range(n_publico):
        fila, pos = divmod(i, 14)
        x = 70 + pos * 82 + (fila % 2) * 40
        desenhar_pessoa(surf, x, 270 + fila * 22, PUBLICO[i % len(PUBLICO)], t, escala=0.8)


# ------------------------------------------------------------------------------
# AUDIÊNCIA PÚBLICA
# ------------------------------------------------------------------------------
class AudienciaUI:
    def __init__(self, game):
        self.game = game
        self.estado = game.estado
        self.fase = "INTRO"
        self.idx = 0
        self.bonus = bonus_preparo(self.estado)
        self.credibilidade = sum(v for _, v in self.bonus)
        self.acertos = 0
        self.ultimo = None
        self.retratos = {"Dr. Mendonça": retrato(ADVOGADO, (130, 156)), "Sr. Valdemar": retrato(SECRETARIO, (130, 156))}
        mob = len({"associacao_na_audiencia", "francisca_mobilizada"} & self.estado.flags)
        self.n_publico = [5, 16, 28][mob]
        self.btn_ok = Button((C.VIRTUAL_WIDTH // 2 - 130, 640, 260, 46), "COMEÇAR A AUDIÊNCIA", C.COLOR_ACCENT_GOLD,
                             text_color=(0, 0, 0), font_size=16)
        self.btn_silencio = Button((C.VIRTUAL_WIDTH - 250, 666, 210, 38), "NÃO CONTESTAR", font_size=14)
        self._montar_registros()

    def _montar_registros(self):
        e = self.estado
        regs = [(ev, e.registro_evidencia(ev)[0], True) for ev in e.evidencias]
        regs += [(i.id, i.nome, False) for i in e.itens if i.tipo == "SECONDARY" and i.id in e.vistos]
        self.registros = regs

    def _reg_rect(self, k):
        col, row = k % 4, k // 4
        return pygame.Rect(40 + col * 302, 470 + row * 44, 292, 38)

    def draw(self, surf, mouse_pos, t):
        desenhar_camara(surf, self.n_publico, t)
        painel = pygame.Rect(30, 80, C.VIRTUAL_WIDTH - 60, 610)
        UIUtils.draw_rounded_rect(surf, painel, (24, 32, 42), 12, 2, C.COLOR_PANEL_BORDER)
        surf.blit(FontManager.get(22, True).render("AUDIÊNCIA PÚBLICA — CÂMARA MUNICIPAL", True, C.COLOR_ACCENT_GOLD),
                  (painel.x + 24, painel.y + 16))
        cred = FontManager.get(16, True).render(f"CREDIBILIDADE DA DENÚNCIA: {self.credibilidade}", True,
                                                C.COLOR_ACCENT_CYAN)
        surf.blit(cred, (painel.right - cred.get_width() - 24, painel.y + 20))
        getattr(self, "_draw_" + self.fase.lower())(surf, mouse_pos, painel)

    def _draw_intro(self, surf, mouse_pos, p):
        e = self.estado
        motivo = ("O prazo da investigação acabou. A audiência foi convocada com as provas que você conseguiu reunir.\n\n"
                  if e.tempo_esgotado else "Você convocou a audiência pública com as provas reunidas.\n\n")
        texto = (motivo + "Representantes da Vale das Pedras e da Prefeitura vão fazer alegações. Para cada uma, "
                 "apresente o registro da sua mochila que melhor a desmente. Uma evidência direta vale mais; uma "
                 "informação secundária ajuda um pouco; um registro sem relação enfraquece a denúncia.")
        UIUtils.draw_text(surf, texto, pygame.Rect(p.x + 40, p.y + 70, p.width - 80, 200), FontManager.get(17),
                          C.COLOR_TEXT_LIGHT, line_spacing=6)
        y = p.y + 260
        surf.blit(FontManager.get(16, True).render("PREPARO (credibilidade inicial):", True, C.COLOR_ACCENT_GOLD),
                  (p.x + 40, y))
        y += 32
        if not self.bonus:
            surf.blit(FontManager.get(15).render("Nenhum. (Desafios concluídos e o apoio da Associação dão bônus.)", True,
                                                 C.COLOR_TEXT_MUTED), (p.x + 60, y))
        for texto, v in self.bonus:
            surf.blit(FontManager.get(15).render(f"+{v}  {texto}", True, C.COLOR_ACCENT_GREEN), (p.x + 60, y))
            y += 26
        surf.blit(FontManager.get(15).render(f"Evidências principais reunidas: {len(e.evidencias)}/6", True,
                                             C.COLOR_TEXT_LIGHT), (p.x + 40, p.y + 440))
        self.btn_ok.text = "COMEÇAR A AUDIÊNCIA"
        self.btn_ok.draw(surf, mouse_pos)

    def _cabecalho_alegacao(self, surf, p):
        a = ALEGACOES[self.idx]
        surf.blit(self.retratos[a.quem], (p.x + 30, p.y + 60))
        surf.blit(FontManager.get(13, True).render(f"ALEGAÇÃO {self.idx + 1} DE {len(ALEGACOES)}", True,
                                                   C.COLOR_TEXT_MUTED), (p.x + 190, p.y + 66))
        surf.blit(FontManager.get(18, True).render(a.quem, True, C.COLOR_TEXT_LIGHT), (p.x + 190, p.y + 88))
        surf.blit(FontManager.get(13).render(a.cargo, True, C.COLOR_TEXT_MUTED), (p.x + 190, p.y + 112))
        balao = pygame.Rect(p.x + 190, p.y + 140, p.width - 230, 84)
        UIUtils.draw_rounded_rect(surf, balao, (240, 236, 225), 10)
        UIUtils.draw_text(surf, f"\"{a.texto}\"", balao.inflate(-30, -24), FontManager.get(18, True), (30, 30, 30))
        return a

    def _draw_alegacao(self, surf, mouse_pos, p):
        self._cabecalho_alegacao(surf, p)
        surf.blit(FontManager.get(16, True).render("Qual registro desmente essa alegação?", True, C.COLOR_ACCENT_GOLD),
                  (p.x + 30, p.y + 330))
        surf.blit(FontManager.get(13).render("Dourado = evidência principal   •   Azul = informação secundária", True,
                                             C.COLOR_TEXT_MUTED), (p.x + 30, p.y + 356))
        for k, (rid, nome, principal) in enumerate(self.registros):
            r = self._reg_rect(k)
            hov = r.collidepoint(mouse_pos)
            borda = C.COLOR_ACCENT_GOLD if principal else C.COLOR_ACCENT_CYAN
            UIUtils.draw_rounded_rect(surf, r, (55, 68, 82) if hov else C.COLOR_PANEL_ALT, 6, 2 if hov else 1, borda)
            UIUtils.draw_text(surf, nome, pygame.Rect(r.x + 10, r.y + 10, r.width - 20, 20), FontManager.get(13, True),
                              borda if principal else C.COLOR_TEXT_LIGHT)
        if not self.registros:
            surf.blit(FontManager.get(15).render("Sua mochila está vazia.", True, C.COLOR_TEXT_MUTED), (p.x + 30, p.y + 400))
        self.btn_silencio.draw(surf, mouse_pos)

    def _draw_resposta(self, surf, mouse_pos, p):
        a = self._cabecalho_alegacao(surf, p)
        delta, tipo, nome = self.ultimo
        cores = {"acerto": C.COLOR_ACCENT_GREEN, "parcial": C.COLOR_ACCENT_GOLD, "erro": C.COLOR_ACCENT_RED,
                 "silencio": C.COLOR_TEXT_MUTED}
        titulos = {"acerto": "CONTRADIÇÃO EXPOSTA!", "parcial": "ARGUMENTO PARCIAL",
                   "erro": "ESSE REGISTRO NÃO DESMENTE A ALEGAÇÃO", "silencio": "A ALEGAÇÃO FICOU SEM RESPOSTA"}
        y = p.y + 260
        surf.blit(FontManager.get(22, True).render(titulos[tipo], True, cores[tipo]), (p.x + 40, y))
        sinal = f"{delta:+d}" if delta else "0"
        surf.blit(FontManager.get(18, True).render(f"Credibilidade {sinal}", True, cores[tipo]), (p.right - 240, y + 4))
        y += 44
        if nome:
            surf.blit(FontManager.get(15).render(f"Você apresentou: {nome}", True, C.COLOR_TEXT_LIGHT), (p.x + 40, y))
            y += 30
        if tipo == "acerto":
            expl = a.explicacao
        elif tipo == "parcial":
            expl = "Esse registro reforça a denúncia, mas não é uma prova direta. A melhor resposta seria: " + a.explicacao
        else:
            expl = ("A empresa e a Prefeitura aproveitam a falta de uma prova direta. " +
                    ("Você ainda não tinha a evidência certa para este ponto." if a.correta not in self.estado.evidencias
                     else "A evidência certa estava na sua mochila..."))
        UIUtils.draw_text(surf, expl, pygame.Rect(p.x + 40, y + 6, p.width - 80, 120), FontManager.get(16),
                          C.COLOR_TEXT_LIGHT, line_spacing=6)
        self.btn_ok.text = "PRÓXIMA ALEGAÇÃO" if self.idx < len(ALEGACOES) - 1 else "VER RESULTADO"
        self.btn_ok.draw(surf, mouse_pos)

    def _draw_resumo(self, surf, mouse_pos, p):
        UIUtils.draw_text(surf, f"Você desmentiu diretamente {self.acertos} de {len(ALEGACOES)} alegações.",
                          pygame.Rect(p.x, p.y + 110, p.width, 40), FontManager.get(24, True), C.COLOR_TEXT_LIGHT,
                          center=True)
        UIUtils.draw_text(surf, f"Credibilidade final da denúncia: {self.credibilidade}",
                          pygame.Rect(p.x, p.y + 170, p.width, 40), FontManager.get(22, True), C.COLOR_ACCENT_CYAN,
                          center=True)
        if self.credibilidade >= C.CRED_ALTA:
            txt = "A Câmara está convencida. A denúncia tem força para exigir mudanças profundas."
        elif self.credibilidade >= C.CRED_MINIMA:
            txt = "A denúncia foi ouvida, mas a empresa ainda tem espaço para se defender."
        else:
            txt = "A denúncia saiu enfraquecida. Os advogados da empresa dominaram a audiência."
        UIUtils.draw_text(surf, txt, pygame.Rect(p.x + 100, p.y + 240, p.width - 200, 60), FontManager.get(18),
                          C.COLOR_TEXT_MUTED, center=True)
        UIUtils.draw_text(surf, "Agora, monte o dossiê final: quem é responsável e o que deve ser feito.",
                          pygame.Rect(p.x + 100, p.y + 330, p.width - 200, 60), FontManager.get(18),
                          C.COLOR_TEXT_LIGHT, center=True)
        self.btn_ok.text = "MONTAR O DOSSIÊ FINAL"
        self.btn_ok.draw(surf, mouse_pos)

    def _responder(self, rid, nome):
        a = ALEGACOES[self.idx]
        delta, tipo = avaliar_resposta(a, rid)
        self.credibilidade += delta
        if tipo == "acerto":
            self.acertos += 1
        self.ultimo = (delta, tipo, nome)
        self.fase = "RESPOSTA"

    def handle_event(self, event, mouse_pos):
        """Retorna 'DOSSIE' quando a audiência termina."""
        if not is_left_click(event):
            return None
        if self.fase == "INTRO" and self.btn_ok.rect.collidepoint(mouse_pos):
            self.fase = "ALEGACAO"
        elif self.fase == "ALEGACAO":
            if self.btn_silencio.rect.collidepoint(mouse_pos):
                self._responder(None, "")
            for k, (rid, nome, _) in enumerate(self.registros):
                if self._reg_rect(k).collidepoint(mouse_pos):
                    self._responder(rid, nome)
                    break
        elif self.fase == "RESPOSTA" and self.btn_ok.rect.collidepoint(mouse_pos):
            if self.idx < len(ALEGACOES) - 1:
                self.idx += 1
                self.fase = "ALEGACAO"
            else:
                self.fase = "RESUMO"
                if self.acertos == len(ALEGACOES):
                    self.estado.gamif.unlock("a_argumento")
        elif self.fase == "RESUMO" and self.btn_ok.rect.collidepoint(mouse_pos):
            return "DOSSIE"
        return None


# ------------------------------------------------------------------------------
# DOSSIÊ FINAL
# ------------------------------------------------------------------------------
class DossieUI:
    def __init__(self, game):
        self.game = game
        self.q = 0
        self.respostas = {}
        self.sel = None
        self.btn_ok = Button((C.VIRTUAL_WIDTH // 2 + 10, 630, 240, 46), "CONFIRMAR", C.COLOR_ACCENT_GOLD,
                             text_color=(0, 0, 0), font_size=16)
        self.btn_voltar = Button((C.VIRTUAL_WIDTH // 2 - 250, 630, 240, 46), "VOLTAR", font_size=16)

    def _opt_rect(self, i):
        return pygame.Rect(170, 230 + i * 92, C.VIRTUAL_WIDTH - 340, 80)

    def draw(self, surf, mouse_pos, t):
        surf.fill(C.COLOR_BG_DARK)
        perg = PERGUNTAS_DOSSIE[self.q]
        surf.blit(FontManager.get(16, True).render(f"DOSSIÊ FINAL — PARTE {self.q + 1} DE {len(PERGUNTAS_DOSSIE)}", True,
                                                   C.COLOR_ACCENT_GOLD), (170, 110))
        UIUtils.draw_text(surf, perg.titulo, pygame.Rect(170, 145, C.VIRTUAL_WIDTH - 340, 70), FontManager.get(26, True),
                          C.COLOR_TEXT_LIGHT)
        for i, op in enumerate(perg.opcoes):
            r = self._opt_rect(i)
            sel = self.sel == op.id
            hov = r.collidepoint(mouse_pos)
            UIUtils.draw_rounded_rect(surf, r, (55, 68, 82) if sel or hov else C.COLOR_PANEL_ALT, 8, 2 if sel else 1,
                                      C.COLOR_ACCENT_GOLD if sel else C.COLOR_PANEL_BORDER)
            pygame.draw.circle(surf, C.COLOR_ACCENT_GOLD if sel else C.COLOR_TEXT_MUTED, (r.x + 30, r.centery), 10, 2)
            if sel:
                pygame.draw.circle(surf, C.COLOR_ACCENT_GOLD, (r.x + 30, r.centery), 5)
            f = FontManager.get(17)
            th = UIUtils.text_height(op.texto, r.width - 80, f, 4)
            UIUtils.draw_text(surf, op.texto, pygame.Rect(r.x + 56, r.centery - th // 2 + 2, r.width - 80, th),
                              f, C.COLOR_TEXT_LIGHT, line_spacing=4)
        self.btn_ok.enabled = self.sel is not None
        self.btn_ok.text = "CONFIRMAR" if self.q < len(PERGUNTAS_DOSSIE) - 1 else "ENTREGAR O DOSSIÊ"
        self.btn_ok.draw(surf, mouse_pos)
        if self.q > 0:
            self.btn_voltar.draw(surf, mouse_pos)

    def handle_event(self, event, mouse_pos):
        """Retorna o dicionário de respostas quando o dossiê é entregue."""
        if not is_left_click(event):
            return None
        perg = PERGUNTAS_DOSSIE[self.q]
        for i, op in enumerate(perg.opcoes):
            if self._opt_rect(i).collidepoint(mouse_pos):
                self.sel = op.id
                return None
        if self.q > 0 and self.btn_voltar.rect.collidepoint(mouse_pos):
            self.q -= 1
            self.sel = self.respostas.get(PERGUNTAS_DOSSIE[self.q].id)
            return None
        if self.btn_ok.clicked(event, mouse_pos):
            self.respostas[perg.id] = self.sel
            if self.q < len(PERGUNTAS_DOSSIE) - 1:
                self.q += 1
                self.sel = self.respostas.get(PERGUNTAS_DOSSIE[self.q].id)
                return None
            return dict(self.respostas)
        return None


# ------------------------------------------------------------------------------
# TELA DE FINAL
# ------------------------------------------------------------------------------
class FinalUI:
    def __init__(self, game, final_id, credibilidade, acertos):
        self.game = game
        self.final = FINAIS[final_id]
        self.estado = game.estado
        self.credibilidade = credibilidade
        self.acertos = acertos
        self.pagina = 0
        self.btn_prox = Button((C.VIRTUAL_WIDTH - 300, 650, 260, 46), "REFLEXÃO FINAL", C.COLOR_ACCENT_GOLD,
                               text_color=(0, 0, 0), font_size=16)
        self.btn_novo = Button((C.VIRTUAL_WIDTH - 300, 650, 260, 46), "JOGAR NOVAMENTE", C.COLOR_ACCENT_GOLD,
                               text_color=(0, 0, 0), font_size=16)
        self.btn_cred = Button((40, 650, 200, 46), "CRÉDITOS", font_size=16)

    def draw(self, surf, mouse_pos, t):
        surf.fill(C.COLOR_BG_DARK)
        f = self.final
        if self.pagina == 0:
            surf.blit(FontManager.get(14, True).render("FINAL", True, C.COLOR_TEXT_MUTED), (40, 34))
            surf.blit(FontManager.get(34, True).render(f.titulo, True, f.cor_titulo), (40, 52))
            surf.blit(FontManager.get(18).render(f.subtitulo, True, C.COLOR_TEXT_LIGHT), (40, 98))
            img = pygame.Rect(40, 140, 512, 288)
            desenhar_rio_final(surf, img, f.cor_rio, self.game.renderer, peixes=f.id == "justica", t=t)
            UIUtils.draw_text(surf, f.texto, pygame.Rect(590, 140, 650, 420), FontManager.get(17), C.COLOR_TEXT_LIGHT,
                              line_spacing=6)
            e = self.estado
            linhas = [f"Evidências: {len(e.evidencias)}/6", f"Alegações desmentidas: {self.acertos}/{len(ALEGACOES)}",
                      f"Credibilidade: {self.credibilidade}", f"Dia {e.dia}/{C.TOTAL_DIAS}",
                      f"Nível {e.gamif.level}: {e.gamif.level_names[e.gamif.level - 1]}",
                      f"Conquistas: {sum(a.unlocked for a in e.gamif.achievements)}/{len(e.gamif.achievements)}"]
            for i, l in enumerate(linhas):
                surf.blit(FontManager.get(15).render(l, True, C.COLOR_TEXT_MUTED), (40 + (i % 2) * 260, 450 + (i // 2) * 28))
            self._draw_finais(surf, 560)
            self.btn_prox.draw(surf, mouse_pos)
        else:
            surf.blit(FontManager.get(28, True).render("PARA REFLETIR", True, C.COLOR_ACCENT_GOLD), (120, 70))
            y = 130
            for q in f.reflexoes:
                y += UIUtils.draw_text(surf, "•  " + q, pygame.Rect(140, y, 1000, 80), FontManager.get(19),
                                       C.COLOR_TEXT_LIGHT, line_spacing=6) + 16
            box = pygame.Rect(120, max(y + 20, 380), 1040, 150)
            UIUtils.draw_rounded_rect(surf, box, C.COLOR_PANEL_ALT, 10, 2, C.COLOR_ACCENT_GREEN)
            UIUtils.draw_text(surf, MENSAGEM_CENTRAL, box.inflate(-50, -40), FontManager.get(18, True),
                              C.COLOR_ACCENT_GREEN, center=True, line_spacing=6)
            UIUtils.draw_text(surf, "Existem 5 finais. Jogue de novo e tome outras decisões para descobrir os demais.",
                              pygame.Rect(0, 600, C.VIRTUAL_WIDTH, 30), FontManager.get(15), C.COLOR_TEXT_MUTED,
                              center=True)
            self.btn_cred.draw(surf, mouse_pos)
            self.btn_novo.draw(surf, mouse_pos)

    def _draw_finais(self, surf, y):
        vistos = self.game.finais_vistos
        surf.blit(FontManager.get(14, True).render(f"FINAIS DESCOBERTOS: {len(vistos)}/5", True, C.COLOR_TEXT_MUTED),
                  (40, y))
        for i, fid in enumerate(ORDEM_FINAIS):
            r = pygame.Rect(40 + i * 104, y + 26, 96, 50)
            ok = fid in vistos
            fin = FINAIS[fid]
            UIUtils.draw_rounded_rect(surf, r, C.COLOR_PANEL_ALT if ok else (26, 32, 38), 6, 2 if fid == self.final.id else 1,
                                      fin.cor_titulo if ok else C.COLOR_PANEL_BORDER)
            nome = fin.titulo.split(",")[0].replace("\"", "") if ok else "?"
            f = FontManager.get(10, True)
            th = UIUtils.text_height(nome, r.width - 8, f, 0)
            UIUtils.draw_text(surf, nome, pygame.Rect(r.x + 4, r.centery - th // 2, r.width - 8, th), f,
                              fin.cor_titulo if ok else C.COLOR_TEXT_MUTED, center=True, line_spacing=0)

    def handle_event(self, event, mouse_pos):
        """Retorna 'NOVO' ou 'CREDITOS'."""
        if not is_left_click(event):
            return None
        if self.pagina == 0 and self.btn_prox.rect.collidepoint(mouse_pos):
            self.pagina = 1
        elif self.pagina == 1:
            if self.btn_novo.rect.collidepoint(mouse_pos):
                return "NOVO"
            if self.btn_cred.rect.collidepoint(mouse_pos):
                return "CREDITOS"
        return None
