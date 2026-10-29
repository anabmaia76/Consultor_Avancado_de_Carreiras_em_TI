# Matriz de Decisão e Engenharia do Conhecimento

**Projeto:** Consultor Avançado de Carreiras em TI  
**Base de conhecimento:** `regras_carreiras.json` — versão `0.3.0`  
**Motor de inferência:** `motor_ponderado.py`  
**Interface:** `app.py` (Streamlit)  
**Testes:** `teste.py`

> **Escopo e interpretação:** este documento descreve o comportamento implementado no motor ponderado e as regras cadastradas na base de conhecimento JSON do projeto. Os percentuais são **índices orientativos de compatibilidade** com as respostas informadas, não probabilidades de contratação nem medidas científicas de aptidão. Os níveis “Júnior” são referências pedagógicas, não requisitos universais de empresas.

## 1. Objetivo e organização do sistema

O consultor avalia **dez carreiras de TI** a partir de (a) afinidades autodeclaradas, (b) objetivos profissionais e (c) atividades que a pessoa prefere evitar. Calcula um **Top 3**, exibe justificativas e, após a escolha de uma das carreiras recomendadas, compara cinco competências técnicas com níveis de referência Júnior para produzir um roadmap de aprendizagem personalizado.

| Componente | Responsabilidade |
|---|---|
| `regras_carreiras.json` | Define as dimensões, objetivos, pesos por carreira, restrições, regras de penalidade, verificações de contradição, competências, pré-requisitos, projetos e sugestões de estudo. |
| `motor_ponderado.py` | Lê e valida a base JSON; calcula afinidades, objetivos, penalidades, Top 3, lacunas e roadmaps. |
| `app.py` | Coleta respostas e mostra resultados e orientações na interface Streamlit. |
| `teste.py` | Executa testes automatizados do motor e da base. |

A base de conhecimento é **externa** ao motor: alterações de pesos e descrições são feitas no JSON, sem modificar as fórmulas Python. Isso não elimina a necessidade de validar novamente o sistema após mudanças nos parâmetros.

## 2. Entradas e escalas

| Informação | Escala ou formato | Significado |
|---|---|---|
| Afinidades (`D01` a `D13`) | Inteiros de **1 a 5** ou `null` | 1 = nenhum interesse; 2 = pouco; 3 = moderado; 4 = bastante; 5 = muito. `null` = a pessoa não consegue avaliar. |
| Objetivos (`O01` a `O08`) | Inteiros de **1 a 5** ou `null` | Intensidade do alinhamento com cada objetivo profissional. |
| Restrições (`RSTR01` a `RSTR08`) | Conjunto de códigos escolhidos | Atividades que a pessoa declara preferir evitar; pode ser vazio. |
| Conhecimento técnico | Inteiros de **0 a 3** ou `null` | 0 = nenhum conhecimento; 1 = básico; 2 = intermediário; 3 = prático. `null` = não informado. |
| Pesos por carreira | Inteiros de **0 a 5** | Relevância da dimensão/objetivo para a carreira; peso zero não participa do cálculo. |

### 2.1. Dimensões de afinidade

| Código | Dimensão |
|---|---|
| `D01` | Lógica e programação |
| `D02` | Desenvolvimento Back-end |
| `D03` | Interfaces e UI/UX |
| `D04` | Matemática e estatística |
| `D05` | Ciência de Dados e IA |
| `D06` | Engenharia de Dados |
| `D07` | Cibersegurança |
| `D08` | Infraestrutura e redes |
| `D09` | Automação e DevOps |
| `D10` | Computação em nuvem |
| `D11` | Desenvolvimento Mobile |
| `D12` | Qualidade e testes (QA) |
| `D13` | Gestão de produtos |

### 2.2. Objetivos profissionais

| Código | Objetivo |
|---|---|
| `O01` | Desenvolver sistemas e soluções de software |
| `O02` | Criar experiências digitais intuitivas e acessíveis |
| `O03` | Transformar dados em informações e decisões |
| `O04` | Manter infraestruturas e serviços tecnológicos eficientes e escaláveis |
| `O05` | Proteger sistemas, dados e informações |
| `O06` | Garantir a qualidade e a confiabilidade de aplicações |
| `O07` | Planejar produtos e contribuir para decisões estratégicas |
| `O08` | Desenvolver soluções para dispositivos móveis |

