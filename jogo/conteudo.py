# ==============================================================================
# CONTEÚDO DO JOGO: TEXTOS, PERSONAGENS, DIÁLOGOS, AUDIÊNCIA E FINAIS
# A equipe pode editar os textos aqui sem mexer na lógica do jogo.
# ==============================================================================
from .modelos import (Alegacao, AMBOS, DIA, Escolha, Final, Item, NOITE, NPC,
                      OpcaoDossie, PerguntaDossie)

# ------------------------------------------------------------------------------
# REGISTROS DAS EVIDÊNCIAS (o que fica salvo na Mochila)
# ------------------------------------------------------------------------------
REGISTRO_EVIDENCIAS = {
    "ev1": ("Memorando Interno da Diretoria",
            "MEMORANDO INTERNO — DIRETORIA EXECUTIVA\n\n\"Diante da necessidade de maximizar lucros, fica aprovada a "
            "redução de 65% nos custos operacionais da Estação de Tratamento. Eventuais multas devem ser tratadas "
            "como risco calculado, pois são inferiores ao custo de tratamento.\"\n\n"
            "O que revela: a poluição foi uma decisão econômica da diretoria, e não um acidente."),
    "ev2": ("Laudo da Tubulação de Descarte",
            "LAUDO TÉCNICO DE INSPEÇÃO\n\n\"Identificada tubulação subterrânea lançando efluentes sem tratamento no rio. "
            "Amostras atestam metais pesados 14x acima do limite. A descarga ocorre à noite para burlar a "
            "fiscalização visual.\"\n\n"
            "O que revela: há prova técnica de que o efluente chega ao rio sem tratamento."),
    "ev3": ("Depoimento de Dona Francisca",
            "\"De uns meses pra cá, a água ficou pesada, com cheiro químico. Os peixes boiaram mortos. Minha neta "
            "começou com feridas vermelhas na pele. Nós somos pobres, dependemos do rio e ficamos presos na "
            "contaminação.\"\n\n"
            "O que revela: quem sofre primeiro os danos são as famílias que dependem diretamente do rio."),
    "ev4": ("Depoimento do Trabalhador da Fábrica",
            "\"Todo mundo no chão de fábrica sabe. A ordem vem direto da gerência. Desligam os filtros de madrugada. "
            "Se a gente falar, é rua.\"\n\n"
            "O que revela: as irregularidades são conhecidas internamente, mas o medo do desemprego silencia "
            "os trabalhadores."),
    "ev5": ("Processo de Fiscalização nº 402/26",
            "PROCESSO DE FISCALIZAÇÃO PARALISADO Nº 402/26\n\n\"Auto de infração propondo interdição cautelar. Processo "
            "retido no gabinete com parecer: 'Aguardando momento oportuno devido ao impacto na arrecadação "
            "tributária'. Anexos mostram doações da empresa para campanhas.\"\n\n"
            "O que revela: o poder público sabia da infração e engavetou a fiscalização."),
    "ev6": ("Dossiê da Associação de Moradores",
            "DOSSIÊ DE MOBILIZAÇÃO\n\n\"Compilado de 14 ofícios enviados aos órgãos públicos sem resposta. A comunidade "
            "formou um comitê autônomo para exigir saneamento e responsabilização.\"\n\n"
            "O que revela: a comunidade denunciou várias vezes e se organizou diante do silêncio das autoridades."),
}

