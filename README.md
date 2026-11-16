# Detetives Ambientais: Por Trás da Degradação

**Relatório do jogo educativo** — BIO 606: Educação Ambiental (UEFS, 2026.2)  
Docente: Profa. Viviane Souza Martins  
Desenvolvimento: Douglas Oliveira de Jesus e Antonio Vitor Costa da Silva

O roteiro narrativo completo, com todos os textos e personagens, está em
[roteiro_detetives_ambientais.md](roteiro_detetives_ambientais.md).

## Sumário

1. [Apresentação](#1-apresentação)
2. [Ficha do jogo](#2-ficha-do-jogo)
3. [Como instalar e executar](#3-como-instalar-e-executar)
4. [Instruções de jogo](#4-instruções-de-jogo)
5. [Passo a passo com gabarito](#5-passo-a-passo-com-gabarito)
6. [Por que é um jogo](#6-por-que-é-um-jogo)
7. [A Educação Ambiental Crítica no jogo](#7-a-educação-ambiental-crítica-no-jogo)
8. [Potencialidades e limitações](#8-potencialidades-e-limitações)
9. [Estrutura do código e verificações](#9-estrutura-do-código-e-verificações)
10. [Referências](#10-referências)

---

## 1. Apresentação

Em Vila das Águas, uma comunidade de pescadores artesanais, o Rio das Pedras escureceu, os peixes morreram e as
famílias perderam o sustento. Ao lado do rio funciona a Vale das Pedras S.A., maior empregadora da cidade. O jogador
assume o papel de um detetive ambiental que tem **três dias** para investigar o caso antes de uma **audiência
pública**.

A proposta não é apenas descobrir "quem poluiu". Para vencer, o jogador precisa entender **por que** a poluição
aconteceu e **por que** foi tolerada: a decisão econômica da diretoria, o medo de demissão dos operários, a omissão
da Prefeitura e a resistência organizada da comunidade. No fim, ele precisa decidir o que fazer com as provas. As
escolhas levam a **cinco finais diferentes**, e só um deles representa justiça socioambiental.

## 2. Ficha do jogo

| Item | Descrição |
|---|---|
| **Nome** | Detetives Ambientais: Por Trás da Degradação |
| **Gênero** | Investigação 2D *point-and-click*, com gestão de tempo e escolhas com consequências |
| **Objetivo** | Reunir as seis evidências principais, desmentir o discurso oficial em uma audiência pública e propor um encaminhamento justo para o conflito socioambiental |
| **Participantes** | 1 jogador. Também pode ser jogado em grupo, com projeção em sala, e as decisões discutidas coletivamente antes de cada clique |
| **Público** | Estudantes do ensino médio e superior, e educadores em espaços formais e não formais |
| **Duração estimada** | De 20 a 40 minutos por partida. A rejogabilidade vem dos cinco finais |
| **Plataforma** | Computador (Windows, Linux ou macOS) com Python 3.10+ e pygame-ce |
| **Abordagem pedagógica** | Educação Ambiental Crítica e Justiça Socioambiental |

## 3. Como instalar e executar

**Requisitos:** **Python 3.10 ou mais recente** ([python.org/downloads](https://www.python.org/downloads/)). No
Windows, marque *"Add python.exe to PATH"* na instalação. A biblioteca gráfica, **pygame-ce**, é instalada no
passo 2.

> **Por que pygame-ce?** É a edição mantida pela comunidade do Pygame, com a mesma API (o código usa
> `import pygame`) e versões prontas para o Python 3.15. O `pygame` original ainda não tem: no Python 3.15,
> `pip install pygame` falha ao compilar. **Não instale os dois no mesmo ambiente.**

Rode todos os comandos **dentro da pasta do projeto**, a que contém `main.py`.

### Windows (PowerShell)

1. Crie o ambiente virtual (só na primeira vez):

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

Se `python` não for reconhecido, use `py` no passo 1. Esses comandos não exigem ativar o ambiente virtual.

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
| `ModuleNotFoundError: No module named 'pygame'` | O jogo foi aberto com um Python fora do ambiente virtual. Use o comando do passo 3. |
| `can't open file ... main.py` ou `requirements.txt` não encontrado | O terminal está em outra pasta. Entre na pasta do projeto (por exemplo, `cd detetive-ambiental`). |
| `ModuleNotFoundError: No module named 'jogo'` | A pasta `jogo/` está faltando. Baixe o repositório completo. |
| Erro ao compilar `pygame` (*Failed to build pygame*) | Foi instalado `pygame` em vez do `requirements.txt`. Use o passo 2. |
| A pasta `venv/` antiga sumiu depois de atualizar o repositório | É esperado: ela não é mais versionada. Recrie o ambiente com os passos 1 e 2. |

## 4. Instruções de jogo

### 4.1. Objetivo

Reunir as **6 evidências principais**, convocar a **audiência pública**, desmentir as alegações da empresa e da
Prefeitura e montar um **dossiê final** que leve ao melhor desfecho para o rio e para a comunidade.

### 4.2. Controles

| Comando | Ação |
|---|---|
| Clique em pessoa ou objeto | Examina ou inicia uma conversa |
| Clique em uma opção de diálogo | Escolhe o que perguntar ou dizer |
| **MOCHILA** ou tecla **M** | Abre os registros: evidências, informações, curiosidades, conversas, objetivos e conquistas |
| **DESAFIOS** | Abre os três desafios de interpretação |
| **Esperar a noite / Dormir** | Avança o tempo. Pede um segundo clique de confirmação se ainda houver ações sobrando |
| **Convocar audiência** | Aparece depois que as 6 evidências forem reunidas |
| **Esc** | Fecha a janela aberta |
| Roda do mouse | Rola textos longos na mochila |

Ao passar o mouse sobre um elemento, aparece o nome dele e o custo para examiná-lo: "1 ação", "grátis",
"já examinado", "você precisa de uma pista" ou "fechado / indisponível neste horário".

### 4.3. Regras

**Tempo.** A investigação dura **3 dias**. Cada dia tem um período de **DIA, com 5 ações**, e um de **NOITE, com
3 ações**. Quando as ações acabam, o período avança sozinho.

| Ação | Custo |
|---|---|
| Examinar pela primeira vez uma evidência, uma informação secundária ou uma curiosidade (inclusive a primeira conversa com um personagem) | 1 ação |
| Examinar um objeto comum | grátis |
| Rever qualquer registro ou conversar de novo com quem você já conheceu | grátis |
| Escolher perguntas dentro de uma conversa | grátis |
| Tentar algo indisponível (lugar fechado ou pista faltando) | grátis (aparece uma dica) |
| Fazer os desafios | grátis |

**Dia e noite.** De dia, Prefeitura, escola e mercadinho funcionam, e Dona Francisca está na margem do rio. À noite,
esses lugares fecham, mas a tubulação despeja efluentes, um caminhão-tanque sai da fábrica às escondidas e o operário
Seu Jair pode conversar longe do supervisor.

**Pistas encadeadas.** Algumas evidências só ficam acessíveis depois de outras descobertas (ver o passo a passo,
seção 5).

**Conversas e confiança.** As perguntas disponíveis mudam conforme o que você já descobriu. Seu Jair tem um medidor de
**confiança** (0 a 3): empatia e garantia de sigilo aumentam a confiança; acusá-lo derruba a confiança e faz com que
ele vá embora naquela noite.

**Prazo.** Se os 3 dias acabarem antes de você convocar a audiência, ela acontece mesmo assim, com as provas que você
tiver reunido.

**Audiência pública.** São seis alegações. Para cada uma, apresente um registro da mochila:

| Resposta | Credibilidade |
|---|---:|
| Evidência que desmente a alegação | +2 |
| Informação secundária relacionada (argumento parcial) | +1 |
| Não contestar | 0 |
| Registro sem relação | −1 |
| Bônus: cada desafio concluído | +1 |
| Bônus: Associação de Moradores presente | +1 |

**Dossiê e finais.** Três perguntas definem o desfecho, junto com a credibilidade e o número de evidências
(ver a seção 5.6).

### 4.4. Pontuação

A pontuação é em XP: evidência, 100; desafio, 100; informação secundária, 40; curiosidade, 20; objeto comum, 5.
Os níveis são Observador, Explorador, Investigador, Analista e Detetive Ambiental. Há 11 conquistas, listadas na
mochila.

## 5. Passo a passo com gabarito

> **Atenção: esta seção revela as soluções.** Ela serve para professores e avaliadores e para quem quiser conferir
> o caminho até o melhor final. O roteiro abaixo foi verificado com a simulação das regras do jogo
> (`scripts/simular.py`).

### 5.1. Mapa das evidências e o que destrava cada uma

| # | Evidência | Onde | Quando | O que é preciso |
|---|---|---|---|---|
| 1 | Memorando interno da diretoria | Prédio "Administração" da fábrica (alto, à direita) | Dia | Seu Jair revelar a porta dos fundos (confiança 3) |
| 2 | Laudo da tubulação de descarte | Saída de concreto na margem do rio, abaixo da fábrica | **Noite** | Nada: basta ir à noite |
| 3 | Depoimento de Dona Francisca | Margem do rio, ao lado da casa de madeira | Dia | Perguntar sobre a pesca ou sobre a saúde |
| 4 | Depoimento de Seu Jair | De dia no portão da fábrica (não fala); **à noite no ponto de ônibus** | **Noite** | Confiança 2 ou mais |
| 5 | Processo de fiscalização nº 402/26 | Prefeitura (alto, à esquerda) | Dia | Saber o número do processo (Seu Zé, no bar) |
| 6 | Dossiê da Associação de Moradores | Dona Lúcia, na porta da Associação | Dia | Perguntar o que a Associação tem feito |

### 5.2. Roteiro recomendado (melhor final)

**Dia 1 — DIA (5 ações)**

1. **Dona Lúcia** (Associação de Moradores), 1 ação. Escolha, nesta ordem:
   - "O que a Associação tem feito sobre o rio?" → **Evidência 6**.
   - "Vocês protegem quem quer denunciar?" → libera a garantia de sigilo para Seu Jair.
   - "Se houver uma audiência pública, a Associação vai?" → a Associação estará presente (+1 de credibilidade e
     requisito do melhor final).
   - "Onde mais eu deveria procurar?" (opcional) → dica do bar e do despejo noturno.
2. **Dona Francisca** (margem do rio), 1 ação. "O que aconteceu com a pesca?" → **Evidência 3**. As outras
   perguntas são opcionais e enriquecem o debate.
3. **Seu Zé** (bar), 1 ação. "O que sabem sobre a fiscalização?" → descobre o processo 402.
4. **Prefeitura**, 1 ação → **Evidência 5**.
5. Ação livre, sugestão: **Aviso no Posto de Saúde**. Na audiência, ele serve de argumento parcial na alegação
   sobre saúde.

**Dia 1 — NOITE (3 ações)**

6. **Tubulação de Descarte** (margem do rio), 1 ação → **Evidência 2**.
7. **Seu Jair** (ponto de ônibus), 1 ação. Escolha:
   - "Seu nome não vai aparecer. A Associação de Moradores protege quem denuncia." → confiança +2.
   - "Sei como é depender do emprego. Não quero prejudicar vocês..." → confiança +1 (total 3).
   - "Você sabe sobre os despejos no rio?" → **Evidência 4**.
   - "Existe algum documento que prove que a ordem veio de cima?" → revela a porta dos fundos do escritório.
   - **Nunca** escolha "Você é cúmplice disso!": ele vai embora e a confiança cai.
8. Ação livre, sugestão: **Caminhão-Tanque Noturno** (só aparece à noite).

**Dia 2 — DIA**

9. **Escritório da Fábrica** ("Administração"), 1 ação → **Evidência 1**. As 6 evidências estão completas.
10. Volte a **Dona Francisca** (grátis) e escolha "[Mostrar o laudo da tubulação]". Ela mobiliza os pescadores, e a
    Câmara fica mais cheia na audiência.
11. Faça os **três desafios** (grátis, gabarito na seção 5.3). Cada um vale +1 de credibilidade.
12. Use o tempo que sobrar para conhecer curiosidades e informações secundárias. Depois clique em
    **Convocar audiência**.

### 5.3. Gabarito dos desafios

**Linha do Tempo** (do mais antigo ao mais recente):

1. A Vila das Águas é fundada por pescadores artesanais (1952).
2. A Vale das Pedras expande suas atividades industriais na região.
3. A diretoria corta 65% do orçamento da estação de tratamento.
4. Começam os despejos irregulares noturnos no rio.
5. Peixes morrem e surgem problemas de pele na comunidade.
6. O processo de fiscalização é engavetado na Prefeitura.

**Análise do Discurso** (frase do outdoor → evidência que a desmente):

| Frase da propaganda | Evidência |
|---|---|
| "A empresa atua com responsabilidade ambiental e tratamento adequado." | Laudo da Tubulação (ou Memorando Interno) |
| "As atividades da fábrica trazem prosperidade para toda a população." | Depoimento de Dona Francisca |
| "A empresa tem uma relação ética e transparente com a cidade." | Processo de Fiscalização nº 402/26 |

**Mapa de Atores:**

| Quem lucra | Quem sofre os danos | Quem deveria fiscalizar | Quem se organiza |
|---|---|---|---|
| Vale das Pedras S.A. | Pescadores ribeirinhos; Operários da fábrica; Comerciantes da vila | Prefeitura | Associação de Moradores |

### 5.4. Gabarito da audiência pública

| # | Quem fala | Alegação | Resposta correta (+2) | Argumentos parciais (+1) |
|---|---|---|---|---|
| 1 | Dr. Mendonça (empresa) | "Nosso efluente é tratado conforme a legislação." | Laudo da Tubulação | Caminhão-Tanque Noturno |
| 2 | Dr. Mendonça | "A empresa nunca reduziu seus investimentos ambientais." | Memorando Interno | — |
| 3 | Sr. Valdemar (Prefeitura) | "A Prefeitura fiscaliza todas as empresas com rigor." | Processo nº 402/26 | Seu Zé (bar) |
| 4 | Sr. Valdemar | "Nunca recebemos reclamação formal dos moradores." | Dossiê da Associação | — |
| 5 | Dr. Mendonça | "Não existe prejuízo à saúde ou à renda da população." | Depoimento de Dona Francisca | Aviso do Posto, Seu Antônio, Horta, Barco |
| 6 | Dr. Mendonça | "Se houvesse irregularidade, os funcionários denunciariam." | Depoimento de Seu Jair | Quadro de Empregos, Rafael |

Com as 6 respostas corretas, os 3 desafios e a Associação presente, a credibilidade chega a **16**. O mínimo para o
melhor final é 10.

### 5.5. Gabarito do dossiê final (melhor final)

1. **Quem é responsável?** → "A empresa, que poluiu para lucrar, e o poder público, que engavetou a fiscalização."
2. **O que fazer com as provas?** → "Entregar o dossiê ao Ministério Público, junto com a Associação de Moradores."
3. **E os trabalhadores e a renda da vila?** → "Proteger a testemunha e exigir transição justa..."

### 5.6. Como chegar a cada um dos cinco finais

| Final | Condição (verificada nesta ordem) |
|---|---|
| **Caso Arquivado** | Culpar "os operários" ou "um acidente", **ou** ter menos de 4 evidências, **ou** credibilidade abaixo de 4 |
| **Acordo de Bastidores** | Escolher o acordo sigiloso com a diretoria, **ou** expor o nome de Seu Jair |
| **Fábrica Fechada, Vila Dividida** | Exigir o fechamento imediato da fábrica, **ou** ignorar os trabalhadores |
| **Justiça Socioambiental** | As três respostas da seção 5.5, as 6 evidências, credibilidade ≥ 10 e a Associação presente |
| **Multa como "Risco Calculado"** | Qualquer outro caso: denúncia correta, mas incompleta (por exemplo, culpar só a empresa, apostar só nas redes sociais ou não levar a Associação) |

Ao final, o jogo mostra perguntas de reflexão ligadas ao desfecho e a mensagem central da proposta.

### 5.7. Conquistas

| Conquista | Como obter |
|---|---|
| Primeiro Contato | Examinar qualquer elemento |
| Olhar Atento / Explorador da Vila | Examinar 10 / 20 elementos (os objetos comuns são grátis e contam) |
| Investigação Completa | Reunir as 6 evidências |
| Curioso por Natureza | Descobrir 5 curiosidades |
| Vozes da Comunidade | Conversar com 3 personagens |
| Coruja | Examinar algo à noite |
| Confiança Conquistada | Levar a confiança de Seu Jair a 3 |
| Pensamento Crítico | Concluir os 3 desafios |
| Argumentação Sólida | Acertar as 6 alegações da audiência |
| Justiça Ambiental | Alcançar o final de Justiça Socioambiental |

## 6. Por que é um jogo

Huizinga (2019) descreve o jogo como uma atividade voluntária, com regras próprias, tempo e espaço delimitados e
tensão em relação ao resultado. Salen e Zimmerman (2012) o definem como um sistema em que os jogadores enfrentam um
conflito artificial, definido por regras, que termina em um resultado quantificável. *Detetives Ambientais* tem todos
esses elementos:

| Elemento | Como aparece no jogo |
|---|---|
| **Objetivo claro** | Reunir 6 evidências, vencer a audiência e alcançar um desfecho justo |
| **Regras explícitas** | Custo de ações, dia e noite, pistas encadeadas, confiança, pontuação da audiência e condições dos finais (seção 4) |
| **Conflito e desafio** | O jogador disputa a narrativa com a empresa e a Prefeitura e enfrenta obstáculos: lugares fechados, informantes desconfiados e prazo |
| **Recursos escassos** | 24 ações no total para cerca de 25 elementos que custam ação: não dá para ver tudo, é preciso **priorizar** |
| **Decisões significativas** | As escolhas nos diálogos mudam a confiança e as pistas; as respostas na audiência mudam a credibilidade; o dossiê define o final |
| **Resultado quantificável e variável** | Credibilidade, XP, níveis, conquistas e **5 finais** distintos |
| **Feedback imediato** | Notificações de XP, novas pistas, mudança de confiança, resultado de cada alegação |
| **Incerteza e rejogabilidade** | O jogador não sabe de antemão o que cada escolha provoca; os finais estimulam novas partidas com decisões diferentes |
| **Ambiente lúdico próprio** | Uma vila fictícia, personagens com voz própria e ciclo de dia e noite |

O jogo também foge do modelo de "quiz disfarçado". O conhecimento não é cobrado em perguntas soltas: ele é
**necessário para jogar bem**. Para desmentir uma alegação, é preciso entender o que cada documento prova. Para ganhar
a confiança de um operário, é preciso reconhecer sua vulnerabilidade, não acusá-lo. E para chegar ao melhor final, é
preciso compreender o conflito como um todo.

## 7. A Educação Ambiental Crítica no jogo

A Educação Ambiental Crítica entende a crise ambiental como expressão de relações sociais, econômicas e políticas
desiguais. Ela não a reduz a comportamentos individuais nem a soluções apenas técnicas (LOUREIRO, 2004; GUIMARÃES,
2004). Layrargues e Lima (2014) distinguem essa macrotendência crítica das abordagens conservacionista e pragmática,
que tratam o problema sem questionar o modelo de desenvolvimento. A Política Nacional de Educação Ambiental
(BRASIL, 1999) também prevê, entre seus objetivos, a compreensão integrada do meio ambiente em suas dimensões
ecológicas, políticas, sociais, econômicas e éticas, e o estímulo à participação coletiva como exercício de
cidadania.

O jogo traduz esses princípios em mecânicas:

| Princípio da EA Crítica | Como o jogo o materializa |
|---|---|
| **O problema ambiental é socialmente produzido** | O memorando mostra que a poluição foi uma decisão de diretoria ("multas como risco calculado"), não um acidente. A Linha do Tempo reforça essa leitura. |
| **Injustiça ambiental: os danos recaem sobre os mais vulneráveis** (ACSELRAD; MELLO; BEZERRA, 2009) | Pescadores, crianças e comerciantes sofrem os efeitos enquanto o lucro fica com a empresa. O desafio Mapa de Atores explicita quem lucra e quem sofre. |
| **Crítica ao discurso hegemônico do "desenvolvimento"** | O outdoor ("o motor do desenvolvimento") e as falas na audiência precisam ser confrontados com provas. A Análise do Discurso trabalha a "maquiagem verde". |
| **Papel e responsabilidade do Estado** | O processo 402 engavetado e as doações de campanha mostram a captura do poder público. Culpar só a empresa leva a um final apenas parcial. |
| **Recusa a culpar indivíduos** | Atribuir a culpa aos operários ou a um "acidente" leva ao final Caso Arquivado. Acusar Seu Jair faz o informante ir embora. |
| **Trabalho e ambiente não são inimigos** | O dilema "emprego ou rio limpo" é apresentado como uma armadilha. Exigir o fechamento imediato gera desemprego e deixa o passivo ambiental. O melhor final exige **transição justa**. |
| **Participação social e organização coletiva** | Sem a Associação de Moradores, não há sigilo para a testemunha, não há memorando nem melhor final. A presença da Associação na audiência soma credibilidade. |
| **Direito à informação e instrumentos de cidadania** | O jogador pede vista do processo com base na Lei de Acesso à Informação (BRASIL, 2011). O melhor final envolve o Ministério Público e um Termo de Ajustamento de Conduta. |
| **Território, memória e cultura** | As curiosidades (fundação da vila em 1952, Festa de São Pedro, foto dos pescadores, árvore das reuniões) mostram que o rio é modo de vida, não só recurso. |
| **Reflexão, não resposta pronta** | Cada final termina com perguntas de reflexão, e os finais "ruins" são plausíveis, não punições arbitrárias: mostram consequências reais de escolhas comuns. |

Assim, a pergunta do jogo deixa de ser "quem sujou o rio?" e passa a ser "que relações permitem que o rio seja sujo,
e como a sociedade pode transformá-las?". Essa é a mensagem central da proposta.

## 8. Potencialidades e limitações

**Potencialidades**

- Abordagem sistêmica do conflito: economia, trabalho, saúde, poder público e organização popular aparecem
  interligados.
- A aprendizagem acontece pela ação e pela consequência, com cinco finais que permitem comparar caminhos.
- Funciona individualmente ou em grupo, e as perguntas de reflexão podem abrir um debate depois da partida.
- Todo o texto fica em um único arquivo (`jogo/conteudo.py`), o que facilita adaptar o caso a outras realidades locais.

**Limitações**

- Exige computador com Python instalado. Não roda em celular nem direto no navegador.
- O caso é fictício e simplificado. Situações reais envolvem mais atores, como órgãos estaduais, a Justiça e a
  imprensa, e mais tempo.
- As escolhas são pré-definidas: o jogador não formula soluções próprias. Isso reforça a importância de um debate
  mediado depois da partida.
- O jogo não tem som e ainda não passou por testes com o público-alvo.

## 9. Estrutura do código e verificações

| Arquivo | Conteúdo |
|---|---|
| `main.py` | Ponto de entrada |
| `jogo/conteudo.py` | **Todos os textos**: objetos, diálogos, alegações, dossiê e finais |
| `jogo/config.py` | Balanceamento: dias, ações, custos, XP e limiares dos finais |
| `jogo/estado.py` | Regras: tempo, pistas, confiança, evidências e conquistas |
| `jogo/cenario.py` | Desenho da vila, das pessoas e do ciclo de dia e noite |
| `jogo/ui.py` | Mochila, conversas, inspeção e desafios |
| `jogo/final.py` | Audiência pública, dossiê e cálculo dos finais |
| `jogo/jogo.py` | Loop principal, HUD e máquina de estados |

Para quem edita o código, há duas verificações automáticas (no Linux/macOS, troque o caminho por `.venv/bin/python`).
A primeira simula partidas sem abrir janela e confere as regras e os 5 finais:

```powershell
.\.venv\Scripts\python.exe scripts\simular.py
```

A segunda gera imagens de todas as telas em `scripts/saida/` e confere o layout do cenário:

```powershell
.\.venv\Scripts\python.exe scripts\renderizar_cena.py
```

## 10. Referências

ACSELRAD, H.; MELLO, C. C. A.; BEZERRA, G. N. **O que é justiça ambiental**. Rio de Janeiro: Garamond, 2009.

BRASIL. **Lei nº 9.795, de 27 de abril de 1999**. Dispõe sobre a educação ambiental, institui a Política Nacional de
Educação Ambiental e dá outras providências. Brasília, DF, 1999.

BRASIL. **Lei nº 12.527, de 18 de novembro de 2011**. Regula o acesso a informações. Brasília, DF, 2011.

GUIMARÃES, M. **A formação de educadores ambientais**. Campinas: Papirus, 2004.

HUIZINGA, J. **Homo ludens**: o jogo como elemento da cultura. São Paulo: Perspectiva, 2019.

LAYRARGUES, P. P.; LIMA, G. F. C. As macrotendências político-pedagógicas da educação ambiental brasileira.
**Ambiente & Sociedade**, São Paulo, v. 17, n. 1, p. 23-40, 2014.

LOUREIRO, C. F. B. **Trajetória e fundamentos da educação ambiental**. São Paulo: Cortez, 2004.

SALEN, K.; ZIMMERMAN, E. **Regras do jogo**: fundamentos do design de jogos. São Paulo: Blucher, 2012. v. 1.

---

**Uso de inteligência artificial:** IA generativa (Gemini e Claude) foi utilizada como ferramenta de apoio à
codificação do jogo e à redação deste documento.
