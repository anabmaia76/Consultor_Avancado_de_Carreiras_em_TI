# Matriz de Decisão 
## 1. Objetivo

Este documento registra a base de conhecimento utilizada pelo **Consultor Inteligente de Carreiras em TI**, implementado em Python com a biblioteca **Experta**. A matriz descreve como combinações de respostas ao questionário ativam **25 regras lógicas cruzadas**, distribuindo pontos entre **10 trilhas de carreira**.

As regras abaixo correspondem aos métodos `regra_01` a `regra_25` do arquivo `motor_inferencia.py`. As respostas são representadas pelos códigos `P1` a `P10`, definidos no arquivo `perguntas.py`.

## 2. Perguntas e dimensões consideradas

| Código | Dimensão avaliada | Respostas |
|---|---|---|
| P1 | Afinidade com matemática e estatística | `baixa`, `media`, `alta` |
| P2 | Atividade profissional de maior interesse | A a I |
| P3 | Linguagem ou ferramenta de maior afinidade | A a I |
| P4 | Entrega de valor preferida | A a J |
| P5 | Abordagem preferida para resolver problemas | A a F |
| P6 | Infraestrutura e segurança | A a F |
| P7 | Dados e inteligência artificial | A a F |
| P8 | Desenvolvimento de aplicações | A a F |
| P9 | Qualidade e testes de software | A a F |
| P10 | Objetivo de atuação profissional | A a F |

**Observação:** os códigos das alternativas devem ser interpretados conforme os enunciados e descrições de `perguntas.py`; uma letra não tem necessariamente o mesmo significado em perguntas diferentes.

## 3. Matriz das 25 regras de inferência

A coluna *Condição de ativação* apresenta combinações lógicas com **E** (ambas as condições necessárias), **OU** (pelo menos uma alternativa) e **∈** (pertence ao conjunto indicado).

| Regra | Trilha de carreira | Condição de ativação | Pontos |
|---|---|---|---:|
| R01 | Desenvolvimento Back-end | P2 = A **E** P8 ∈ {A, D, E} | +3 |
| R02 | Desenvolvimento Front-end e UI/UX | P2 = B **E** P8 ∈ {B, D} | +3 |
| R03 | Ciência de Dados e Machine Learning | P1 ∈ {`media`, `alta`} **E** P7 = B | +3 |
| R04 | Engenharia de Dados | P2 = D **E** P7 ∈ {C, D} | +3 |
| R05 | Cibersegurança | P2 = E **E** P6 = A | +3 |
| R06 | DevOps e SRE | P2 = F **E** P6 = B | +3 |
| R07 | Computação em Nuvem | P4 = G **E** P6 = C | +3 |
| R08 | Desenvolvimento Mobile | P2 = G **E** P8 = C | +3 |
| R09 | Engenharia de Qualidade e Testes (QA) | P2 = H **E** P9 ∈ {A, B, C, D, E} | +3 |
| R10 | Gestão de Produtos Digitais | P2 = I **E** P10 = F | +3 |
| R11 | Ciência de Dados e Machine Learning | P7 = B **E** (P5 = C **OU** P10 = C) | +2 |
| R12 | Engenharia de Dados | P4 = D **E** P7 = D | +2 |
| R13 | Cibersegurança | P6 = A **E** (P5 = D **OU** P10 = E) | +2 |
| R14 | Engenharia de Qualidade e Testes (QA) | P4 = I **E** P9 = D | +2 |
| R15 | DevOps e SRE | P4 = F **E** P6 = E | +2 |
| R16 | Desenvolvimento Back-end | P4 = A **E** (P5 = A **OU** P10 = A) | +2 |
| R17 | Desenvolvimento Front-end e UI/UX | P4 = B **E** (P5 = B **OU** P10 = B) | +2 |
| R18 | Computação em Nuvem | P6 = C **E** (P2 = F **OU** P10 = D) | +2 |
| R19 | Desenvolvimento Mobile | P4 = H **E** P8 = C | +2 |
| R20 | Gestão de Produtos Digitais | P4 = J **E** P5 = F | +2 |
| R21 | Ciência de Dados e Machine Learning | P2 = C **E** P7 ∈ {A, E} | +2 |
| R22 | Engenharia de Dados | P4 = D **E** P7 = C | +2 |
| R23 | Engenharia de Qualidade e Testes (QA) | P4 = I **E** (P5 = D **OU** P10 = E) | +2 |
| R24 | Cibersegurança | P4 = E **E** P6 = A | +2 |
| R25 | DevOps e SRE | P5 = E **E** P6 ∈ {B, D} | +2 |

Cada regra é registrada apenas uma vez por entrevista, mesmo quando mais de uma condição alternativa de uma expressão **OU** é satisfeita.

## 4. Distribuição das regras por carreira

