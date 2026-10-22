
# Consultor Inteligente de Carreiras em TI

Sistema Especialista baseado em regras, desenvolvido em **Python**, que entrevista o usuário sobre seus interesses, conhecimentos e objetivos profissionais e recomenda **uma entre dez trilhas de carreira em Tecnologia da Informação**.

O projeto utiliza **Experta** como motor de inferência e **Streamlit** para oferecer uma interface web interativa. A recomendação é acompanhada de pontuação e das regras que contribuíram para o resultado.

> **Aviso:** o resultado é uma orientação exploratória baseada nas preferências informadas. Não representa um teste psicológico, uma medida científica de aptidão ou uma garantia de sucesso profissional.

## Funcionalidades

- Questionário interativo com **10 perguntas e 67 alternativas**, apresentado uma pergunta por vez.
- **25 regras lógicas cruzadas**, utilizando fatos (`Fact`) e regras (`@Rule`) do Experta.
- Recomendação de uma das **10 carreiras** contempladas.
- Pontuação por carreira e justificativas associadas às regras ativadas.
- Resolução de empates pela afinidade com linguagem/ferramenta (Pergunta 3) ou, quando necessário, por uma pergunta adicional sobre a atividade preferida.
- Possibilidade de consultar as respostas, revisar escolhas e reiniciar a entrevista.
- Testes automatizados para regras, perfis profissionais e cenários de empate.

## Demonstração do sistema

As imagens a seguir são **capturas reais da aplicação em execução**. Elas ilustram as etapas do questionário, a apresentação dos resultados e os mecanismos de desempate.

As abas e a barra de endereços do navegador foram retiradas das imagens para destacar apenas a interface do sistema.

### Tela inicial

A página apresenta o objetivo do consultor, informa que a avaliação contém dez perguntas e oferece o botão para começar.

![Tela inicial do Consultor Inteligente de Carreiras em TI](pacote_readme_imagens/imagens/tela_inicial.png)

### Questionário interativo

O usuário responde uma pergunta de cada vez, escolhendo uma alternativa. A barra de progresso indica o andamento da entrevista.

![Pergunta sobre atividades profissionais de maior interesse](pacote_readme_imagens/imagens/pergunta_02.png)

<details>
<summary><strong>Ver as capturas das dez perguntas do questionário</strong></summary>

As imagens abaixo mostram as dez dimensões avaliadas pelo sistema. As alternativas selecionadas são ilustrativas de uma execução de teste.

#### P1 — Afinidade com matemática e estatística

![P1 — Afinidade com matemática e estatística](pacote_readme_imagens/imagens/pergunta_01.png)

#### P2 — Atividades profissionais de interesse

![P2 — Atividades profissionais de interesse](pacote_readme_imagens/imagens/pergunta_02.png)

#### P3 — Linguagens e ferramentas

![P3 — Linguagens e ferramentas](pacote_readme_imagens/imagens/pergunta_03.png)

#### P4 — Resultados desejados no trabalho

![P4 — Resultados desejados no trabalho](pacote_readme_imagens/imagens/pergunta_04.png)

#### P5 — Abordagem para resolver problemas

![P5 — Abordagem para resolver problemas](pacote_readme_imagens/imagens/pergunta_05.png)

#### P6 — Infraestrutura e segurança

![P6 — Infraestrutura e segurança](pacote_readme_imagens/imagens/pergunta_06.png)

#### P7 — Dados e inteligência artificial

![P7 — Dados e inteligência artificial](pacote_readme_imagens/imagens/pergunta_07.png)

#### P8 — Desenvolvimento de aplicações

![P8 — Desenvolvimento de aplicações](pacote_readme_imagens/imagens/pergunta_08.png)

#### P9 — Qualidade e testes de software

![P9 — Qualidade e testes de software](pacote_readme_imagens/imagens/pergunta_09.png)

#### P10 — Objetivos profissionais

![P10 — Objetivos profissionais](pacote_readme_imagens/imagens/pergunta_10.png)

</details>

### Recomendação de carreira

Após concluir as perguntas, o sistema exibe a carreira recomendada, sua pontuação e as regras que contribuíram para o resultado.

No exemplo abaixo, o sistema recomenda **Engenharia de Qualidade e Testes (QA)**, com três pontos decorrentes da regra R09.

![Recomendação de QA com pontuação e justificativa da regra R09](pacote_readme_imagens/imagens/resultado_qa.png)

