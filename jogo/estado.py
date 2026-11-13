# ==============================================================================
# ESTADO DA PARTIDA: TEMPO, FLAGS, CONFIANÇA, EVIDÊNCIAS E GAMIFICAÇÃO
# Não desenha nada: pode ser usado em testes sem abrir janela.
# ==============================================================================
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from . import config as C
from .conteudo import NPCS, REGISTRO_EVIDENCIAS, criar_itens
from .modelos import DIA, NOITE, Escolha, Item


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
        self.notifications = []
        self.level_thresholds = [0, 150, 350, 600, 1000]
        self.level_names = ["Observador", "Explorador", "Investigador", "Analista", "Detetive Ambiental"]
        self.achievements = [
            Achievement("a_first", "Primeiro Contato", "Examine o primeiro objeto do cenário."),
            Achievement("a_10", "Olhar Atento", "Examine 10 objetos ou pessoas."),
            Achievement("a_20", "Explorador da Vila", "Examine 20 objetos ou pessoas."),
            Achievement("a_all_ev", "Investigação Completa", "Encontre as 6 evidências principais."),
            Achievement("a_curious", "Curioso por Natureza", "Descubra 5 curiosidades da região."),
            Achievement("a_voices", "Vozes da Comunidade", "Converse com 3 moradores diferentes."),
            Achievement("a_coruja", "Coruja", "Investigue algo durante a noite."),
            Achievement("a_confianca", "Confiança Conquistada", "Ganhe a confiança total de Seu Jair."),
            Achievement("a_desafios", "Pensamento Crítico", "Conclua os 3 desafios de interpretação."),
            Achievement("a_argumento", "Argumentação Sólida", "Desminta as 6 alegações na audiência."),
            Achievement("a_justica", "Justiça Ambiental", "Alcance o final de Justiça Socioambiental."),
        ]

    def add_xp(self, amount: int, reason: str):
        self.xp += amount
        self.add_notification(f"+{amount} XP: {reason}", C.COLOR_ACCENT_GREEN)
        new_level = self.level
        for i, threshold in enumerate(self.level_thresholds):
            if self.xp >= threshold:
                new_level = i + 1
        if new_level > self.level:
            self.level = new_level
            self.add_notification(f"NÍVEL {self.level}: {self.level_names[self.level - 1]}!", C.COLOR_ACCENT_GOLD)

    def unlock(self, ach_id: str):
        for a in self.achievements:
            if a.id == ach_id and not a.unlocked:
                a.unlocked = True
                self.add_notification(f"CONQUISTA: {a.title}", C.COLOR_ACCENT_CYAN, icon="trophy")

    def add_notification(self, text: str, color, icon: str = ""):
        self.notifications.append({"text": text, "color": color, "time": 4.0, "icon": icon})
        self.notifications = self.notifications[-6:]

    def update_notifications(self, dt: float):
        for n in self.notifications:
            n["time"] -= dt
        self.notifications = [n for n in self.notifications if n["time"] > 0]

    def get_level_progress(self):
        if self.level >= len(self.level_thresholds):
            return 1.0
        cur = self.level_thresholds[self.level - 1]
        nxt = self.level_thresholds[self.level]
        return (self.xp - cur) / max(1, nxt - cur)


@dataclass
class Resultado:
    """O que acontece ao clicar num item."""
    tipo: str            # "TEXTO", "BLOQUEADO" ou "DIALOGO"
    item: Item
    texto: str = ""
    custo: int = 0


