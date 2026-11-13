# ==============================================================================
# ESTRUTURAS DE DADOS DO CONTEÚDO
# ==============================================================================
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

DIA = "DIA"
NOITE = "NOITE"
AMBOS = (DIA, NOITE)


@dataclass
class Escolha:
    """Uma pergunta/atitude que o jogador pode escolher numa conversa."""
    id: str
    texto: str                      # o que o jogador diz
    resposta: str                   # o que o personagem responde
    requer: Tuple[str, ...] = ()    # flags necessárias para a opção aparecer
    confianca_min: int = 0          # confiança mínima para a opção aparecer
    confianca: int = 0              # quanto a confiança muda ao escolher
    define: Tuple[str, ...] = ()    # flags ativadas ao escolher
    concede: str = ""               # id da evidência registrada ao escolher
    encerra: bool = False           # personagem encerra a conversa (vai embora)


@dataclass
class NPC:
    id: str
    nome: str
    papel: str
    posicoes: Dict[str, Tuple[int, int]]   # período -> (x, y do pé)
    camisa: Tuple[int, int, int]
    calca: Tuple[int, int, int]
    pele: Tuple[int, int, int]
    cabelo: Tuple[int, int, int]
    saudacao: str
    escolhas: List[Escolha] = field(default_factory=list)
    saia: bool = False
    chapeu: Optional[Tuple[int, int, int]] = None
    mostra_confianca: bool = False


@dataclass
class Item:
    """Qualquer coisa clicável no cenário (objeto ou pessoa)."""
    id: str
    tipo: str                        # EVIDENCE, SECONDARY, CURIOSITY, FLAVOR
    nome: str
    ancora: str = ""                 # chave em cenario.HOTSPOTS (objetos fixos)
    npc: str = ""                    # chave em conteudo.NPCS (pessoas)
    texto: str = ""
    icone: str = "magnifier"
    periodos: Tuple[str, ...] = AMBOS   # quando pode ser examinado
    aparece: Tuple[str, ...] = AMBOS    # quando existe na cena (só objetos)
    requer: Tuple[str, ...] = ()        # flags necessárias para examinar
    texto_periodo: str = ""             # mostrado no período errado
    texto_bloqueado: str = ""           # mostrado quando faltam flags
    define: Tuple[str, ...] = ()        # flags ativadas ao examinar


@dataclass
class Alegacao:
    quem: str
    cargo: str
    texto: str
    correta: str                         # id da evidência que desmente
    parciais: Tuple[str, ...]            # ids que ajudam parcialmente
    explicacao: str                      # por que a evidência desmente


@dataclass
class OpcaoDossie:
    id: str
    texto: str


@dataclass
class PerguntaDossie:
    id: str
    titulo: str
    opcoes: List[OpcaoDossie]


@dataclass
class Final:
    id: str
    titulo: str
    subtitulo: str
    texto: str
    reflexoes: List[str]
    cor_rio: Tuple[int, int, int]
    cor_titulo: Tuple[int, int, int]