### Comparação de pontuações

O painel de comparação apresenta os pontos obtidos pelas dez carreiras para a entrevista realizada.

Essa funcionalidade permite visualizar a classificação das carreiras conforme as respostas fornecidas.

![Tabela de pontuação das dez carreiras](pacote_readme_imagens/imagens/comparacao_pontuacoes.png)

### Rastreabilidade das regras

O sistema permite consultar as regras efetivamente ativadas e os motivos associados a cada uma.

Essa funcionalidade torna a recomendação transparente, permitindo compreender quais combinações de respostas contribuíram para a pontuação.

![Detalhamento das regras ativadas no resultado](pacote_readme_imagens/imagens/regras_ativadas.png)

### Conferência das respostas

Também é possível visualizar as respostas registradas e, se necessário, retornar ao questionário para revisá-las ou iniciar uma nova entrevista.

![Conferência das respostas do questionário](pacote_readme_imagens/imagens/respostas_registradas.png)

### Resolução de empates

O sistema possui mecanismos para resolver situações em que duas ou mais carreiras recebem a mesma pontuação.

Inicialmente, é considerada a afinidade com a linguagem ou ferramenta indicada na **Pergunta 3**.

Caso esse critério não seja suficiente para identificar uma única carreira, o sistema apresenta uma **pergunta adicional**, permitindo ao usuário indicar qual atividade profissional prefere realizar.

O exemplo a seguir demonstra um empate entre **Ciência de Dados e Machine Learning** e **Engenharia de Qualidade e Testes (QA)**, ambas com três pontos.

#### Pergunta adicional de desempate

Como as duas carreiras receberam pontuações iguais e o critério da Pergunta 3 não resolveu o empate, o sistema solicita ao usuário uma preferência entre as atividades correspondentes.

![Pergunta adicional para desempate entre Ciência de Dados e QA](pacote_readme_imagens/imagens/pergunta_desempate.png)

#### Recomendação final após o desempate

Nesse exemplo, o usuário selecionou a atividade relacionada a testes de software.

O sistema recomendou **Engenharia de Qualidade e Testes (QA)**, mantendo a pontuação de três pontos e informando que a escolha adicional foi utilizada para definir a recomendação.

O desempate não acrescenta pontos às carreiras: ele apenas determina a recomendação entre as candidatas empatadas.

![Resultado final após desempate com recomendação de QA](pacote_readme_imagens/imagens/recomendacao_pos_desempate.png)

#### Regras ativadas no cenário de empate

O sistema permite consultar as regras que contribuíram para a pontuação das carreiras envolvidas:

- **R03 — Ciência de Dados e Machine Learning (+3 pontos):** afinidade com matemática e interesse em modelos de inteligência artificial.
- **R09 — Engenharia de Qualidade e Testes (QA) (+3 pontos):** interesse em testes, investigação de defeitos e qualidade de software.

A imagem abaixo demonstra que ambas as regras foram ativadas, justificando a necessidade do desempate.

![Regras R03 e R09 ativadas no cenário de desempate](pacote_readme_imagens/imagens/regras_desempate.png)

## Trilhas de carreira

1. Desenvolvimento Back-end
2. Desenvolvimento Front-end e UI/UX
3. Ciência de Dados e Machine Learning
4. Engenharia de Dados
5. Cibersegurança
6. DevOps e SRE
7. Computação em Nuvem
8. Desenvolvimento Mobile
9. Engenharia de Qualidade e Testes (QA)
10. Gestão de Produtos Digitais

## Tecnologias e ambiente

- **Python** — versão utilizada no desenvolvimento: **3.12.3**.
- **Experta 1.9.4** — motor de regras e encadeamento para frente.
- **frozendict 1.2** — dependência compatível com a configuração utilizada pelo Experta neste projeto.
- **Streamlit 1.66.0** — interface web.
- **Git e GitHub** — versionamento do código.

O arquivo `motor_inferencia.py` contém um ajuste de compatibilidade para executar o Experta no ambiente Python 3.12 utilizado no desenvolvimento.

## Como instalar e executar

As instruções abaixo utilizam **Windows PowerShell**. É necessário possuir Python instalado e acesso aos arquivos do repositório.

Se o repositório estiver privado, o usuário precisará ter permissão para cloná-lo.

### 1. Obter o projeto

```powershell
git clone https://github.com/anabmaia76/consultor-carreiras-ti.git
cd consultor-carreiras-ti
```