## 3. Matriz de pesos das dez carreiras

Em cada célula, o número entre parênteses é o **peso** do fator (0–5). Os fatores não listados têm peso **zero** para a carreira em questão.

| Carreira (código interno) | Pesos de afinidade | Pesos de objetivos |
|---|---|---|
| **Desenvolvimento Back-end** (`backend`) | `D01` (5); `D02` (5); `D06` (3); `D12` (2); `D09` (2) | `O01` (5); `O04` (2) |
| **Desenvolvimento Front-end e UI/UX** (`frontend`) | `D03` (5); `D01` (4); `D12` (2); `D02` (1) | `O02` (5); `O01` (3) |
| **Ciência de Dados e Machine Learning** (`ciencia_dados`) | `D05` (5); `D04` (5); `D06` (3); `D01` (2) | `O03` (5) |
| **Engenharia de Dados** (`engenharia_dados`) | `D06` (5); `D01` (4); `D09` (3); `D04` (2); `D05` (2) | `O03` (4); `O04` (3) |
| **Cibersegurança** (`ciberseguranca`) | `D07` (5); `D08` (4); `D01` (2); `D12` (2) | `O05` (5); `O04` (2) |
| **DevOps e SRE** (`devops`) | `D09` (5); `D08` (5); `D10` (3); `D01` (2); `D12` (2) | `O04` (5); `O06` (3) |
| **Computação em Nuvem** (`nuvem`) | `D10` (5); `D08` (4); `D09` (4); `D07` (2) | `O04` (5); `O05` (2) |
| **Desenvolvimento Mobile** (`mobile`) | `D11` (5); `D01` (4); `D03` (3); `D02` (2); `D12` (2) | `O08` (5); `O01` (3); `O02` (2) |
| **Engenharia de Qualidade e Testes (QA)** (`qa`) | `D12` (5); `D01` (3); `D07` (2); `D09` (2); `D03` (1) | `O06` (5); `O05` (2) |
| **Gestão de Produtos Digitais** (`gestao_produtos`) | `D13` (5); `D03` (3); `D12` (2); `D05` (2) | `O07` (5); `O02` (2); `O03` (2) |

Os pesos são critérios **definidos para este protótipo** e documentados no JSON. Não representam estatísticas de contratação ou probabilidades reais.

## 4. Cálculo da afinidade e dos objetivos

Para cada carreira, aplica-se a transformação da nota informada `aᵢ` ou `oᵢ` (de 1 a 5) para uma escala de 0 a 1:

```text
nota_normalizada = (nota - 1) / 4
```

A afinidade `A` e o alinhamento com objetivos `O` são **médias ponderadas normalizadas**, calculadas separadamente:

```text
A (%) = 100 × Σ[peso_afinidade × (nota_afinidade - 1) / 4]
              / Σ[pesos_de_afinidades_respondidas]

O (%) = 100 × Σ[peso_objetivo × (nota_objetivo - 1) / 4]
              / Σ[pesos_de_objetivos_respondidos]
```

**Atenção:** as somas acima consideram apenas fatores com **peso positivo** e **nota conhecida**. Cada componente é arredondado a duas casas decimais pelo motor. Nota 1 é válida e produz contribuição zero; não deve ser confundida com resposta desconhecida.

### 4.1. Respostas desconhecidas e cobertura mínima

Quando a pessoa seleciona “não conheço a área” (`null`) ou não informa uma nota, o fator fica **fora da média**, mas seu peso **continua no total usado para medir a cobertura**. Para cada carreira e para cada grupo de perguntas:

```text
cobertura = Σ[pesos dos fatores respondidos] / Σ[todos os pesos positivos da carreira]
```