# ------------------------------------------------------------------------------
# PERSONAGENS E DIÁLOGOS
# Posições = (x, y do pé) no cenário. Se um período não estiver listado,
# o personagem não está na cena nesse período.
# ------------------------------------------------------------------------------
NPCS = {
    "francisca": NPC(
        "francisca", "Dona Francisca", "Pescadora e moradora ribeirinha",
        {DIA: (455, 600)},
        camisa=(170, 90, 120), calca=(90, 60, 80), pele=(150, 105, 75), cabelo=(200, 200, 200), saia=True,
        saudacao="Bom dia, moço. Veio ver o estrago no nosso rio? Pode perguntar, que eu respondo.",
        escolhas=[
            Escolha("pesca", "O que aconteceu com a pesca?",
                    "De uns meses pra cá, a água ficou pesada, com cheiro químico. Os peixes boiaram mortos. "
                    "A gente não tem mais como tirar sustento daqui.", concede="ev3"),
            Escolha("saude", "Alguém da família adoeceu?",
                    "Minha neta começou com feridas vermelhas na pele. Nós somos pobres, dependemos do rio "
                    "e ficamos presos na contaminação.", concede="ev3"),
            Escolha("prefeitura", "A prefeitura ajudou?",
                    "Só promessas. Eles vêm aqui em época de eleição, mas na hora de enfrentar a fábrica, todos somem. "
                    "O pessoal do bar vive falando de um tal processo que ficou parado..."),
            Escolha("ficar", "Por que a senhora não se muda daqui?",
                    "Meu pai ajudou a fundar essa vila em 1952, muito antes dessa fábrica. Aqui é minha casa, meu "
                    "trabalho, minha história. Por que quem sujou o rio fica, e quem vive dele é que tem que sair?"),
            Escolha("laudo", "[Mostrar o laudo da tubulação] Olhe o resultado da análise da água.",
                    "Metal pesado catorze vezes acima do limite... Então não era coisa da nossa cabeça! Vou levar "
                    "isso pra Associação hoje mesmo. Agora ninguém vai dizer que é invenção de pescador.",
                    requer=("ev2",), define=("francisca_mobilizada",)),
        ]),

    "trabalhador": NPC(
        "trabalhador", "Seu Jair", "Operário da Vale das Pedras",
        {DIA: (930, 272), NOITE: (782, 348)},
        camisa=(230, 170, 40), calca=(50, 60, 90), pele=(120, 80, 55), cabelo=(30, 25, 20), chapeu=(230, 200, 40),
        mostra_confianca=True,
        saudacao="(Ele está cansado, esperando o ônibus depois do turno. Olha para os lados antes de responder.) "
                 "...Boa noite. O que você quer?",
        escolhas=[
            Escolha("empatia", "Sei como é depender do emprego. Não quero prejudicar vocês, quero entender quem deu as ordens.",
                    "(Ele relaxa um pouco os ombros.) Pelo menos alguém entende que a gente não manda em nada lá dentro.",
                    confianca=1),
            Escolha("sigilo_assoc", "Seu nome não vai aparecer. A Associação de Moradores protege quem denuncia.",
                    "A Dona Lúcia? Ela é séria, ajudou meu cunhado uma vez. Se for com ela... talvez eu possa falar.",
                    requer=("sigilo_garantido",), confianca=2),
            Escolha("sigilo", "Prometo que seu nome não vai aparecer.",
                    "Promessa é fácil. Quem vai me proteger depois, quando a fábrica descobrir?",
                    confianca=1),
            Escolha("acusar", "Você é cúmplice disso! Vou denunciar você também.",
                    "(Ele se levanta, irritado.) Cúmplice? Eu tenho três filhos pra criar! Esquece que me viu. "
                    "(Ele vai embora a pé, sem esperar o ônibus.)",
                    confianca=-2, encerra=True),
            Escolha("despejos", "Você sabe sobre os despejos no rio?",
                    "Todo mundo no chão de fábrica sabe. A ordem vem direto da gerência. Desligam os filtros de "
                    "madrugada.", confianca_min=2, concede="ev4"),
            Escolha("denuncia", "Por que ninguém denuncia?",
                    "Se a gente falar, é rua. 'Tem cem na porta querendo sua vaga', eles dizem. Ficamos reféns do "
                    "medo do desemprego.", confianca_min=2, concede="ev4"),
            Escolha("organizar", "Vocês não se organizam?",
                    "É difícil. A empresa usa nossa necessidade contra nós. Ameaçam fechar a fábrica se houver "
                    "pressão ambiental. Se tivesse garantia de emprego, muita gente falava.", confianca_min=2),
            Escolha("documento", "Existe algum documento que prove que a ordem veio de cima?",
                    "(Ele baixa a voz.) Tem um memorando da diretoria cortando o dinheiro da estação de tratamento. "
                    "Fica na sala de reuniões da administração. Amanhã cedo, na troca de turno, a porta dos fundos "
                    "fica aberta. Mas você não ouviu isso de mim.",
                    confianca_min=3, define=("acesso_escritorio",)),
        ]),

    "lucia": NPC(
        "lucia", "Dona Lúcia", "Presidente da Associação de Moradores",
        {DIA: (600, 272)},
        camisa=(60, 130, 90), calca=(70, 50, 40), pele=(95, 65, 45), cabelo=(25, 20, 20), saia=True,
        saudacao="Seja bem-vindo à Associação! Faz tempo que a gente espera alguém de fora que queira ouvir a vila.",
        escolhas=[
            Escolha("feito", "O que a Associação tem feito sobre o rio?",
                    "Juntamos tudo num dossiê: 14 ofícios mandados à prefeitura e aos órgãos ambientais. Nenhuma "
                    "resposta. Então formamos um comitê para exigir saneamento e responsabilização. Pode levar uma cópia.",
                    concede="ev6"),
            Escolha("sigilo", "Vocês protegem quem quer denunciar?",
                    "Sim. Quem tem medo fala com a gente em sigilo, e nós levamos o caso ao Ministério Público sem "
                    "expor ninguém. Muito operário sabe das coisas, mas tem medo de perder o emprego.",
                    define=("sigilo_garantido",)),
            Escolha("audiencia", "Se houver uma audiência pública, a Associação vai?",
                    "Se você convocar, a gente enche a Câmara! Pescador, comerciante, professora, todo mundo. "
                    "Audiência vazia é fácil de ignorar; cheia, não.",
                    define=("associacao_na_audiencia",)),
            Escolha("pistas", "Onde mais eu deveria procurar?",
                    "No bar falam muito do processo que o fiscal abriu e que sumiu na prefeitura. E dizem que a "
                    "fábrica só solta a sujeira de madrugada... alguém precisava ver isso de perto."),
        ]),

    "comerciante": NPC(
        "comerciante", "Seu Antônio", "Dono do Mercadinho",
        {DIA: (172, 436)},
        camisa=(220, 220, 210), calca=(80, 70, 60), pele=(200, 150, 110), cabelo=(90, 70, 50),
        saudacao="Bom dia! Vai levar alguma coisa? Anda tão parado que qualquer freguês é festa.",
        escolhas=[
            Escolha("vendas", "Como estão as vendas?",
                    "Caíram muito. O pessoal da pesca não tem mais renda, então ninguém compra. A economia da vila "
                    "inteira gira em torno do rio."),
            Escolha("fabrica", "O senhor também depende da fábrica?",
                    "Metade da minha freguesia é operário. Se a fábrica fecha, eu fecho junto. Por isso ninguém aqui "
                    "quer ver a fábrica fechada... a gente quer ver ela funcionando direito."),
        ]),

    "ponto": NPC(
        "ponto", "Rafael", "Operário a caminho do turno",
        {DIA: (806, 348)},
        camisa=(70, 120, 170), calca=(40, 40, 50), pele=(170, 120, 85), cabelo=(20, 20, 20),
        saudacao="E aí? Tô esperando a condução pro turno da tarde.",
        escolhas=[
            Escolha("conducao", "Esperando condução?",
                    "Sim, indo pro turno da fábrica. A gente reclama da poluição, mas sem essa empresa, metade da "
                    "cidade passa fome. É uma armadilha."),
            Escolha("tratamento", "E se a fábrica tratasse os resíduos direito?",
                    "Aí era o melhor dos mundos: emprego e rio limpo. Mas dizem lá dentro que tratar não dá lucro. "
                    "Lucro pra quem, né?"),
        ]),

    "bar": NPC(
        "bar", "Seu Zé do Bar", "Morador e frequentador do bar",
        {DIA: (312, 442), NOITE: (312, 442)},
        camisa=(180, 70, 60), calca=(60, 60, 70), pele=(110, 75, 50), cabelo=(150, 150, 150),
        saudacao="Senta aí! Aqui no bar a gente resolve os problemas do mundo... só não resolve os da vila.",
        escolhas=[
            Escolha("conversa", "Sobre o que vocês conversam?",
                    "A gente discute como o prefeito não faz nada. Ele tem rabo preso com os donos da fábrica. "
                    "O lucro fica lá, a sujeira fica aqui."),
            Escolha("fiscal", "O que sabem sobre a fiscalização?",
                    "O Seu Jorge, fiscal da prefeitura, autuou a fábrica ano passado. Processo 402. Pediu até "
                    "interdição! Tá parado no gabinete do prefeito até hoje. Vai lá no arquivo e pede pra ver.",
                    define=("sabe_processo",)),
            Escolha("prefeito", "Por que o prefeito não age?",
                    "Campanha é cara, né? Quem paga a banda escolhe a música. E a fábrica paga muito imposto."),
        ]),
}