| Trilha | Regras associadas |
|---|---|
| Desenvolvimento Back-end | R01, R16 |
| Desenvolvimento Front-end e UI/UX | R02, R17 |
| Ciência de Dados e Machine Learning | R03, R11, R21 |
| Engenharia de Dados | R04, R12, R22 |
| Cibersegurança | R05, R13, R24 |
| DevOps e SRE | R06, R15, R25 |
| Computação em Nuvem | R07, R18 |
| Desenvolvimento Mobile | R08, R19 |
| Engenharia de Qualidade e Testes (QA) | R09, R14, R23 |
| Gestão de Produtos Digitais | R10, R20 |

## 5. Cálculo da pontuação

1. O motor identifica as regras ativadas e registra seus pontos e justificativas.
2. Para **cada carreira**, a pontuação obtida pelas regras é limitada a **5 pontos**: `min(soma_das_regras, 5)`.
3. A resposta da **P4** acrescenta **1 ponto** à carreira que corresponde à entrega de valor preferida.
4. Assim, a pontuação final de cada carreira varia de **0 a 6 pontos**.
5. A maior pontuação determina as carreiras candidatas à recomendação.

**Correspondência da P4:** A → Back-end; B → Front-end/UI/UX; C → Ciência de Dados; D → Engenharia de Dados; E → Cibersegurança; F → DevOps/SRE; G → Nuvem; H → Mobile; I → QA; J → Gestão de Produtos.

**Exemplo — Cibersegurança:** R05 (+3), R13 (+2) e R24 (+2) somam 7 pontos brutos. O limite reduz essa parcela a 5 pontos; se P4 = E, acrescenta-se 1 ponto, totalizando **6 pontos**. As três regras continuam aparecendo na justificativa, pois foram efetivamente ativadas.

## 6. Critérios de desempate

Quando duas ou mais carreiras têm a mesma maior pontuação:

1. O sistema verifica a resposta da **P3**, relacionando a ferramenta indicada às carreiras compatíveis. Se restar exatamente uma candidata, ela é recomendada, sem alterar a pontuação.
2. Se a P3 não distinguir uma única carreira, o sistema apresenta **uma pergunta adicional**, composta apenas pelas atividades correspondentes às carreiras ainda empatadas.
3. A preferência indicada nessa pergunta define a recomendação, **sem acrescentar pontos**.

**Compatibilidade utilizada pela P3:**

| P3 | Linguagem/ferramenta | Carreiras consideradas compatíveis no desempate |
|---|---|---|
| A | C | Back-end, Cibersegurança |
| B | C++ | Back-end, Cibersegurança |
| C | C# | Back-end, Mobile |
| D | Python | Back-end, Ciência de Dados, Engenharia de Dados, QA, DevOps/SRE |
| E | HTML / CSS / JavaScript | Front-end/UI/UX, Back-end, Mobile |
| F | Java | Back-end, Mobile |
| G | SQL / Bancos de Dados | Engenharia de Dados, Back-end, Ciência de Dados |
| H | Linux / Redes | Cibersegurança, DevOps/SRE, Computação em Nuvem |
| I | Nenhuma / Iniciante | Nenhuma compatibilidade usada para desempatar |

Se a ferramenta não for compatível com nenhuma das carreiras empatadas, todas as empatadas seguem para a pergunta adicional. Se for compatível com mais de uma delas, somente essas candidatas seguem para a pergunta adicional.

## 7. Exemplos de rastreabilidade

| Perfil de teste | Regras relevantes | Resultado esperado |
|---|---|---|
| QA: P2 = H, P4 = I, P5 = D, P9 = A, P10 = E | R09 (+3), R23 (+2), P4 (+1) | QA: 6 pontos |
| Cibersegurança: P2 = E, P4 = E, P5 = D, P6 = A | R05 (+3), R13 (+2), R24 (+2), limite de 5 e P4 (+1) | Cibersegurança: 6 pontos |
| Conflito: P1 = alta, P2 = H, P3 = I, P4 = J, P5 = A, P6 = F, P7 = B, P8 = F, P9 = A, P10 = F | R03 (+3) para Ciência de Dados e R09 (+3) para QA | Empate com pergunta adicional |
| Mesmo conflito, mas P3 = G (SQL) | Mesma pontuação das duas carreiras | Ciência de Dados por desempate da P3, com 3 pontos |

Os cenários de teste estão implementados em `teste_integrado.py` e `teste_conflitos.py`; outros testes de regras individuais estão incluídos em `motor_inferencia.py`.

## 8. Arquivos relacionados

- `perguntas.py`: enunciados, descrições das alternativas e códigos válidos.
- `motor_inferencia.py`: declaração dos fatos, implementação das 25 regras, pontuação e desempate.
- `app.py`: interface Streamlit, coleta de respostas e apresentação da recomendação com justificativas.
- `teste_integrado.py`: validação de dez perfis representando as dez trilhas.
- `teste_conflitos.py`: validação de empates e critérios de desempate.

**Nota metodológica:** esta matriz documenta a lógica definida para o sistema e os critérios de pontuação adotados no projeto; a recomendação é orientativa, não uma medida objetiva ou probabilística de aptidão profissional.