O sistema exige **cobertura ≥ 70% nas afinidades E cobertura ≥ 70% nos objetivos**, separadamente, para atribuir compatibilidade definitiva à carreira. Se qualquer componente ficar abaixo de 70%, seu status é `dados_insuficientes` e o percentual final não é calculado.

### 4.2. Compatibilidade inicial e final

```text
compatibilidade_inicial = arredondar(0,80 × A + 0,20 × O, 2)
penalidade_aplicada    = min(soma_das_penalidades_ativadas, 16 p.p.)
compatibilidade_final = arredondar(
    limitar(compatibilidade_inicial - penalidade_aplicada, 0, 100), 2
```

O **80%/20%** é uma decisão de modelagem do projeto. As penalidades são subtraídas em **pontos percentuais**, não como porcentagem multiplicativa.

## 5. Matriz de restrições e penalidades lógicas

As penalidades são aplicadas apenas quando a pessoa seleciona **explicitamente** a atividade que prefere evitar. Atividade **principal** para a carreira: **−8 p.p.**; **complementar**: **−4 p.p.**; penalidade acumulada limitada a **16 p.p.** por carreira. Não há exclusão automática de carreiras nem penalidade adicional por afinidade ou conhecimento baixos.

| Código e restrição | Penalidade principal (−8 p.p.) | Penalidade complementar (−4 p.p.) |
|---|---|---|
| **`RSTR01` — Prefiro evitar programação frequente.** | Desenvolvimento Back-end; Desenvolvimento Front-end e UI/UX; Engenharia de Dados; Desenvolvimento Mobile | Ciência de Dados e Machine Learning; DevOps e SRE; Engenharia de Qualidade e Testes (QA) |
| **`RSTR02` — Prefiro evitar cálculos e análises estatísticas.** | Ciência de Dados e Machine Learning | Engenharia de Dados |
| **`RSTR03` — Prefiro evitar criar interfaces e elementos visuais.** | Desenvolvimento Front-end e UI/UX | Desenvolvimento Mobile |
| **`RSTR04` — Prefiro evitar administrar servidores e redes.** | DevOps e SRE; Computação em Nuvem | Cibersegurança |
| **`RSTR05` — Prefiro evitar investigar vulnerabilidades de segurança.** | Cibersegurança | — |
| **`RSTR06` — Prefiro evitar realizar testes de software.** | Engenharia de Qualidade e Testes (QA) | Desenvolvimento Back-end; Desenvolvimento Front-end e UI/UX; Desenvolvimento Mobile; DevOps e SRE |
| **`RSTR07` — Prefiro evitar automatizar implantações e processos de infraestrutura.** | DevOps e SRE | Computação em Nuvem |
| **`RSTR08` — Prefiro evitar planejar prioridades e requisitos de produtos.** | Gestão de Produtos Digitais | — |

A base contém **23 regras** de penalidade individuais (`carreira` × `restrição`). Seleções repetidas da mesma restrição são normalizadas antes do cálculo, para não contabilizar uma mesma regra duas vezes.

## 6. Detecção e confirmação de possíveis contradições

Uma contradição **aparente** é identificada quando a pessoa atribui nota de afinidade **4 ou 5** a determinada dimensão, mas declara que prefere evitar uma atividade relacionada. O sistema solicita **revisar ou confirmar** a combinação; não altera as respostas automaticamente.

| Restrição selecionada | Dimensão comparada | Dispara alerta com nota |
|---|---|---|
| `RSTR01` | `D01` — Lógica e programação | 4 ou 5 |
| `RSTR02` | `D04` — Matemática e estatística | 4 ou 5 |
| `RSTR03` | `D03` — Interfaces e UI/UX | 4 ou 5 |
| `RSTR04` | `D08` — Infraestrutura e redes | 4 ou 5 |
| `RSTR05` | `D07` — Cibersegurança | 4 ou 5 |
| `RSTR06` | `D12` — Qualidade e testes (QA) | 4 ou 5 |
| `RSTR07` | `D09` — Automação e DevOps | 4 ou 5 |
| `RSTR08` | `D13` — Gestão de produtos | 4 ou 5 |