# ------------------------------------------------------------------------------
# OBJETOS E PESSOAS CLICÁVEIS
# ------------------------------------------------------------------------------
def criar_itens():
    itens = [
        # --- EVIDÊNCIAS PRINCIPAIS (6) ---
        Item("ev1", "EVIDENCE", "Escritório da Fábrica", ancora="escritorio", icone="document",
             periodos=(DIA,), requer=("acesso_escritorio",),
             texto_periodo="O prédio administrativo está trancado, e um vigia faz a ronda com uma lanterna. "
                           "Não é hora de entrar aqui.",
             texto_bloqueado="A recepcionista barra sua entrada: 'Área restrita a funcionários.' Talvez alguém "
                             "de dentro da fábrica saiba como chegar aos documentos...",
             texto="Na troca de turno, você entra pela porta dos fundos que Seu Jair mencionou. Na sala de reuniões, "
                   "fotografa um documento sobre a mesa:\n\n" + REGISTRO_EVIDENCIAS["ev1"][1].split("\n\nO que")[0]),
        Item("ev2", "EVIDENCE", "Tubulação de Descarte", ancora="tubulacao", icone="registry",
             periodos=(NOITE,),
             texto_periodo="Uma saída de concreto meio escondida pela vegetação da margem. Agora está seca, mas há "
                           "manchas escuras nas pedras e um cheiro químico no ar. O que será que acontece aqui "
                           "fora do horário comercial?",
             texto="Pouco depois da meia-noite, a tubulação começa a despejar um líquido escuro e espumoso. Você "
                   "coleta uma amostra e envia ao laboratório da universidade. O resultado chega rápido:\n\n"
                   + REGISTRO_EVIDENCIAS["ev2"][1].split("\n\nO que")[0]),
        Item("ev3", "EVIDENCE", "Dona Francisca (Pescadora)", npc="francisca", icone="speech"),
        Item("ev4", "EVIDENCE", "Seu Jair (Trabalhador da Fábrica)", npc="trabalhador", icone="speech",
             periodos=(NOITE,),
             texto_periodo="Ele está no portão, sob o olhar do supervisor. Sem virar o rosto, cochicha: "
                           "'Aqui não. Depois do turno, à noite, no ponto de ônibus.'"),
        Item("ev5", "EVIDENCE", "Prefeitura (Arquivo)", ancora="prefeitura", icone="document",
             periodos=(DIA,), requer=("sabe_processo",),
             texto_periodo="A Prefeitura está fechada. O expediente é só durante o dia.",
             texto_bloqueado="O atendente do protocolo é educado, mas firme: 'Sem o número do processo, não posso "
                             "liberar nada do arquivo.' Alguém na vila deve saber qual é esse processo...",
             texto="Com o número 402 em mãos, você pede vista do processo, um direito garantido pela Lei de Acesso à "
                   "Informação. Depois de muita espera, o atendente traz uma pasta empoeirada:\n\n"
                   + REGISTRO_EVIDENCIAS["ev5"][1].split("\n\nO que")[0]),
        Item("ev6", "EVIDENCE", "Dona Lúcia (Associação de Moradores)", npc="lucia", icone="speech"),

        # --- INFORMAÇÕES SECUNDÁRIAS ---
        Item("sec1", "SECONDARY", "Seu Antônio (Mercadinho)", npc="comerciante", icone="speech"),
        Item("sec2", "SECONDARY", "Mural da Escola", ancora="mural_escola", periodos=(DIA,),
             texto_periodo="Está escuro demais para enxergar os desenhos do mural.",
             texto="Trabalhos das crianças do 4º ano. Os desenhos mostram o rio escuro e peixinhos chorando. "
                   "A degradação já faz parte do imaginário infantil da vila."),
        Item("sec3", "SECONDARY", "Aviso no Posto de Saúde", ancora="aviso_posto",
             texto="\"ATENÇÃO: Devido ao aumento de casos de dermatite de contato e viroses, evitem utilizar a água "
                   "do rio para banho ou lavagem de roupas.\""),
        Item("sec4", "SECONDARY", "Outdoor da Fábrica", ancora="outdoor",
             texto="\"VALE DAS PEDRAS S.A. — O motor do desenvolvimento! Gerando 500 empregos diretos e construindo "
                   "o futuro da nossa cidade.\"\n\nNenhuma palavra sobre o rio."),
        Item("sec5", "SECONDARY", "Rafael (Ponto de Ônibus)", npc="ponto", icone="speech"),
        Item("sec6", "SECONDARY", "Horta Comunitária", ancora="horta",
             texto="O agricultor colocou uma placa: 'Não estamos irrigando com água do rio'. Mesmo assim, as folhas "
                   "de algumas hortaliças estão amareladas. O lençol freático pode estar contaminado."),
        Item("sec7", "SECONDARY", "Seu Zé (Bar da Comunidade)", npc="bar", icone="speech"),
        Item("sec8", "SECONDARY", "Quadro de Empregos", ancora="quadro_empregos",
             texto="Diversas vagas para 'Auxiliar de Produção'. Os salários são baixos, mas a fila de currículos é "
                   "imensa, o que mostra a forte dependência econômica da região."),
        Item("sec9", "SECONDARY", "Barco Abandonado", ancora="barco",
             texto="Um barco de madeira rachado, encalhado na margem. O nome 'Esperança' está quase apagado. "
                   "Há meses não sai para pescar."),
        Item("sec10", "SECONDARY", "Placa de Área de Preservação", ancora="placa_app",
             texto="Uma placa enferrujada de 15 anos atrás: 'Área de Preservação Permanente'. Hoje restam tocos de "
                   "árvores cortadas e lixo. Sem a mata ciliar, a margem desmorona e o rio fica mais vulnerável."),
        Item("sec11", "SECONDARY", "Caminhão-Tanque Noturno", ancora="caminhao", aparece=(NOITE,),
             texto="Um caminhão-tanque sem identificação sai pelos fundos da fábrica de madrugada, com os faróis "
                   "apagados até chegar à estrada. Para onde vai essa carga, e por que às escondidas?"),

        # --- CURIOSIDADES LOCAIS ---
        Item("cur1", "CURIOSITY", "Placa do Rio", ancora="placa_rio",
             texto="O nome 'Rio das Pedras' surgiu no século XIX, por causa das grandes rochas que formavam "
                   "piscinas naturais cristalinas no verão."),
        Item("cur2", "CURIOSITY", "Árvore Centenária", ancora="arvore",
             texto="Uma imensa figueira. Os mais velhos dizem que as primeiras reuniões da comunidade aconteceram "
                   "sob a sombra desta árvore."),
        Item("cur3", "CURIOSITY", "Pedra Fundamental", ancora="pedra",
             texto="Placa de bronze: 'Vila das Águas — Fundada por pescadores artesanais em 1952'. A vila existe "
                   "desde antes da chegada da indústria."),
        Item("cur4", "CURIOSITY", "Cachorro Caramelo", ancora="cachorro",
             texto="Um cãozinho comunitário dormindo tranquilamente. Todo mundo da vila cuida dele um pouco."),
        Item("cur5", "CURIOSITY", "Campo de Futebol", ancora="campo",
             texto="Restos de um antigo campo de terra. Com o avanço das margens degradadas e o mau cheiro do rio, "
                   "as crianças pararam de jogar bola aqui."),
        Item("cur6", "CURIOSITY", "Cartazes da Festa", ancora="mural_festa",
             texto="Restos de cartazes da 'Festa de São Pedro', padroeiro dos pescadores. Nos últimos anos, a festa "
                   "perdeu força pela falta de peixe."),
        Item("cur7", "CURIOSITY", "Flor na Janela", ancora="flor",
             texto="Um pequeno vaso de Kalanchoe, a flor-da-fortuna, na janela. Alguém cuida dessa planta com "
                   "carinho, usando adubo natural."),
        Item("cur8", "CURIOSITY", "Fotografia Antiga", ancora="foto_bar",
             texto="Pendurada na parede do bar, uma foto em preto e branco mostra dezenas de pescadores felizes "
                   "segurando redes cheias. Um passado não tão distante."),

        # --- OBJETOS COMUNS ---
        Item("flav0", "FLAVOR", "Lixeira", ancora="lixeira",
             texto="Uma lixeira cheia. A coleta parece não passar por aqui há dias."),
        Item("flav1", "FLAVOR", "Banco da Praça", ancora="banco", texto="Um banco de madeira desgastado pelo tempo."),
        Item("flav2", "FLAVOR", "Bicicleta", ancora="bicicleta",
             texto="Uma bicicleta antiga, principal meio de transporte local."),
        Item("flav3", "FLAVOR", "Poste de Luz", ancora="poste",
             texto="Poste com fios emaranhados e uma lâmpada queimada. À noite, esta parte da vila fica no escuro."),
        Item("flav4", "FLAVOR", "Caixa de Ferramentas", ancora="ferramentas",
             texto="Equipamentos de manutenção esquecidos perto de uma tampa de bueiro. Por baixo dela, dá para ouvir "
                   "um cano correndo em direção ao rio..."),
        Item("flav5", "FLAVOR", "Carrinho de Mão", ancora="carrinho",
             texto="Usado para transportar terra e verduras da horta comunitária."),
        Item("flav6", "FLAVOR", "Placa de Trânsito", ancora="placa_transito",
             texto="Placa indicando limite de velocidade para os caminhões da fábrica. Bastante enferrujada."),
        Item("flav7", "FLAVOR", "Tambores Industriais", ancora="tambores",
             texto="Tambores vazios largados perto da margem, fora do pátio da fábrica. Alguns têm resíduos "
                   "escorrendo para o chão."),
        Item("flav8", "FLAVOR", "Caixotes", ancora="caixas", texto="Caixotes de madeira vazios perto do mercadinho."),
        Item("flav9", "FLAVOR", "Telefone Público", ancora="orelhao",
             texto="Um orelhão antigo que não funciona há anos."),
        Item("flav10", "FLAVOR", "Luzes da Fábrica", ancora="galpao", aparece=(NOITE,),
             texto="O galpão funciona a todo vapor de madrugada. Curioso: a estação de tratamento ao lado está "
                   "com as luzes apagadas."),
    ]
    return itens


