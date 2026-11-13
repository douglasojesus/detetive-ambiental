# Detetives Ambientais: Por Trás da Degradação

Jogo educativo 2D de investigação socioambiental (BIO 606 – Educação Ambiental, UEFS 2026.2).
O roteiro completo e as regras estão em [roteiro_detetives_ambientais.md](roteiro_detetives_ambientais.md).

## Requisitos

- **Python 3.10 ou mais recente** ([python.org/downloads](https://www.python.org/downloads/)). No Windows, marque
  a opção *"Add python.exe to PATH"* durante a instalação.
- A biblioteca **pygame-ce**, instalada pelo `requirements.txt` (passo 2 abaixo).

> **Por que pygame-ce e não pygame?** O `pygame-ce` (Community Edition) é mantido pela comunidade do Pygame,
> tem a mesma API (o código continua usando `import pygame`) e já tem versões prontas para o Python 3.15.
> O `pygame` original ainda não tem: no Python 3.15, `pip install pygame` falha ao tentar compilar.
> **Não instale os dois no mesmo ambiente**, porque eles usam o mesmo nome `pygame` e entram em conflito.

## Como executar

Todos os comandos devem ser rodados **dentro da pasta do projeto** (a que contém `main.py`).

### Windows (PowerShell)

1. Crie um ambiente virtual (só na primeira vez):

   ```powershell
   python -m venv .venv
   ```

2. Instale as dependências (só na primeira vez):

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Execute o jogo:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

Se o comando `python` não for reconhecido, troque-o por `py` no passo 1.
Também é possível ativar o ambiente com `.\.venv\Scripts\Activate.ps1` e usar apenas `python main.py`. Se o
PowerShell disser que a execução de scripts está desabilitada, use os comandos acima, que não precisam de ativação.

### Linux e macOS

```bash
python3 -m venv .venv
```

```bash
.venv/bin/python -m pip install -r requirements.txt
```

```bash
.venv/bin/python main.py
```

### Problemas comuns

| Mensagem | O que fazer |
|---|---|
| `ModuleNotFoundError: No module named 'pygame'` | O jogo foi aberto com um Python fora do ambiente virtual. Use `.\.venv\Scripts\python.exe main.py` (Windows) ou `.venv/bin/python main.py`. |
| `can't open file ... main.py` ou `requirements.txt` não encontrado | O terminal está em outra pasta. Entre na pasta do projeto (por exemplo, `cd detetive-ambiental`). |
| `ModuleNotFoundError: No module named 'jogo'` | A pasta `jogo/` está faltando: baixe o repositório completo (`git pull` ou o ZIP da branch certa). |
| Erro ao compilar `pygame` (*Failed to build pygame*) | Foi instalado `pygame` em vez do `requirements.txt`. Use o passo 2, que instala o `pygame-ce`. |
| A pasta `venv/` antiga sumiu depois de atualizar o repositório | É esperado: ela não é mais versionada. Recrie o ambiente com os passos 1 e 2. |

## Controles

- **Mouse:** clique em pessoas e objetos para examiná-los; nas conversas, clique na pergunta desejada.
- **M:** abre a mochila. **Esc:** fecha a janela aberta.
- A roda do mouse rola textos longos na mochila.
- O botão *Esperar a noite / Dormir* pede um segundo clique de confirmação quando ainda há ações sobrando.

As regras completas aparecem no menu **Como Jogar**, dentro do próprio jogo.

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

## Verificações (para quem edita o código)

Simula partidas sem abrir janela e confere as regras (tempo, pistas, confiança e os 5 finais):

```powershell
.\.venv\Scripts\python.exe scripts\simular.py
```

Gera imagens de todas as telas em `scripts/saida/` e confere se áreas clicáveis se sobrepõem ou se alguma
pessoa está fora do chão:

```powershell
.\.venv\Scripts\python.exe scripts\renderizar_cena.py
```

No Linux/macOS, use `.venv/bin/python scripts/simular.py` e `.venv/bin/python scripts/renderizar_cena.py`.
