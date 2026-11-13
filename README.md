# Detetives Ambientais: Por Trás da Degradação

Jogo educativo 2D de investigação socioambiental (BIO 606 – Educação Ambiental, UEFS 2026.2).
O roteiro completo e as regras estão em [roteiro_detetives_ambientais.md](roteiro_detetives_ambientais.md).

## Como rodar

Requer Python 3.8 ou mais recente.

```bash
python -m venv .venv
```

No Windows, ative com `.venv\Scripts\activate`; no Linux/macOS, com `source .venv/bin/activate`. Depois:

```bash
pip install -r requirements.txt
```

```bash
python main.py
```

O jogo usa o `pygame-ce`, versão compatível do Pygame (o código continua usando `import pygame`).
O `pygame` original não compila no Python 3.15.

## Estrutura do código

| Arquivo | Conteúdo |
|---|---|
| `main.py` | Ponto de entrada |
| `jogo/conteudo.py` | **Todos os textos**: objetos, diálogos, alegações da audiência, dossiê e finais |
| `jogo/config.py` | Balanceamento: dias, ações por período, custos, XP e limiares dos finais |
| `jogo/estado.py` | Regras: tempo, pistas, confiança, evidências, conquistas |
| `jogo/cenario.py` | Desenho da vila, das pessoas e do ciclo dia/noite (áreas clicáveis em `HOTSPOTS`) |
| `jogo/ui.py` | Mochila, conversas, inspeção e desafios |
| `jogo/final.py` | Audiência pública, dossiê e cálculo dos 5 finais |
| `jogo/jogo.py` | Loop principal, HUD e máquina de estados |

## Verificações

```bash
python scripts/simular.py
```

Simula partidas sem abrir janela e confere as regras: tempo, pistas, confiança e os 5 finais.

```bash
python scripts/renderizar_cena.py
```

Gera imagens de todas as telas em `scripts/saida/` e confere se áreas clicáveis se sobrepõem ou se alguma pessoa está fora do chão.