# ------------------------------------------------------------------------------
# AUDIÊNCIA PÚBLICA: ALEGAÇÕES QUE O JOGADOR PRECISA CONTESTAR
# ------------------------------------------------------------------------------
ALEGACOES = [
    Alegacao("Dr. Mendonça", "Diretor jurídico da Vale das Pedras",
             "Nosso efluente é tratado conforme a legislação. Nenhuma gota sem tratamento chega ao Rio das Pedras.",
             "ev2", ("sec11",),
             "O laudo da tubulação comprova o lançamento de efluentes sem tratamento, com metais pesados 14 vezes "
             "acima do limite."),
    Alegacao("Dr. Mendonça", "Diretor jurídico da Vale das Pedras",
             "A empresa nunca reduziu seus investimentos ambientais. Sustentabilidade é nosso compromisso.",
             "ev1", (),
             "O memorando da própria diretoria aprova um corte de 65% no tratamento e trata as multas como "
             "'risco calculado'."),
    Alegacao("Sr. Valdemar", "Secretário Municipal de Meio Ambiente",
             "A Prefeitura fiscaliza todas as empresas com rigor e imparcialidade.",
             "ev5", ("sec7",),
             "O processo 402/26 pedia interdição e está parado no gabinete, enquanto a empresa doou para campanhas."),
    Alegacao("Sr. Valdemar", "Secretário Municipal de Meio Ambiente",
             "Nunca recebemos nenhuma reclamação formal dos moradores sobre o rio.",
             "ev6", (),
             "O dossiê da Associação reúne 14 ofícios enviados aos órgãos públicos, todos sem resposta."),
    Alegacao("Dr. Mendonça", "Diretor jurídico da Vale das Pedras",
             "Não existe qualquer prejuízo à saúde ou à renda da população. A vila prospera com a fábrica.",
             "ev3", ("sec3", "sec1", "sec6", "sec9"),
             "Dona Francisca relata peixes mortos, perda de renda e a neta com feridas na pele."),
    Alegacao("Dr. Mendonça", "Diretor jurídico da Vale das Pedras",
             "Se houvesse alguma irregularidade, nossos próprios funcionários já teriam denunciado.",
             "ev4", ("sec8", "sec5"),
             "Seu Jair conta que todos sabem dos despejos, mas que o medo da demissão impede qualquer denúncia."),
]