class Estado:
    def __init__(self):
        self.dia = 1
        self.periodo = DIA
        self.acoes = C.ACOES_DIA
        self.flags = set()
        self.confianca: Dict[str, int] = {k: 0 for k in NPCS}
        self.evidencias: List[str] = []           # ids na ordem em que foram obtidas
        self.vistos = set()                       # itens já examinados (registrados)
        self.conversados = set()                  # npcs com quem já conversou
        self.escolhas_feitas: Dict[str, List[str]] = {k: [] for k in NPCS}
        self.transcricoes: Dict[str, List[Tuple[str, str]]] = {k: [] for k in NPCS}
        self.npc_ausente: Dict[str, Tuple[int, str]] = {}
        self.desafios_ok = set()
        self.gamif = Gamification()
        self.itens = criar_itens()
        self.por_id = {i.id: i for i in self.itens}
        self.tempo_esgotado = False

    # ------------------------------------------------------------------ tempo
    @property
    def acoes_max(self):
        return C.ACOES_DIA if self.periodo == DIA else C.ACOES_NOITE

    def avancar_periodo(self) -> str:
        """Passa para o próximo período. Retorna 'NOITE', 'DIA' ou 'FIM'."""
        if self.periodo == DIA:
            self.periodo = NOITE
            self.acoes = C.ACOES_NOITE
            return NOITE
        if self.dia >= C.TOTAL_DIAS:
            self.tempo_esgotado = True
            self.acoes = 0
            return "FIM"
        self.dia += 1
        self.periodo = DIA
        self.acoes = C.ACOES_DIA
        return DIA

    # --------------------------------------------------------------- presença
    def npc_presente(self, npc_id: str) -> bool:
        npc = NPCS[npc_id]
        if self.periodo not in npc.posicoes:
            return False
        return self.npc_ausente.get(npc_id) != (self.dia, self.periodo)

    def item_presente(self, item: Item) -> bool:
        if item.npc:
            return self.npc_presente(item.npc)
        return self.periodo in item.aparece

    def itens_presentes(self) -> List[Item]:
        return [i for i in self.itens if self.item_presente(i)]

    # ---------------------------------------------------------- examinar itens
    def custo(self, item: Item) -> int:
        ja_visto = item.id in self.vistos or (item.npc and item.npc in self.conversados)
        return 0 if ja_visto else C.CUSTO_POR_TIPO[item.tipo]

    def examinar(self, item: Item) -> Resultado:
        if self.periodo not in item.periodos:
            return Resultado("BLOQUEADO", item, item.texto_periodo)
        faltando = [f for f in item.requer if f not in self.flags]
        if faltando:
            return Resultado("BLOQUEADO", item, item.texto_bloqueado)

        custo = self.custo(item)
        self.acoes = max(0, self.acoes - custo)
        if self.periodo == NOITE:
            self.gamif.unlock("a_coruja")

        if item.npc:
            if item.npc not in self.conversados:
                self.conversados.add(item.npc)
                self._registrar_visto(item)
                if len(self.conversados) >= 3:
                    self.gamif.unlock("a_voices")
            return Resultado("DIALOGO", item, custo=custo)

        if item.id not in self.vistos:
            self._registrar_visto(item)
            for f in item.define:
                self.flags.add(f)
            if item.tipo == "EVIDENCE":
                self.registrar_evidencia(item.id)
        return Resultado("TEXTO", item, item.texto, custo=custo)

    def _registrar_visto(self, item: Item):
        self.vistos.add(item.id)
        g = self.gamif
        if item.tipo != "EVIDENCE":   # evidências dão XP ao serem registradas
            nomes = {"SECONDARY": "Informação Descoberta", "CURIOSITY": "Curiosidade Encontrada",
                     "FLAVOR": "Exploração"}
            g.add_xp(C.XP_POR_TIPO[item.tipo], nomes[item.tipo])
        n = len(self.vistos)
        if n >= 1:
            g.unlock("a_first")
        if n >= 10:
            g.unlock("a_10")
        if n >= 20:
            g.unlock("a_20")
        if self.contar("CURIOSITY") >= 5:
            g.unlock("a_curious")

    def registrar_evidencia(self, ev_id: str):
        if ev_id in self.evidencias:
            return
        self.evidencias.append(ev_id)
        self.flags.add(ev_id)
        self.gamif.add_xp(C.XP_POR_TIPO["EVIDENCE"], "Evidência Principal")
        self.gamif.add_notification(f"EVIDÊNCIA: {REGISTRO_EVIDENCIAS[ev_id][0]}", C.COLOR_ACCENT_GOLD, icon="document")
        if len(self.evidencias) == 6:
            self.gamif.unlock("a_all_ev")
            self.gamif.add_notification("Você pode convocar a audiência pública!", C.COLOR_ACCENT_GREEN)

    def contar(self, tipo: str) -> int:
        return sum(1 for i in self.itens if i.tipo == tipo and i.id in self.vistos)

    # --------------------------------------------------------------- diálogos
    def escolhas_disponiveis(self, npc_id: str) -> List[Escolha]:
        npc = NPCS[npc_id]
        feitas = self.escolhas_feitas[npc_id]
        disp = []
        for e in npc.escolhas:
            if e.id in feitas:
                continue
            if any(f not in self.flags for f in e.requer):
                continue
            if self.confianca[npc_id] < e.confianca_min:
                continue
            disp.append(e)
        return disp

    def escolher(self, npc_id: str, escolha: Escolha) -> Escolha:
        self.escolhas_feitas[npc_id].append(escolha.id)
        self.transcricoes[npc_id].append((escolha.texto, escolha.resposta))
        antes = self.confianca[npc_id]
        self.confianca[npc_id] = max(-3, antes + escolha.confianca)
        if NPCS[npc_id].mostra_confianca and escolha.confianca:
            if escolha.confianca > 0:
                self.gamif.add_notification("Seu Jair confia mais em você.", C.COLOR_ACCENT_GREEN)
            else:
                self.gamif.add_notification("Seu Jair perdeu a confiança em você.", C.COLOR_ACCENT_RED)
        if npc_id == "trabalhador" and self.confianca[npc_id] >= C.CONFIANCA_DOCUMENTO:
            self.gamif.unlock("a_confianca")
        for f in escolha.define:
            if f not in self.flags:
                self.flags.add(f)
                self._avisar_flag(f)
        if escolha.concede:
            self.registrar_evidencia(escolha.concede)
        if escolha.encerra:
            self.npc_ausente[npc_id] = (self.dia, self.periodo)
            # a opção agressiva pode ser tentada de novo outro dia, mas a confiança caiu
            self.escolhas_feitas[npc_id].remove(escolha.id)
        return escolha

    def _avisar_flag(self, f: str):
        avisos = {
            "sabe_processo": "Nova pista: processo nº 402 no arquivo da Prefeitura.",
            "acesso_escritorio": "Nova pista: a porta dos fundos do escritório, de dia.",
            "sigilo_garantido": "Nova pista: a Associação protege testemunhas.",
            "associacao_na_audiencia": "A Associação irá à audiência pública.",
            "francisca_mobilizada": "Dona Francisca vai mobilizar os pescadores.",
        }
        if f in avisos:
            self.gamif.add_notification(avisos[f], C.COLOR_ACCENT_CYAN)

    # ---------------------------------------------------------------- objetivos
    def objetivos(self):
        ev = set(self.evidencias)
        principais = [
            ("Descobrir a origem da contaminação do rio", bool(ev & {"ev1", "ev2"})),
            ("Compreender os impactos sobre a comunidade", "ev3" in ev),
            ("Ouvir quem trabalha na fábrica", "ev4" in ev),
            ("Investigar a atuação do poder público", "ev5" in ev),
            ("Conhecer a organização dos moradores", "ev6" in ev),
            (f"Reunir as seis evidências principais ({len(ev)}/6)", len(ev) == 6),
        ]
        cur = self.contar("CURIOSITY")
        n = len(self.vistos)
        secundarios = [
            (f"Conhecer a história e curiosidades da vila ({min(cur, 5)}/5)", cur >= 5),
            (f"Examinar pelo menos 20 objetos ou pessoas ({min(n, 20)}/20)", n >= 20),
            (f"Concluir os desafios de interpretação ({len(self.desafios_ok)}/3)", len(self.desafios_ok) >= 3),
            ("Garantir a presença da Associação na audiência", "associacao_na_audiencia" in self.flags),
        ]
        return principais, secundarios

    def concluir_desafio(self, desafio_id: str) -> bool:
        """Registra o desafio. Retorna True só na primeira vez (XP pago uma vez)."""
        if desafio_id in self.desafios_ok:
            return False
        self.desafios_ok.add(desafio_id)
        self.gamif.add_xp(C.XP_DESAFIO, "Desafio Concluído")
        if len(self.desafios_ok) >= 3:
            self.gamif.unlock("a_desafios")
        return True

    def registro_evidencia(self, ev_id: str) -> Optional[Tuple[str, str]]:
        return REGISTRO_EVIDENCIAS.get(ev_id)