Se houver alerta **não confirmado**, o motor devolve `revisao_pendente` e não libera o Top 3. Após confirmação, preserva as preferências e aplica as penalidades cadastradas. Resposta de afinidade `null` não dispara alerta.

## 7. Classificação e Top 3

O motor `gerar_ranking_top3` calcula os resultados das dez carreiras, mas só considera **elegíveis** aquelas com cobertura suficiente nos dois componentes. Em caso de contradição não confirmada, retorna `revisao_pendente`. Se houver menos de três carreiras elegíveis, retorna `dados_insuficientes` e solicita respostas adicionais.

Com pelo menos três carreiras elegíveis e sem revisão pendente, a ordenação implementada é:

1. Maior **compatibilidade final**;
2. Empate: maior **afinidade percentual**;
3. Persistindo empate: maior **alinhamento com objetivos**;
4. Persistindo empate: **ordem alfabética do nome da carreira**, seguida do código interno como critério técnico.

O sistema apresenta as três primeiras carreiras e disponibiliza também a classificação completa das elegíveis. O campo `empates_no_corte` identifica carreiras posicionadas **após a terceira** com o mesmo percentual final da terceira colocada — mesmo quando critérios secundários determinaram sua posição. Isso sinaliza um empate na nota final, mas o Top 3 continua contendo três carreiras.

As justificativas recuperam a afinidade, os objetivos, as coberturas e as regras de penalidade ativadas; não atribuem à pessoa características que ela não informou.

## 8. Competências e referências Júnior

Após calcular o Top 3, a pessoa escolhe uma das carreiras apresentadas e informa seu nível atual para **cinco competências específicas**. A referência Júnior é cadastrada para cada competência no JSON. A tabela apresenta as **50 competências e seus níveis**, de acordo com a versão 0.3.0.

| Carreira | Competência 1 | Competência 2 | Competência 3 | Competência 4 | Competência 5 |
|---|---|---|---|---|---|
| **Desenvolvimento Back-end** | Lógica e programação (**2**) | APIs REST (**2**) | Bancos de dados SQL (**2**) | Orientação a objetos (**2**) | Testes de software (**1**) |
| **Desenvolvimento Front-end e UI/UX** | HTML, CSS e JavaScript (**2**) | Interfaces responsivas (**2**) | Frameworks front-end (**1**) | Acessibilidade (**1**) | Princípios de UI/UX (**1**) |
| **Ciência de Dados e Machine Learning** | Python para dados (**2**) | Matemática e estatística (**2**) | SQL (**2**) | Análise e visualização de dados (**2**) | Fundamentos de Machine Learning (**1**) |
| **Engenharia de Dados** | SQL avançado (**2**) | Modelagem de dados (**2**) | Python (**2**) | Pipelines ETL/ELT (**1**) | Processamento e integração de dados (**1**) |
| **Cibersegurança** | Redes de computadores (**2**) | Sistemas Linux (**1**) | Fundamentos de segurança (**2**) | Análise de vulnerabilidades (**1**) | Monitoramento e resposta a incidentes (**1**) |
| **DevOps e SRE** | Linux e administração de sistemas (**2**) | Git e CI/CD (**2**) | Contêineres (**1**) | Automação de infraestrutura (**1**) | Monitoramento e observabilidade (**1**) |
| **Computação em Nuvem** | Fundamentos de cloud (**2**) | Redes e infraestrutura (**2**) | Serviços de nuvem (**2**) | Gerenciamento de identidades e acessos (**1**) | Implantação e automação (**1**) |
| **Desenvolvimento Mobile** | Programação mobile (**2**) | Interfaces para dispositivos móveis (**2**) | Consumo de APIs (**2**) | Persistência de dados (**1**) | Testes de aplicativos (**1**) |
| **Engenharia de Qualidade e Testes (QA)** | Fundamentos de testes (**2**) | Elaboração de casos de teste (**2**) | Identificação e registro de bugs (**2**) | Testes de API (**1**) | Automação de testes (**1**) |
| **Gestão de Produtos Digitais** | Levantamento de necessidades (**2**) | Definição e priorização de requisitos (**2**) | Metodologias ágeis (**2**) | Métricas de produto (**1**) | Comunicação com equipes (**2**) |