# ------------------------------------------------------------------------------
# DOSSIÊ FINAL
# ------------------------------------------------------------------------------
PERGUNTAS_DOSSIE = [
    PerguntaDossie("responsaveis", "1. Quem é responsável pela contaminação do Rio das Pedras?", [
        OpcaoDossie("trabalhadores", "Os operários, que desligam os filtros durante a madrugada."),
        OpcaoDossie("empresa", "A diretoria da Vale das Pedras, que decidiu cortar o tratamento."),
        OpcaoDossie("empresa_poder", "A empresa, que poluiu para lucrar, e o poder público, que engavetou a fiscalização."),
        OpcaoDossie("acidente", "Ninguém em especial: foi uma falha técnica, um acidente."),
    ]),
    PerguntaDossie("encaminhamento", "2. O que fazer com as provas reunidas?", [
        OpcaoDossie("mp", "Entregar o dossiê ao Ministério Público, junto com a Associação de Moradores."),
        OpcaoDossie("redes", "Publicar tudo nas redes sociais e esperar a repercussão."),
        OpcaoDossie("acordo", "Negociar em sigilo com a diretoria um acordo para eles pararem."),
        OpcaoDossie("fechar", "Exigir o fechamento imediato e definitivo da fábrica."),
    ]),
    PerguntaDossie("trabalhadores", "3. E os trabalhadores e a renda da vila?", [
        OpcaoDossie("expor", "Revelar o nome de Seu Jair como testemunha principal, para dar peso à denúncia."),
        OpcaoDossie("transicao", "Proteger a testemunha e exigir transição justa: adequação ambiental com manutenção "
                                 "dos empregos, auxílio aos pescadores e reparação dos danos."),
        OpcaoDossie("ignorar", "Isso não é problema da investigação. O foco é só o rio."),
    ]),
]

