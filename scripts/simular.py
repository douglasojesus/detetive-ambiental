"""
Simula partidas sem abrir janela para conferir as regras do jogo.

Uso:  python scripts/simular.py
Sai com código 1 se alguma verificação falhar.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from jogo import config as C  # noqa: E402
from jogo.conteudo import ALEGACOES  # noqa: E402
from jogo.estado import Estado  # noqa: E402
from jogo.final import avaliar_resposta, calcular_final  # noqa: E402
from jogo.modelos import DIA, NOITE  # noqa: E402

falhas = []


def check(cond, msg):
    print(("  ok   " if cond else "  FALHA ") + msg)
    if not cond:
        falhas.append(msg)


def examinar(e, item_id):
    return e.examinar(e.por_id[item_id])


def conversar(e, npc_id, *escolhas):
    item = next(i for i in e.itens if i.npc == npc_id)
    res = e.examinar(item)
    assert res.tipo == "DIALOGO", (npc_id, res.tipo, res.texto)
    for esc_id in escolhas:
        disp = {x.id: x for x in e.escolhas_disponiveis(npc_id)}
        assert esc_id in disp, f"{npc_id}: opção '{esc_id}' indisponível (há {list(disp)})"
        e.escolher(npc_id, disp[esc_id])


def ate(e, periodo):
    while e.periodo != periodo:
        e.avancar_periodo()


print("1) Caminho eficiente: as 6 evidências cabem no tempo")
e = Estado()
conversar(e, "lucia", "feito", "sigilo", "audiencia")
conversar(e, "francisca", "pesca")
conversar(e, "bar", "fiscal")
examinar(e, "ev5")
check(e.acoes == C.ACOES_DIA - 4, f"dia 1 gastou 4 ações (restam {e.acoes})")
ate(e, NOITE)
examinar(e, "ev2")
conversar(e, "trabalhador", "sigilo_assoc", "empatia", "despejos", "documento")
ate(e, DIA)
examinar(e, "ev1")
check(sorted(e.evidencias) == ["ev1", "ev2", "ev3", "ev4", "ev5", "ev6"], f"6 evidências no dia {e.dia}")
check(e.dia == 2, "terminou no dia 2 de 3 (sobra tempo para explorar)")

print("2) Pistas encadeadas e dia/noite bloqueiam sem gastar ações")
e = Estado()
r = examinar(e, "ev5")
check(r.tipo == "BLOQUEADO" and e.acoes == C.ACOES_DIA, "arquivo da Prefeitura exige o número do processo")
r = examinar(e, "ev2")
check(r.tipo == "BLOQUEADO" and e.acoes == C.ACOES_DIA, "tubulação está seca durante o dia")
r = examinar(e, "ev4")
check(r.tipo == "BLOQUEADO", "trabalhador não conversa durante o turno")
r = examinar(e, "ev1")
check(r.tipo == "BLOQUEADO", "escritório exige a ajuda de alguém de dentro")
ate(e, NOITE)
check(not e.item_presente(e.por_id["ev3"]), "Dona Francisca não está na margem à noite")
check(e.item_presente(e.por_id["sec11"]), "caminhão-tanque só aparece à noite")

print("3) Confiança do trabalhador")
e = Estado()
ate(e, NOITE)
conversar(e, "trabalhador", "sigilo", "empatia")
check("ev4" in e.evidencias or "despejos" in {x.id for x in e.escolhas_disponiveis("trabalhador")},
      "com confiança 2 ele aceita falar dos despejos")
check("documento" not in {x.id for x in e.escolhas_disponiveis("trabalhador")},
      "sem a garantia da Associação ele não revela o memorando")
e2 = Estado()
ate(e2, NOITE)
conversar(e2, "trabalhador", "acusar")
check(not e2.npc_presente("trabalhador"), "após a acusação ele vai embora naquela noite")
e2.avancar_periodo(); ate(e2, NOITE)
check(e2.npc_presente("trabalhador"), "na noite seguinte ele volta")
check(e2.confianca["trabalhador"] < 0, "mas a confiança caiu")

print("4) Rever e conversar de novo não gasta ações; objetos comuns são grátis")
e = Estado()
examinar(e, "sec3"); a = e.acoes
examinar(e, "sec3"); examinar(e, "flav0")
check(e.acoes == a, "rever 'sec3' e examinar a lixeira não gastaram ações")

print("5) Fim do prazo leva à audiência")
e = Estado()
eventos = [e.avancar_periodo() for _ in range(C.TOTAL_DIAS * 2)]
check(eventos[-1] == "FIM" and e.tempo_esgotado, f"sequência de períodos: {eventos}")

print("6) Desafios pagam XP uma única vez")
e = Estado()
xp0 = e.gamif.xp
check(e.concluir_desafio("linha") and not e.concluir_desafio("linha"), "segunda conclusão é ignorada")
check(e.gamif.xp - xp0 == C.XP_DESAFIO, "XP pago uma vez")

print("7) Audiência: avaliação das respostas")
a = ALEGACOES[0]
check(avaliar_resposta(a, a.correta)[1] == "acerto", "evidência correta = acerto")
check(avaliar_resposta(a, "sec11")[1] == "parcial", "caminhão noturno = parcial na 1ª alegação")
check(avaliar_resposta(a, "ev3")[1] == "erro", "evidência sem relação = erro")
check(avaliar_resposta(a, None)[1] == "silencio", "não contestar = 0")
max_cred = len(ALEGACOES) * C.CRED_ACERTO + 3 * C.CRED_BONUS_DESAFIO + C.CRED_BONUS_ASSOCIACAO
check(max_cred >= C.CRED_ALTA, f"credibilidade máxima ({max_cred}) alcança o limiar alto ({C.CRED_ALTA})")
check(len(ALEGACOES) * C.CRED_ACERTO >= C.CRED_ALTA, "dá para chegar ao limiar alto só com acertos")

print("8) Os 5 finais")
ideal = {"responsaveis": "empresa_poder", "encaminhamento": "mp", "trabalhadores": "transicao"}
F = {"associacao_na_audiencia"}
casos = [
    (6, 12, ideal, F, "justica"),
    (6, 12, ideal, set(), "multa"),                                     # sem a Associação
    (6, 7, ideal, F, "multa"),                                          # credibilidade média
    (5, 12, ideal, F, "multa"),                                         # faltou evidência
    (6, 12, {**ideal, "responsaveis": "empresa"}, F, "multa"),          # prefeitura escapa
    (6, 12, {**ideal, "encaminhamento": "redes"}, F, "multa"),
    (6, 12, {**ideal, "encaminhamento": "fechar"}, F, "dividida"),
    (6, 12, {**ideal, "trabalhadores": "ignorar"}, F, "dividida"),
    (6, 12, {**ideal, "encaminhamento": "acordo"}, F, "silenciamento"),
    (6, 12, {**ideal, "trabalhadores": "expor"}, F, "silenciamento"),
    (6, 12, {**ideal, "responsaveis": "trabalhadores"}, F, "arquivado"),
    (6, 12, {**ideal, "responsaveis": "acidente"}, F, "arquivado"),
    (3, 12, ideal, F, "arquivado"),
    (6, 2, ideal, F, "arquivado"),
]
vistos = set()
for n, cred, resp, flags, esperado in casos:
    obtido = calcular_final(n, cred, resp, flags)
    vistos.add(obtido)
    check(obtido == esperado, f"{n} evid, cred {cred}, {resp} -> {obtido} (esperado {esperado})")
check(len(vistos) == 5, "os 5 finais são alcançáveis")

print()
if falhas:
    print(f"{len(falhas)} verificação(ões) falharam.")
    sys.exit(1)
print("Todas as verificações passaram.")