### 8.1. Cálculo de lacunas (Skill Gaps)

```text
lacuna_da_competencia = max(0, nivel_de_referencia_junior - nivel_atual)
```

Para cada competência, o motor informa nível atual, referência Júnior, lacuna e orientação. A **quantidade de competências com lacuna** é o número de competências com resultado maior que zero; o **total de níveis faltantes** é a soma dessas diferenças.

- **Lacuna = 0:** referência atingida; não exigir novamente estudo básico obrigatório.
- **Lacuna = 1:** propor aprofundamento e prática direcionada.
- **Lacuna ≥ 2:** começar por fundamentos e pré-requisitos antes da prática.
- **Conhecimento `null` ou não informado:** marcar `avaliacao_incompleta`; não equivale ao nível zero e não permite roadmap definitivo.

A avaliação de competências **não altera o Top 3**: separa-se o interesse profissional da preparação técnica atual.

## 9. Regras de geração do roadmap personalizado

A função `gerar_roadmap_personalizado` produz quatro etapas, escolhidas com base **apenas nas competências com lacuna positiva**, nos pré-requisitos e nos conteúdos disponíveis no JSON:

| Etapa | Critério implementado |
|---|---|
| **1. Fundamentos** | Para cada lacuna, apresentar tópicos cadastrados em `fundamentos`; começar pela base especialmente quando nível atual é zero ou a lacuna é de dois ou mais níveis. |
| **2. Desenvolvimento técnico** | Para as mesmas lacunas, recomendar `praticas` e `tecnologias_sugeridas` presentes no JSON. |
| **3. Projeto para portfólio** | Apresentar o `projeto_portfolio` da carreira, com descrição, entregáveis, GitHub e as competências com lacunas que ele exercita. |
| **4. Consolidação e próximos passos** | Recomendar documentação do projeto, revisão dos resultados e **certificações opcionais**, quando cadastradas. |

### 9.1. Ordenação dos estudos

O motor confere referências, duplicidades e ciclos entre pré-requisitos. Primeiro respeita a dependência entre competências que **também têm lacuna**; dentre as que podem ser iniciadas, prioriza maior lacuna e, em caso de empate, a ordem original da base JSON. Pré-requisitos cuja referência já foi atingida não são incluídos como estudo obrigatório.

### 9.2. Cenários especiais

| Condição | Status do roadmap | Comportamento |
|---|---|---|
| Conhecimento de alguma competência não informado | `avaliacao_incompleta` | Indica as competências pendentes; não gera etapas definitivas. |
| Existe pelo menos uma lacuna | `roadmap_gerado` | Exibe estudos e práticas para as lacunas, projeto de portfólio e consolidação. |
| Todas as referências atingidas | `sem_lacunas` | Não gera estudos fundamentais/técnicos obrigatórios; mantém projeto de consolidação e próximos passos. |

### 9.3. Projetos integradores cadastrados

| Carreira | Projeto sugerido |
|---|---|
| Desenvolvimento Back-end | API REST de gerenciamento de tarefas |
| Desenvolvimento Front-end e UI/UX | Interface responsiva de consulta a serviços |
| Ciência de Dados e Machine Learning | Análise exploratória com previsão simples |
| Engenharia de Dados | Pipeline ETL de dados abertos |
| Cibersegurança | Laboratório defensivo de segurança |
| DevOps e SRE | Aplicação conteinerizada com CI/CD e logs |
| Computação em Nuvem | Implantação controlada de aplicação em nuvem |
| Desenvolvimento Mobile | Aplicativo de gerenciamento de tarefas |
| Engenharia de Qualidade e Testes (QA) | Portfólio de testes manuais, API e automação |
| Gestão de Produtos Digitais | Caso de produto digital com backlog e métricas |

As certificações cadastradas são **sugestões opcionais**, não condições para ingresso na carreira. A validade, custos, idioma e disponibilidade devem ser confirmados nas páginas oficiais antes de inscrição.