# ------------------------------------------------------------------------------
# FINAIS
# ------------------------------------------------------------------------------
FINAIS = {
    "justica": Final(
        "justica", "JUSTIÇA SOCIOAMBIENTAL", "O rio volta a ser de quem vive dele",
        "Com a Câmara lotada e provas sólidas, o Ministério Público abre uma ação civil pública. A Vale das Pedras "
        "assina um Termo de Ajustamento de Conduta: religa a estação de tratamento, paga a recuperação do rio e da "
        "mata ciliar e financia um auxílio aos pescadores enquanto a pesca se recupera. Nenhum operário é demitido "
        "por denunciar.\n\nO processo 402 é destravado, e a fiscalização passa a ter um conselho com participação da "
        "Associação. Um ano depois, Dona Francisca volta a pescar. A Festa de São Pedro tem peixe outra vez.",
        ["Que medidas combinaram reparação ambiental, proteção dos trabalhadores e garantia de renda?",
         "Por que a presença da comunidade na audiência fez diferença?",
         "O que impede que a mesma situação se repita em outro lugar?"],
        cor_rio=(50, 120, 170), cor_titulo=(80, 200, 130)),
    "multa": Final(
        "multa", "MULTA COMO \"RISCO CALCULADO\"", "Uma vitória que custa barato para quem poluiu",
        "A denúncia repercute, e a Vale das Pedras é multada. Mas o valor é menor que o custo de tratar os "
        "efluentes, exatamente como previa o memorando da diretoria. A empresa paga, faz uma campanha publicitária "
        "sobre 'compromisso ambiental' e reduz os despejos por alguns meses.\n\nSem mudança estrutural, sem "
        "fiscalização permanente e sem a comunidade no centro das decisões, o rio continua turvo. A pesca não volta.",
        ["Por que uma multa pode ser apenas um 'custo do negócio' para uma grande empresa?",
         "Qual é a responsabilidade do poder público, além da empresa?",
         "O que faltou para que a mudança fosse duradoura?"],
        cor_rio=(55, 95, 85), cor_titulo=(235, 180, 50)),
    "dividida": Final(
        "dividida", "FÁBRICA FECHADA, VILA DIVIDIDA", "O problema mudou de lugar, mas não acabou",
        "A pressão pelo fechamento imediato funciona: a fábrica é interditada e encerra as atividades. Quinhentas "
        "famílias perdem a renda de uma vez, o mercadinho fecha, e operários e pescadores passam a se culpar uns aos "
        "outros.\n\nA empresa se muda para outra cidade e deixa para trás tanques e solo contaminados. Ninguém "
        "paga a recuperação do rio. A vila ficou mais pobre, e o Rio das Pedras continua doente.",
        ["Por que os trabalhadores podem ter dificuldade para denunciar irregularidades?",
         "É possível proteger o meio ambiente sem abandonar quem depende da fábrica?",
         "Quem deveria pagar pela recuperação do rio?"],
        cor_rio=(40, 62, 58), cor_titulo=(215, 120, 65)),
    "silenciamento": Final(
        "silenciamento", "ACORDO DE BASTIDORES", "Quando a denúncia é silenciada",
        "A diretoria recebe você muito bem. Promete 'resolver internamente', oferece patrocínio à Festa de São Pedro "
        "e pinta um novo outdoor verde: 'Vale das Pedras: amiga do rio'.\n\nNa semana seguinte, Seu Jair é "
        "demitido por 'corte de pessoal'. Os outros operários entendem o recado. Os despejos continuam de "
        "madrugada, agora com mais cuidado para ninguém ver.",
        ["Por que acordos sem transparência e sem participação social tendem a proteger quem tem mais poder?",
         "O que é 'maquiagem verde' (greenwashing)?",
         "Como proteger quem denuncia?"],
        cor_rio=(30, 48, 45), cor_titulo=(200, 90, 160)),
    "arquivado": Final(
        "arquivado", "CASO ARQUIVADO", "Sem provas sólidas, a culpa recai sobre os mais fracos",
        "Na audiência, os advogados da empresa e o secretário municipal desmontam a denúncia com facilidade. O caso "
        "é arquivado por 'falta de provas', e a versão oficial ganha força: foi uma falha pontual, ou culpa de "
        "operários descuidados.\n\nA Associação continua mandando ofícios, mas agora com menos esperança. O rio "
        "segue escurecendo.",
        ["Quem se beneficia economicamente da atividade industrial?",
         "Por que culpar indivíduos ou 'acidentes' esconde as decisões que produzem a degradação?",
         "Que evidências faltaram para sustentar a denúncia?"],
        cor_rio=(28, 40, 38), cor_titulo=(215, 75, 65)),
}