Se o projeto já estiver disponível no computador, basta abrir o terminal na pasta `consultor-carreiras-ti`.

### 2. Criar o ambiente virtual

Com o Python 3.12 instalado:

```powershell
py -3.12 -m venv .venv
```

Os próximos comandos chamam diretamente o Python do ambiente virtual, sem exigir a ativação do ambiente no PowerShell.

### 3. Instalar as dependências

As versões das bibliotecas estão definidas no arquivo `requirements.txt`.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Iniciar o sistema

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Acesse o endereço exibido pelo Streamlit no terminal, normalmente:

`http://localhost:8501`

Para interromper o servidor no terminal, utilize **Ctrl + C**.

## Como o sistema decide

1. O usuário responde às dez perguntas sobre preferências e afinidades profissionais.
2. As respostas são declaradas como fatos no motor Experta.
3. As regras cujas condições são atendidas são ativadas e registradas com seus motivos.
4. Cada carreira acumula os pontos das regras: **até 5 pontos** dessa parcela.
5. A resposta à **Pergunta 4** acrescenta **1 ponto** à carreira correspondente, totalizando um máximo de **6 pontos por carreira**.
6. A carreira com maior pontuação é recomendada. Se houver empate, o sistema considera a **Pergunta 3**; caso isso não resulte em uma única candidata, solicita uma **atividade adicional de preferência**.
7. O desempate **não acrescenta pontos**: ele apenas define a recomendação entre carreiras empatadas.

As regras, as condições de ativação e os exemplos de aplicação estão descritos em **[Matriz de Decisão](matriz_decisao.md)**.

## Organização dos arquivos

```text
consultor-carreiras-ti/
├── .gitignore
├── app.py                    # Interface Streamlit e exibição das recomendações
├── motor_inferencia.py       # Fatos, 25 regras, pontuação e desempates
├── perguntas.py              # Enunciados e alternativas do questionário
├── matriz_decisao.md         # Tabela das regras e critérios de decisão
├── pacote_readme_imagens/
│   └── imagens/              # Capturas de tela utilizadas no README
│       ├── tela_inicial.png
│       ├── pergunta_01.png
│       ├── pergunta_02.png
│       ├── pergunta_03.png
│       ├── pergunta_04.png
│       ├── pergunta_05.png
│       ├── pergunta_06.png
│       ├── pergunta_07.png
│       ├── pergunta_08.png
│       ├── pergunta_09.png
│       ├── pergunta_10.png
│       ├── resultado_qa.png
│       ├── comparacao_pontuacoes.png
│       ├── regras_ativadas.png
│       ├── respostas_registradas.png
│       ├── pergunta_desempate.png
│       ├── recomendacao_pos_desempate.png
│       └── regras_desempate.png
├── teste_experta.py          # Verificação básica do Experta
├── teste_integrado.py        # Validação de perfis para as dez carreiras
├── teste_conflitos.py        # Cenários de empate e desempate
├── requirements.txt          # Dependências para instalação do projeto
└── README.md                 # Documentação do projeto
```

A pasta `.venv` é criada localmente e não deve ser versionada.

## Como executar os testes

A partir da pasta principal do projeto, após instalar as dependências:

**Regras individuais e funções do motor:**

```powershell
.\.venv\Scripts\python.exe motor_inferencia.py
```

**Perfis integrados das dez carreiras:**

```powershell
.\.venv\Scripts\python.exe teste_integrado.py
```

**Conflitos, empates e desempates:**

```powershell
.\.venv\Scripts\python.exe teste_conflitos.py
```

Nos testes realizados durante o desenvolvimento, foram aprovados **45 cenários individuais de regras**, **dez perfis de carreira** e **três cenários de conflito**.

Também foram testados, pela interface web, uma recomendação direta, um desempate por ferramenta, um desempate por pergunta adicional e a aplicação do limite de pontuação.

Esses testes mostram o comportamento do sistema nos casos avaliados; não representam validação estatística de recomendações para toda a população.

## Contexto acadêmico

Projeto desenvolvido para a disciplina de **Inteligência Artificial**, do curso de **Ciência da Computação**, no **Centro Universitário Presidente Antônio Carlos (UNIPAC), Barbacena**.

A matriz de decisão documenta as regras escolhidas para este protótipo de Sistema Especialista.

A ferramenta foi concebida para **exploração de interesses de carreira**, não para substituir orientação profissional individualizada.