## 10. Exemplo numérico auditável — Back-end

Considere as seguintes respostas fictícias, usadas também nos exemplos do motor:

| Afinidade (peso) | Nota | Contribuição normalizada |
|---|---:|---:|
| `D01` (5) | 5 | 5.00 |
| `D02` (5) | 5 | 5.00 |
| `D06` (3) | 4 | 2.25 |
| `D12` (2) | 3 | 1.00 |
| `D09` (2) | 2 | 0.50 |

**Afinidade:** `(13.75 / 17) × 100 = 80,88%`.

Para os objetivos, `O01 = 5` (peso 5) e `O04 = 3` (peso 2):

```text
Objetivos = [(5 × 1,00) + (2 × 0,50)] / 7 × 100 = 85,71%
Compatibilidade inicial = 0,80 × 80,88 + 0,20 × 85,71 = 81,85%
```

Com a restrição `RSTR01` (evitar programação frequente), a regra principal de Back-end desconta **8 pontos percentuais**. Como `D01 = 5`, há alerta de contradição aparente, que precisa ser confirmado antes do resultado:

```text
Antes da confirmação: status = revisao_pendente; final = None
Após confirmação: 81,85% - 8 p.p. = 73,85%
```

**Exemplo de cobertura insuficiente:** se somente `D01` e `D02` forem respondidas em Back-end, o peso conhecido será 10 de 17; cobertura = **58,82%**, abaixo do mínimo, logo a afinidade não recebe percentual definitivo.

## 11. Validação, rastreabilidade e limitações

A suíte `teste.py` foi executada com **50 testes aprovados** no desenvolvimento, cobrindo carga/validação da base, entradas inválidas, cálculo ponderado, limites de cobertura, penalidades, contradições, Top 3, empates, competências, pré-requisitos e cenários especiais de roadmap. Os testes automatizados são principalmente **do motor**; a interface Streamlit foi verificada também por testes manuais de navegação e apresentação.

Para repetir a validação local:

```powershell
.\.venv\Scripts\python.exe teste.py
```

**Limitações e cuidados:**

- Os resultados dependem das respostas autodeclaradas e dos pesos do protótipo; podem variar se o usuário mudar suas preferências.
- Percentuais são índices internos orientativos: não representam uma probabilidade de êxito, aptidão clínica ou garantia de empregabilidade.
- A avaliação Júnior e a recomendação de certificações são orientativas; requisitos de vagas e disponibilidade de cursos podem mudar.
- A base contém algumas descrições de **`modelagem_pendente`** herdadas de uma versão intermediária; esse campo registra planejamento anterior e **não determina a execução** das funções aqui documentadas. Uma limpeza futura desse registro deverá ser feita sem mudar as regras funcionais.
- Alterações futuras na base JSON exigem nova execução dos testes e revisão desta matriz.

## 12. Correspondência entre critérios e funções do motor

| Critério | Função de referência |
|---|---|
| Carregamento e validação do JSON | `carregar_base_conhecimento`, `validar_base_conhecimento` |
| Afinidades e cobertura | `calcular_afinidade_ponderada` |
| Objetivos e cobertura | `calcular_objetivos_ponderados` |
| Compatibilidade inicial 80% / 20% | `calcular_compatibilidade_inicial` |
| Penalidades e limite de 16 p.p. | `calcular_penalidades` |
| Contradições e confirmação | `detectar_contradicoes`, `calcular_compatibilidade_final` |
| Ordenação, empates e Top 3 | `gerar_ranking_top3` |
| Comparação dos níveis Júnior | `avaliar_lacunas_competencias` |
| Pré-requisitos e roadmap | `_ordenar_lacunas_por_pre_requisitos`, `gerar_roadmap_personalizado` |

---

**Fonte técnica deste documento:** base de conhecimento `regras_carreiras.json` (versão 0.3.0) e implementação de inferência do `motor_ponderado.py`. Esta matriz documenta exclusivamente os critérios e cálculos do Consultor Avançado de Carreiras em TI.