ORDEM_FINAIS = ["justica", "multa", "dividida", "silenciamento", "arquivado"]

MENSAGEM_CENTRAL = ("Enfrentar a degradação ambiental exige mais do que identificar a fonte da poluição. É necessário "
                    "compreender as relações sociais e econômicas que permitem que os danos aconteçam e fortalecer a "
                    "participação coletiva na busca por justiça ambiental.")

# ------------------------------------------------------------------------------
# TEXTOS DAS TELAS
# ------------------------------------------------------------------------------
COMO_JOGAR = (
    "COMO JOGAR\n\n"
    "Você é um detetive ambiental investigando a contaminação do Rio das Pedras. Clique em pessoas e objetos para "
    "examiná-los. Tudo o que descobrir fica salvo na MOCHILA.\n\n"
    "TEMPO: a investigação dura 3 dias. Cada dia tem um período de DIA (5 ações) e de NOITE (3 ações). Examinar algo "
    "novo gasta 1 ação; objetos comuns e rever registros não gastam nada. Use o botão de esperar para passar o tempo.\n\n"
    "DIA E NOITE: alguns lugares só abrem de dia, e certas coisas só acontecem à noite. Preste atenção nas dicas.\n\n"
    "CONVERSAS: escolha o que perguntar. Algumas perguntas só aparecem depois de outras descobertas, e há quem só "
    "fale se confiar em você. Cuidado com as palavras.\n\n"
    "AUDIÊNCIA: com as 6 evidências principais, convoque a audiência pública. Se o prazo acabar, ela acontece com o "
    "que você tiver. Lá você deve desmentir as alegações com as provas certas e, por fim, montar o dossiê final. "
    "Suas escolhas levam a 5 finais diferentes.\n\n"
    "DESAFIOS: atividades de interpretação que dão XP e preparo extra para a audiência.\n\n"
    "(Clique para voltar)")

CREDITOS = (
    "DETETIVES AMBIENTAIS: POR TRÁS DA DEGRADAÇÃO\n\n"
    "Desenvolvimento:\n- Douglas Oliveira de Jesus\n- Antonio Vitor Costa da Silva\n\n"
    "Atividade acadêmica:\nAtividade avaliativa da segunda unidade da disciplina BIO 606 – Educação Ambiental (2026.2).\n"
    "Docente:\nProfa. Viviane Souza Martins.\n\n"
    "Tecnologia:\nPython 3 e Pygame (pygame-ce).\n\n"
    "Uso de inteligência artificial:\nIA generativa (Gemini e Claude) utilizada parcialmente como ferramenta de apoio "
    "à codificação do jogo.\n\n"
    "Abordagem pedagógica:\nEducação Ambiental Crítica e Justiça Socioambiental.\n\n(Clique para voltar)")

INTRO = (
    "Vila das Águas, comunidade de pescadores às margens do Rio das Pedras.\n\n"
    "A água escureceu, os peixes morreram, e as famílias perderam o sustento. Ao lado do rio funciona a Vale das "
    "Pedras S.A., maior empregadora da cidade.\n\n"
    "Você tem 3 dias para descobrir o que está acontecendo antes da audiência pública. Não basta achar quem poluiu: "
    "é preciso entender por que isso foi permitido, e o que fazer a respeito.\n\n"
    "(Clique para começar)")
