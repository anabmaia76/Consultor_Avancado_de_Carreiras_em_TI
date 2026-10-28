import json
from pathlib import Path


ARQUIVO_BASE = Path(__file__).resolve().parent / "regras_carreiras.json"


def carregar_base_conhecimento(caminho=ARQUIVO_BASE):
    caminho = Path(caminho)

    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            base = json.load(arquivo)
    except FileNotFoundError as erro:
        raise FileNotFoundError(f"Base de conhecimento não encontrada: {caminho}") from erro
    except json.JSONDecodeError as erro:
        raise ValueError(
            f"JSON inválido na linha {erro.lineno}, coluna {erro.colno}: {erro.msg}"
        ) from erro

    validar_base_conhecimento(base)
    return base


def validar_base_conhecimento(base):
    secoes = {
        "dimensoes_afinidade": dict,
        "objetivos_profissionais": dict,
        "restricoes_atividades": dict,
        "carreiras": dict,
        "parametros_calculo": dict,
        "penalidades_logicas": list,
        "verificacao_contradicoes": dict,
        "parametros_skill_gaps": dict,
        "parametros_roadmap": dict,
    }

    if not isinstance(base, dict):
        raise ValueError("A raiz da base de conhecimento deve ser um objeto JSON.")

    for secao, tipo in secoes.items():
        if not isinstance(base.get(secao), tipo):
            raise ValueError(f"Seção ausente ou com formato incorreto: {secao}")

    for codigo, carreira in base["carreiras"].items():
        if not isinstance(carreira.get("competencias"), list):
            raise ValueError(f"A carreira {codigo} não possui uma lista de competências.")
        for campo, referencia in (
            ("pesos_afinidade", "dimensoes_afinidade"),
            ("pesos_objetivos", "objetivos_profissionais"),
        ):
            pesos = carreira.get(campo)
            if not isinstance(pesos, dict) or not pesos:
                raise ValueError(f"Pesos ausentes em {codigo}: {campo}")
            for identificador, peso in pesos.items():
                if identificador not in base[referencia]:
                    raise ValueError(f"Referência desconhecida em {codigo}: {identificador}")
                if type(peso) is not int or not 0 <= peso <= 5:
                    raise ValueError(f"Peso inválido em {codigo}: {identificador}")
            if sum(pesos.values()) <= 0:
                raise ValueError(f"A carreira {codigo} não possui pesos positivos em {campo}.")

    for regra in base["penalidades_logicas"]:
        if regra["carreira"] not in base["carreiras"]:
            raise ValueError(f"Carreira não encontrada na penalidade: {regra['carreira']}")
        if regra["restricao"] not in base["restricoes_atividades"]:
            raise ValueError(f"Restrição não encontrada: {regra['restricao']}")

    parametros = base["parametros_calculo"]
    for campo in ("cobertura_minima_afinidades", "cobertura_minima_objetivos"):
        cobertura = parametros.get(campo)
        if type(cobertura) not in (int, float) or not 0 <= cobertura <= 1:
            raise ValueError(f"O parâmetro {campo} deve estar entre 0 e 1.")

    proporcoes = (
        parametros.get("participacao_afinidades"),
        parametros.get("participacao_objetivos"),
    )
    if any(type(valor) not in (int, float) or not 0 <= valor <= 1 for valor in proporcoes):
        raise ValueError("Participações de afinidades e objetivos devem estar entre 0 e 1.")
    if abs(sum(proporcoes) - 1.0) > 1e-9:
        raise ValueError("As participações de afinidades e objetivos devem somar 1.")

    for chave in (
        "penalidade_atividade_principal_pontos_percentuais",
        "penalidade_atividade_complementar_pontos_percentuais",
        "limite_penalidades_pontos_percentuais",
    ):
        valor = parametros.get(chave)
        if type(valor) not in (int, float) or not 0 <= valor <= 100:
            raise ValueError(f"Parâmetro de penalidade inválido: {chave}")

    regras_vistas = set()
    for regra in base["penalidades_logicas"]:
        tipo = regra.get("tipo")
        if tipo not in ("principal", "complementar"):
            raise ValueError(f"Tipo de penalidade inválido: {tipo}")
        chave = (regra["carreira"], regra["restricao"])
        if chave in regras_vistas:
            raise ValueError(f"Penalidade duplicada para {chave}")
        regras_vistas.add(chave)
        valor_esperado = parametros[
            "penalidade_atividade_principal_pontos_percentuais"
            if tipo == "principal"
            else "penalidade_atividade_complementar_pontos_percentuais"
        ]
        if type(regra.get("pontos_percentuais")) not in (int, float) or regra["pontos_percentuais"] != valor_esperado:
            raise ValueError(f"Valor de penalidade incoerente em {chave}")

    verificacao = base["verificacao_contradicoes"]
    nota_alerta = verificacao.get("nota_afinidade_minima_para_alerta")
    if type(nota_alerta) is not int or not 1 <= nota_alerta <= 5:
        raise ValueError("Nota mínima para alerta de contradição inválida.")
    mapa = verificacao.get("comparacoes_restricao_afinidade")
    if not isinstance(mapa, dict):
        raise ValueError("O mapeamento das contradições deve ser um objeto JSON.")
    for restricao, dimensao in mapa.items():
        if restricao not in base["restricoes_atividades"]:
            raise ValueError(f"Restrição desconhecida no mapa de contradições: {restricao}")
        if dimensao not in base["dimensoes_afinidade"]:
            raise ValueError(f"Dimensão desconhecida no mapa de contradições: {dimensao}")


def calcular_afinidade_ponderada(base, codigo_carreira, respostas_afinidade):

    if codigo_carreira not in base["carreiras"]:
        raise ValueError(f"Carreira não cadastrada: {codigo_carreira}")
    if not isinstance(respostas_afinidade, dict):
        raise TypeError("As respostas devem ser fornecidas em um dicionário.")

    dimensoes = base["dimensoes_afinidade"]
    for codigo, nota in respostas_afinidade.items():
        if codigo not in dimensoes:
            raise ValueError(f"Dimensão de afinidade desconhecida: {codigo}")
        if nota is not None and (type(nota) is not int or not 1 <= nota <= 5):
            raise ValueError(f"Nota inválida para {codigo}: use inteiro de 1 a 5 ou None.")

    carreira = base["carreiras"][codigo_carreira]
    pesos = carreira["pesos_afinidade"]
    peso_total = sum(pesos.values())
    peso_respondido = 0
    soma_ponderada_normalizada = 0.0
    detalhes = []

    for codigo, peso in pesos.items():
        if peso == 0:
            continue
        nota = respostas_afinidade.get(codigo)
        if nota is None:
            detalhes.append({"dimensao": codigo, "peso": peso, "nota": None})
            continue
        peso_respondido += peso
        soma_ponderada_normalizada += peso * ((nota - 1) / 4)
        detalhes.append({"dimensao": codigo, "peso": peso, "nota": nota})

    cobertura = peso_respondido / peso_total
    cobertura_minima = base["parametros_calculo"]["cobertura_minima_afinidades"]
    suficiente = peso_respondido > 0 and cobertura >= cobertura_minima
    percentual = (
        round(100 * soma_ponderada_normalizada / peso_respondido, 2)
        if suficiente else None
    )

    return {
        "codigo_carreira": codigo_carreira,
        "carreira": carreira["nome"],
        "status": "calculada" if suficiente else "dados_insuficientes",
        "afinidade_percentual": percentual,
        "cobertura_percentual": round(100 * cobertura, 2),
        "peso_respondido": peso_respondido,
        "peso_total": peso_total,
        "dimensoes": detalhes,
    }


def calcular_afinidades_todas(base, respostas_afinidade):
    return {
        codigo: calcular_afinidade_ponderada(base, codigo, respostas_afinidade)
        for codigo in base["carreiras"]
    }

def calcular_objetivos_ponderados(base, codigo_carreira, respostas_objetivos):
    if codigo_carreira not in base["carreiras"]:
        raise ValueError(f"Carreira não cadastrada: {codigo_carreira}")
    if not isinstance(respostas_objetivos, dict):
        raise TypeError("Os objetivos devem ser fornecidos em um dicionário.")

    objetivos = base["objetivos_profissionais"]
    for codigo, nota in respostas_objetivos.items():
        if codigo not in objetivos:
            raise ValueError(f"Objetivo profissional desconhecido: {codigo}")
        if nota is not None and (type(nota) is not int or not 1 <= nota <= 5):
            raise ValueError(f"Nota inválida para {codigo}: use inteiro de 1 a 5 ou None.")

    carreira = base["carreiras"][codigo_carreira]
    pesos = carreira["pesos_objetivos"]
    peso_total = sum(pesos.values())
    peso_respondido = 0
    soma_ponderada_normalizada = 0.0
    detalhes = []

    for codigo, peso in pesos.items():
        if peso == 0:
            continue
        nota = respostas_objetivos.get(codigo)
        detalhes.append({"objetivo": codigo, "peso": peso, "nota": nota})
        if nota is None:
            continue
        peso_respondido += peso
        soma_ponderada_normalizada += peso * ((nota - 1) / 4)

    cobertura = peso_respondido / peso_total
    cobertura_minima = base["parametros_calculo"]["cobertura_minima_objetivos"]
    suficiente = peso_respondido > 0 and cobertura >= cobertura_minima
    percentual = (
        round(100 * soma_ponderada_normalizada / peso_respondido, 2)
        if suficiente else None
    )

    return {
        "codigo_carreira": codigo_carreira,
        "carreira": carreira["nome"],
        "status": "calculada" if suficiente else "dados_insuficientes",
        "objetivos_percentual": percentual,
        "cobertura_percentual": round(100 * cobertura, 2),
        "peso_respondido": peso_respondido,
        "peso_total": peso_total,
        "objetivos": detalhes,
    }


def calcular_compatibilidade_inicial(base, codigo_carreira, respostas_afinidade, respostas_objetivos):
    afinidade = calcular_afinidade_ponderada(base, codigo_carreira, respostas_afinidade)
    objetivos = calcular_objetivos_ponderados(base, codigo_carreira, respostas_objetivos)

    suficiente = afinidade["status"] == "calculada" and objetivos["status"] == "calculada"
    percentual = None
    if suficiente:
        parametros = base["parametros_calculo"]
        percentual = round(
            parametros["participacao_afinidades"] * afinidade["afinidade_percentual"]
            + parametros["participacao_objetivos"] * objetivos["objetivos_percentual"],
            2,
        )

    return {
        "codigo_carreira": codigo_carreira,
        "carreira": base["carreiras"][codigo_carreira]["nome"],
        "status": "calculada" if suficiente else "dados_insuficientes",
        "compatibilidade_inicial_percentual": percentual,
        "afinidade": afinidade,
        "objetivos": objetivos,
        "penalidades_aplicadas": False,
    }

def calcular_compatibilidades_iniciais_todas(base, respostas_afinidade, respostas_objetivos):
    return {
        codigo: calcular_compatibilidade_inicial(base, codigo, respostas_afinidade, respostas_objetivos)
        for codigo in base["carreiras"]
    }

def _normalizar_restricoes(base, restricoes):
    if restricoes is None:
        restricoes = []
    if not isinstance(restricoes, (list, tuple, set, frozenset)):
        raise TypeError("Informe restrições como lista, tupla ou conjunto de códigos.")
    itens = sorted(restricoes) if isinstance(restricoes, (set, frozenset)) else restricoes
    unicas = []
    for codigo in itens:
        if not isinstance(codigo, str) or codigo not in base["restricoes_atividades"]:
            raise ValueError(f"Restrição não cadastrada: {codigo!r}")
        if codigo not in unicas:
            unicas.append(codigo)
    return unicas


def calcular_penalidades(base, codigo_carreira, restricoes):
    if codigo_carreira not in base["carreiras"]:
        raise ValueError(f"Carreira não cadastrada: {codigo_carreira}")
    selecionadas = set(_normalizar_restricoes(base, restricoes))
    detalhes = []
    for regra in base["penalidades_logicas"]:
        if regra["carreira"] != codigo_carreira or regra["restricao"] not in selecionadas:
            continue
        restricao = regra["restricao"]
        detalhes.append({
            "restricao": restricao,
            "descricao": base["restricoes_atividades"][restricao]["descricao"],
            "tipo": regra["tipo"],
            "pontos_percentuais": regra["pontos_percentuais"],
        })
    total_bruto = sum(item["pontos_percentuais"] for item in detalhes)
    limite = base["parametros_calculo"]["limite_penalidades_pontos_percentuais"]
    total_aplicado = min(total_bruto, limite)
    return {
        "codigo_carreira": codigo_carreira,
        "regras_ativadas": detalhes,
        "total_bruto_pontos_percentuais": total_bruto,
        "limite_pontos_percentuais": limite,
        "total_aplicado_pontos_percentuais": total_aplicado,
        "reducao_pelo_limite": total_bruto - total_aplicado,
    }


def detectar_contradicoes(base, respostas_afinidade, restricoes):
    if not isinstance(respostas_afinidade, dict):
        raise TypeError("As afinidades devem ser fornecidas em um dicionário.")
    for codigo, nota in respostas_afinidade.items():
        if codigo not in base["dimensoes_afinidade"]:
            raise ValueError(f"Dimensão de afinidade desconhecida: {codigo}")
        if nota is not None and (type(nota) is not int or not 1 <= nota <= 5):
            raise ValueError(f"Nota inválida para {codigo}: {nota}")
    selecionadas = _normalizar_restricoes(base, restricoes)
    configuracao = base["verificacao_contradicoes"]
    minimo = configuracao["nota_afinidade_minima_para_alerta"]
    mapa = configuracao["comparacoes_restricao_afinidade"]
    avisos = []
    for restricao in selecionadas:
        dimensao = mapa.get(restricao)
        nota = respostas_afinidade.get(dimensao) if dimensao else None
        if nota is not None and nota >= minimo:
            avisos.append({
                "restricao": restricao,
                "descricao_restricao": base["restricoes_atividades"][restricao]["descricao"],
                "dimensao": dimensao,
                "nota_afinidade": nota,
                "mensagem": (
                    "Você indicou alta afinidade com esta dimensão, mas prefere "
                    "evitar uma atividade relacionada. Revise ou confirme ambas as respostas."
                ),
            })
    return avisos

def calcular_compatibilidade_final(
    base, codigo_carreira, respostas_afinidade, respostas_objetivos,
    restricoes=None, contradicoes_confirmadas=False,
):
    if type(contradicoes_confirmadas) is not bool:
        raise TypeError("contradicoes_confirmadas deve ser True ou False.")
    inicial = calcular_compatibilidade_inicial(
        base, codigo_carreira, respostas_afinidade, respostas_objetivos
    )
    penalidades = calcular_penalidades(base, codigo_carreira, restricoes)
    contradicoes = detectar_contradicoes(base, respostas_afinidade, restricoes)
    pendente = bool(contradicoes) and not contradicoes_confirmadas

    if inicial["status"] != "calculada":
        status = "dados_insuficientes"
        percentual_final = None
    elif pendente:
        status = "revisao_pendente"
        percentual_final = None
    else:
        status = "calculada"
        percentual_final = round(max(
            0.0,
            min(100.0, inicial["compatibilidade_inicial_percentual"]
                - penalidades["total_aplicado_pontos_percentuais"]),
        ), 2)

    return {
        **inicial,
        "status": status,
        "compatibilidade_final_percentual": percentual_final,
        "penalidades": penalidades,
        "contradicoes": contradicoes,
        "confirmacao_pendente": pendente,
        "contradicoes_confirmadas": contradicoes_confirmadas,
        "penalidades_aplicadas": percentual_final is not None and penalidades["total_aplicado_pontos_percentuais"] > 0,
    }


def calcular_compatibilidades_finais_todas(
    base, respostas_afinidade, respostas_objetivos,
    restricoes=None, contradicoes_confirmadas=False,
):
    return {
        codigo: calcular_compatibilidade_final(
            base, codigo, respostas_afinidade, respostas_objetivos,
            restricoes, contradicoes_confirmadas,
        )
        for codigo in base["carreiras"]
    }




def gerar_ranking_top3(
    base, respostas_afinidade, respostas_objetivos,
    restricoes=None, contradicoes_confirmadas=False,
):
    resultados = calcular_compatibilidades_finais_todas(
        base, respostas_afinidade, respostas_objetivos,
        restricoes=restricoes,
        contradicoes_confirmadas=contradicoes_confirmadas,
    )
    avisos = detectar_contradicoes(base, respostas_afinidade, restricoes)

    elegiveis = [
        resultado for resultado in resultados.values()
        if resultado["afinidade"]["status"] == "calculada"
        and resultado["objetivos"]["status"] == "calculada"
    ]
    insuficientes = [
        {"codigo_carreira": codigo, "carreira": resultado["carreira"],
         "cobertura_afinidade": resultado["afinidade"]["cobertura_percentual"],
         "cobertura_objetivos": resultado["objetivos"]["cobertura_percentual"]}
        for codigo, resultado in resultados.items()
        if resultado["afinidade"]["status"] != "calculada"
        or resultado["objetivos"]["status"] != "calculada"
    ]

    if avisos and not contradicoes_confirmadas:
        return {
            "status": "revisao_pendente",
            "mensagem": "Revise ou confirme as respostas aparentemente contraditórias antes de gerar o Top 3.",
            "top_3": [],
            "classificacao_completa": [],
            "carreiras_elegiveis": len(elegiveis),
            "carreiras_com_dados_insuficientes": insuficientes,
            "contradicoes": avisos,
            "empates_no_corte": [],
            "resultados_por_carreira": resultados,
        }

    if len(elegiveis) < 3:
        return {
            "status": "dados_insuficientes",
            "mensagem": (
                f"Apenas {len(elegiveis)} carreira(s) possuem cobertura suficiente. "
                "Responda a mais questões de afinidades e objetivos para obter o Top 3 completo."
            ),
            "top_3": [],
            "classificacao_completa": [],
            "carreiras_elegiveis": len(elegiveis),
            "carreiras_com_dados_insuficientes": insuficientes,
            "contradicoes": avisos,
            "empates_no_corte": [],
            "resultados_por_carreira": resultados,
        }

    ordenados = sorted(
        elegiveis,
        key=lambda r: (
            -r["compatibilidade_final_percentual"],
            -r["afinidade"]["afinidade_percentual"],
            -r["objetivos"]["objetivos_percentual"],
            r["carreira"].casefold(),
            r["codigo_carreira"],
        ),
    )
    classificacao = []
    for indice, resultado in enumerate(ordenados, start=1):
        classificacao.append({
            "posicao": indice,
            "codigo_carreira": resultado["codigo_carreira"],
            "carreira": resultado["carreira"],
            "compatibilidade_final_percentual": resultado["compatibilidade_final_percentual"],
            "compatibilidade_inicial_percentual": resultado["compatibilidade_inicial_percentual"],
            "afinidade_percentual": resultado["afinidade"]["afinidade_percentual"],
            "objetivos_percentual": resultado["objetivos"]["objetivos_percentual"],
            "cobertura_afinidade_percentual": resultado["afinidade"]["cobertura_percentual"],
            "cobertura_objetivos_percentual": resultado["objetivos"]["cobertura_percentual"],
            "penalidade_aplicada_pontos_percentuais": resultado["penalidades"]["total_aplicado_pontos_percentuais"],
            "justificativas_penalidades": resultado["penalidades"]["regras_ativadas"],
        })

    nota_corte = classificacao[2]["compatibilidade_final_percentual"]
    empates_no_corte = [
        {"codigo_carreira": item["codigo_carreira"],
         "carreira": item["carreira"],
         "compatibilidade_final_percentual": item["compatibilidade_final_percentual"]}
        for item in classificacao[3:]
        if item["compatibilidade_final_percentual"] == nota_corte
    ]

    return {
        "status": "calculada",
        "mensagem": "Top 3 calculado; índices de compatibilidade não são probabilidades de contratação.",
        "top_3": classificacao[:3],
        "classificacao_completa": classificacao,
        "carreiras_elegiveis": len(elegiveis),
        "carreiras_com_dados_insuficientes": insuficientes,
        "contradicoes": avisos,
        "empates_no_corte": empates_no_corte,
        "criterio_ordenacao": (
            "Maior compatibilidade final; empate: maior afinidade, depois objetivos "
            "e, por último, ordem alfabética técnica. Empates no corte são sinalizados."
        ),
        "resultados_por_carreira": resultados,
    }


def avaliar_lacunas_competencias(base, codigo_carreira, niveis_atuais):
    if codigo_carreira not in base["carreiras"]:
        raise ValueError(f"Carreira não cadastrada: {codigo_carreira}")
    if not isinstance(niveis_atuais, dict):
        raise TypeError("Os conhecimentos devem ser fornecidos em um dicionário.")

    carreira = base["carreiras"][codigo_carreira]
    competencias = carreira["competencias"]
    codigos_validos = {item["codigo"] for item in competencias}
    if len(codigos_validos) != len(competencias):
        raise ValueError(f"Códigos de competência repetidos em {codigo_carreira}.")

    for codigo, nivel in niveis_atuais.items():
        if codigo not in codigos_validos:
            raise ValueError(f"Competência não cadastrada para {codigo_carreira}: {codigo}")
        if nivel is not None and (type(nivel) is not int or not 0 <= nivel <= 3):
            raise ValueError(
                f"Nível inválido para {codigo}: use inteiro de 0 a 3 ou None."
            )

    detalhes = []
    pendentes = []
    total_lacunas_conhecidas = 0
    qtd_atendidas_conhecidas = 0
    qtd_com_lacuna_conhecida = 0

    for competencia in competencias:
        codigo = competencia["codigo"]
        referencia = competencia["nivel_junior"]
        if type(referencia) is not int or not 0 <= referencia <= 3:
            raise ValueError(f"Referência Júnior inválida: {codigo}")
        atual = niveis_atuais.get(codigo)
        if atual is None:
            lacuna = None
            situacao = "nao_informada"
            orientacao = "Informe o nível de conhecimento para avaliar a lacuna."
            pendentes.append(codigo)
        else:
            lacuna = max(0, referencia - atual)
            total_lacunas_conhecidas += lacuna
            if lacuna == 0:
                qtd_atendidas_conhecidas += 1
                situacao = "referencia_atendida"
                orientacao = "Referência atingida; não exigir estudo básico novamente."
            else:
                qtd_com_lacuna_conhecida += 1
                situacao = "lacuna_identificada"
                orientacao = (
                    "Começar pelos fundamentos e pré-requisitos, depois praticar."
                    if lacuna >= 2 else "Recomendar aprofundamento e prática direcionada."
                )
        detalhes.append({
            "codigo": codigo,
            "competencia": competencia["nome"],
            "nivel_atual": atual,
            "nivel_junior": referencia,
            "lacuna": lacuna,
            "situacao": situacao,
            "orientacao": orientacao,
            "pre_requisitos": list(competencia.get("pre_requisitos", [])),
        })

    completo = not pendentes
    return {
        "codigo_carreira": codigo_carreira,
        "carreira": carreira["nome"],
        "status": "avaliacao_completa" if completo else "avaliacao_incompleta",
        "total_competencias": len(competencias),
        "quantidade_respondida": len(competencias) - len(pendentes),
        "competencias_pendentes": pendentes,
        "competencias_atendidas": qtd_atendidas_conhecidas if completo else None,
        "competencias_com_lacuna": qtd_com_lacuna_conhecida if completo else None,
        "total_niveis_de_lacuna": total_lacunas_conhecidas if completo else None,
        "detalhes": detalhes,
        "altera_ranking_top3": False,
    }

def _ordenar_lacunas_por_pre_requisitos(competencias, detalhes):
    mapa = {item["codigo"]: item for item in competencias}
    if len(mapa) != len(competencias):
        raise ValueError("Códigos de competências repetidos na base de conhecimento.")
    indice = {item["codigo"]: i for i, item in enumerate(competencias)}
    detalhes_por_codigo = {item["codigo"]: item for item in detalhes}

    dependencias = {}
    for codigo, competencia in mapa.items():
        prereqs = competencia.get("pre_requisitos", [])
        if not isinstance(prereqs, list) or len(prereqs) != len(set(prereqs)):
            raise ValueError(f"Pré-requisitos inválidos ou duplicados em {codigo}.")
        for prereq in prereqs:
            if prereq not in mapa or prereq == codigo:
                raise ValueError(f"Pré-requisito inválido em {codigo}: {prereq}")
        dependencias[codigo] = prereqs

    visitados, em_processamento = set(), set()

    def conferir_ciclos(codigo):
        if codigo in em_processamento:
            raise ValueError(f"Dependências cíclicas encontradas em {codigo}.")
        if codigo in visitados:
            return
        em_processamento.add(codigo)
        for prereq in dependencias[codigo]:
            conferir_ciclos(prereq)
        em_processamento.remove(codigo)
        visitados.add(codigo)

    for codigo in mapa:
        conferir_ciclos(codigo)

    faltantes = {item["codigo"] for item in detalhes if item["lacuna"] > 0}
    ordenados = []
    concluidos = set()
    while faltantes:
        liberados = [
            codigo for codigo in faltantes
            if all(p not in faltantes or p in concluidos for p in dependencias[codigo])
        ]
        if not liberados:
            raise ValueError("Não foi possível ordenar as lacunas por pré-requisitos.")
        escolhido = min(
            liberados,
            key=lambda codigo: (-detalhes_por_codigo[codigo]["lacuna"], indice[codigo]),
        )
        ordenados.append(escolhido)
        concluidos.add(escolhido)
        faltantes.remove(escolhido)
    return ordenados


def gerar_roadmap_personalizado(base, codigo_carreira, niveis_atuais):
    avaliacao = avaliar_lacunas_competencias(base, codigo_carreira, niveis_atuais)
    carreira = base["carreiras"][codigo_carreira]
    definicao = base["parametros_roadmap"]
    etapas_configuradas = definicao.get("etapas", [])
    codigos_etapas = [etapa.get("codigo") for etapa in etapas_configuradas]
    esperadas = ["fundamentos", "desenvolvimento_tecnico", "projeto_portfolio", "consolidacao"]
    if codigos_etapas != esperadas:
        raise ValueError("Etapas do roadmap ausentes ou fora da ordem aprovada no JSON.")

    if avaliacao["status"] == "avaliacao_incompleta":
        return {
            "codigo_carreira": codigo_carreira,
            "carreira": carreira["nome"],
            "status": "avaliacao_incompleta",
            "mensagem": "Informe os conhecimentos pendentes antes de gerar um roadmap definitivo.",
            "competencias_pendentes": avaliacao["competencias_pendentes"],
            "competencias_com_lacuna": None,
            "total_niveis_de_lacuna": None,
            "ordem_priorizada": [],
            "etapas": [],
            "altera_ranking_top3": False,
        }

    competencias = carreira["competencias"]
    por_codigo = {comp["codigo"]: comp for comp in competencias}
    detalhes_por_codigo = {item["codigo"]: item for item in avaliacao["detalhes"]}
    ordem = _ordenar_lacunas_por_pre_requisitos(competencias, avaliacao["detalhes"])
    lacunas = set(ordem)

    fundamentos, praticas = [], []
    for codigo in ordem:
        competencia = por_codigo[codigo]
        detalhe = detalhes_por_codigo[codigo]
        prereqs = [
            {
                "codigo": prereq,
                "competencia": por_codigo[prereq]["nome"],
                "situacao": (
                    "incluido_antes_no_roadmap" if prereq in lacunas
                    else "nivel_de_referencia_atendido"
                ),
            }
            for prereq in competencia.get("pre_requisitos", [])
        ]
        comum = {
            "codigo": codigo,
            "competencia": competencia["nome"],
            "nivel_atual": detalhe["nivel_atual"],
            "nivel_junior": detalhe["nivel_junior"],
            "lacuna": detalhe["lacuna"],
            "pre_requisitos": prereqs,
        }
        fundamentos.append({
            **comum,
            "abordagem": (
                "Começar pelos fundamentos, antes da prática"
                if detalhe["nivel_atual"] == 0 or detalhe["lacuna"] >= 2
                else "Revisar pontos relevantes e aprofundar o conhecimento"
            ),
            "conteudos": list(competencia.get("fundamentos", [])),
        })
        praticas.append({
            **comum,
            "atividades": list(competencia.get("praticas", [])),
            "tecnologias_sugeridas": list(competencia.get("tecnologias_sugeridas", [])),
        })

    projeto = carreira.get("projeto_portfolio")
    if not isinstance(projeto, dict):
        raise ValueError(f"Projeto de portfólio inválido para {codigo_carreira}.")
    relacionados = projeto.get("competencias_relacionadas", [])
    if not isinstance(relacionados, list) or any(c not in por_codigo for c in relacionados):
        raise ValueError(f"Competências do projeto inválidas para {codigo_carreira}.")
    certs = carreira.get("certificacoes_opcionais", [])
    if not isinstance(certs, list):
        raise ValueError(f"Certificações opcionais inválidas para {codigo_carreira}.")
    foco = [
        {
            "codigo": codigo,
            "competencia": por_codigo[codigo]["nome"],
            "lacuna": detalhes_por_codigo[codigo]["lacuna"],
        }
        for codigo in ordem if codigo in relacionados
    ]
    sem_lacunas = not ordem
    itens = [
        fundamentos,
        praticas,
        [{
            "titulo": projeto["titulo"],
            "descricao": projeto["descricao"],
            "entregaveis": list(projeto.get("entregaveis", [])),
            "plataforma_sugerida": projeto.get("plataforma_sugerida", "GitHub"),
            "competencias_relacionadas_com_lacuna": foco,
            "orientacao": (
                "Projeto de consolidação: todas as competências avaliadas atendem à referência."
                if sem_lacunas else
                "Projeto integrador: exercitar as lacunas após os respectivos fundamentos."
            ),
        }],
        [{
            "acoes": (
                ["Praticar um projeto integrador para consolidar os conhecimentos."]
                if sem_lacunas else
                ["Revisar o que foi aprendido e verificar se os níveis de referência foram alcançados."]
            ) + [
                "Documentar no GitHub objetivo, instalação, execução, resultados e evidências.",
                "Evitar publicar credenciais, dados pessoais ou outros segredos.",
                "Considerar certificações somente se forem úteis ao objetivo profissional; conferir requisitos, custos e validade.",
            ],
            "certificacoes_opcionais": [dict(cert) for cert in certs],
        }],
    ]
    etapas = [
        {
            "codigo": config["codigo"],
            "nome": config["nome"],
            "objetivo": config["objetivo"],
            "itens": dados,
        }
        for config, dados in zip(etapas_configuradas, itens)
    ]
    return {
        "codigo_carreira": codigo_carreira,
        "carreira": carreira["nome"],
        "status": "sem_lacunas" if sem_lacunas else "roadmap_gerado",
        "mensagem": (
            "Níveis de referência atendidos: mantenha a prática e consolide um projeto."
            if sem_lacunas else "Roadmap elaborado a partir das lacunas identificadas."
        ),
        "competencias_pendentes": [],
        "competencias_com_lacuna": avaliacao["competencias_com_lacuna"],
        "total_niveis_de_lacuna": avaliacao["total_niveis_de_lacuna"],
        "ordem_priorizada": ordem,
        "etapas": etapas,
        "altera_ranking_top3": False,
    }


if __name__ == "__main__":
    base = carregar_base_conhecimento()
    total_competencias = sum(
        len(carreira["competencias"]) for carreira in base["carreiras"].values()
    )
    print("BASE DE CONHECIMENTO CARREGADA E VALIDADA!")
    print("Versão:", base["versao_modelo"])
    print("Dimensões de afinidade:", len(base["dimensoes_afinidade"]))
    print("Objetivos profissionais:", len(base["objetivos_profissionais"]))
    print("Carreiras:", len(base["carreiras"]))
    print("Competências:", total_competencias)
    print("Penalidades lógicas:", len(base["penalidades_logicas"]))

    exemplo = {"D01": 5, "D02": 5, "D06": 4, "D12": 3, "D09": 2}
    resultado = calcular_afinidade_ponderada(base, "backend", exemplo)
    print("\nEXEMPLO BACK-END — RESPOSTAS COMPLETAS")
    print("Afinidade:", resultado["afinidade_percentual"], "%")
    print("Cobertura:", resultado["cobertura_percentual"], "%")
    print("Situação:", resultado["status"])

    incompleto = calcular_afinidade_ponderada(
        base, "backend", {"D01": 5, "D02": 5, "D06": None}
    )
    print("\nEXEMPLO BACK-END — DADOS INSUFICIENTES")
    print("Afinidade:", incompleto["afinidade_percentual"])
    print("Cobertura:", incompleto["cobertura_percentual"], "%")
    print("Situação:", incompleto["status"])

    objetivos_exemplo = {"O01": 5, "O04": 3}
    combinada = calcular_compatibilidade_inicial(base, "backend", exemplo, objetivos_exemplo)
    print("\nEXEMPLO BACK-END — AFINIDADES + OBJETIVOS")
    print("Afinidade:", combinada["afinidade"]["afinidade_percentual"], "%")
    print("Objetivos:", combinada["objetivos"]["objetivos_percentual"], "%")
    print("Cobertura de objetivos:", combinada["objetivos"]["cobertura_percentual"], "%")
    print("Compatibilidade inicial:", combinada["compatibilidade_inicial_percentual"], "%")
    print("Situação:", combinada["status"])

    objetivos_incompletos = calcular_compatibilidade_inicial(base, "backend", exemplo, {"O04": 5})
    print("\nEXEMPLO BACK-END — OBJETIVOS INSUFICIENTES")
    print("Afinidade:", objetivos_incompletos["afinidade"]["afinidade_percentual"], "%")
    print("Cobertura de objetivos:", objetivos_incompletos["objetivos"]["cobertura_percentual"], "%")
    print("Compatibilidade inicial:", objetivos_incompletos["compatibilidade_inicial_percentual"])
    print("Situação:", objetivos_incompletos["status"])

    print("\nEXEMPLO BACK-END — SEM RESTRIÇÕES")
    sem_restricoes = calcular_compatibilidade_final(base, "backend", exemplo, objetivos_exemplo, [])
    print("Compatibilidade inicial:", sem_restricoes["compatibilidade_inicial_percentual"], "%")
    print("Penalidade aplicada:", sem_restricoes["penalidades"]["total_aplicado_pontos_percentuais"], "p.p.")
    print("Compatibilidade final:", sem_restricoes["compatibilidade_final_percentual"], "%")
    print("Situação:", sem_restricoes["status"])

    print("\nEXEMPLO BACK-END — CONTRADIÇÃO A REVISAR")
    pendente = calcular_compatibilidade_final(base, "backend", exemplo, objetivos_exemplo, ["RSTR01"])
    print("Alertas de contradição:", len(pendente["contradicoes"]))
    print("Compatibilidade final:", pendente["compatibilidade_final_percentual"])
    print("Situação:", pendente["status"])

    print("\nEXEMPLO BACK-END — CONTRADIÇÃO CONFIRMADA")
    confirmado = calcular_compatibilidade_final(
        base, "backend", exemplo, objetivos_exemplo, ["RSTR01"], contradicoes_confirmadas=True
    )
    print("Penalidade aplicada:", confirmado["penalidades"]["total_aplicado_pontos_percentuais"], "p.p.")
    print("Compatibilidade final:", confirmado["compatibilidade_final_percentual"], "%")
    print("Situação:", confirmado["status"])

    print("\nEXEMPLO DEVOPS — LIMITE DE PENALIDADES")
    respostas_max_afinidade = {codigo: 5 for codigo in base["dimensoes_afinidade"]}
    respostas_max_objetivos = {codigo: 5 for codigo in base["objetivos_profissionais"]}
    com_limite = calcular_compatibilidade_final(
        base, "devops", respostas_max_afinidade, respostas_max_objetivos,
        ["RSTR01", "RSTR04", "RSTR07"], contradicoes_confirmadas=True,
    )
    print("Soma das regras:", com_limite["penalidades"]["total_bruto_pontos_percentuais"], "p.p.")
    print("Penalidade aplicada:", com_limite["penalidades"]["total_aplicado_pontos_percentuais"], "p.p.")
    print("Compatibilidade final:", com_limite["compatibilidade_final_percentual"], "%")
    print("Situação:", com_limite["status"])


    print("\nRANKING TOP 3 — PERFIL FICTÍCIO DE DESENVOLVIMENTO")
    exemplo_afinidades_top3 = {
        codigo: 2 for codigo in base["dimensoes_afinidade"]
    }
    exemplo_afinidades_top3.update({"D01": 5, "D02": 5, "D06": 4, "D09": 3, "D12": 3})
    exemplo_objetivos_top3 = {
        codigo: 2 for codigo in base["objetivos_profissionais"]
    }
    exemplo_objetivos_top3.update({"O01": 5, "O04": 4})
    ranking = gerar_ranking_top3(
        base, exemplo_afinidades_top3, exemplo_objetivos_top3
    )
    print("Situação:", ranking["status"])
    print("Carreiras elegíveis:", ranking["carreiras_elegiveis"])
    for item in ranking["top_3"]:
        print(f"{item['posicao']}º {item['carreira']}: "
              f"{item['compatibilidade_final_percentual']}%")
    print("Empates adicionais na terceira posição:", len(ranking["empates_no_corte"]))

    print("\nRANKING TOP 3 — RESPOSTAS INSUFICIENTES")
    incompleto_top3 = gerar_ranking_top3(
        base, {"D01": 5}, {"O01": 5}
    )
    print("Situação:", incompleto_top3["status"])
    print("Carreiras elegíveis:", incompleto_top3["carreiras_elegiveis"])
    print("Quantidade no Top 3:", len(incompleto_top3["top_3"]))

    print("\nRANKING TOP 3 — CONTRADIÇÃO NÃO CONFIRMADA")
    contraditorio_top3 = gerar_ranking_top3(
        base, exemplo_afinidades_top3, exemplo_objetivos_top3,
        restricoes=["RSTR01"], contradicoes_confirmadas=False,
    )
    print("Situação:", contraditorio_top3["status"])
    print("Alertas:", len(contraditorio_top3["contradicoes"]))
    print("Quantidade no Top 3:", len(contraditorio_top3["top_3"]))


    print("\nSKILL GAPS — PERFIL QA COM DUAS LACUNAS")
    niveis_qa = {
        "QA_01": 2,
        "QA_02": 2,
        "QA_03": 3,
        "QA_04": 0,
        "QA_05": 0,
    }
    lacunas_qa = avaliar_lacunas_competencias(base, "qa", niveis_qa)
    print("Situação:", lacunas_qa["status"])
    for detalhe in lacunas_qa["detalhes"]:
        print(f"{detalhe['competencia']}: atual={detalhe['nivel_atual']}, "
              f"referência={detalhe['nivel_junior']}, lacuna={detalhe['lacuna']}")
    print("Competências com lacuna:", lacunas_qa["competencias_com_lacuna"])
    print("Total de níveis faltantes:", lacunas_qa["total_niveis_de_lacuna"])
    print("Top 3 alterado:", lacunas_qa["altera_ranking_top3"])

    print("\nSKILL GAPS — CONHECIMENTO NÃO INFORMADO")
    niveis_incompletos = dict(niveis_qa)
    niveis_incompletos["QA_05"] = None
    lacunas_incompletas = avaliar_lacunas_competencias(base, "qa", niveis_incompletos)
    print("Situação:", lacunas_incompletas["status"])
    print("Competências pendentes:", ", ".join(lacunas_incompletas["competencias_pendentes"]))
    print("Lacuna da competência não informada:", lacunas_incompletas["detalhes"][-1]["lacuna"])
    print("Total definitivo de níveis faltantes:", lacunas_incompletas["total_niveis_de_lacuna"])


    print("\nROADMAP PERSONALIZADO — QA COM DUAS LACUNAS")
    roteiro_qa = gerar_roadmap_personalizado(base, "qa", niveis_qa)
    print("Situação:", roteiro_qa["status"])
    print("Etapas:", len(roteiro_qa["etapas"]))
    print("Competências com lacuna:", roteiro_qa["competencias_com_lacuna"])
    print("Ordem de estudo:", " → ".join(roteiro_qa["ordem_priorizada"]))
    for etapa in roteiro_qa["etapas"]:
        print(f"{etapa['nome']}: {len(etapa['itens'])} item(ns)")
    print("Projeto:", roteiro_qa["etapas"][2]["itens"][0]["titulo"])
    print("Top 3 alterado:", roteiro_qa["altera_ranking_top3"])

    print("\nROADMAP — CONHECIMENTO NÃO INFORMADO")
    roteiro_incompleto = gerar_roadmap_personalizado(base, "qa", niveis_incompletos)
    print("Situação:", roteiro_incompleto["status"])
    print("Competências pendentes:", ", ".join(roteiro_incompleto["competencias_pendentes"]))
    print("Etapas geradas:", len(roteiro_incompleto["etapas"]))

    print("\nROADMAP — TODAS AS REFERÊNCIAS ATENDIDAS")
    niveis_atendidos = {c["codigo"]: c["nivel_junior"] for c in base["carreiras"]["qa"]["competencias"]}
    roteiro_sem_lacunas = gerar_roadmap_personalizado(base, "qa", niveis_atendidos)
    print("Situação:", roteiro_sem_lacunas["status"])
    print("Estudos obrigatórios:", len(roteiro_sem_lacunas["etapas"][0]["itens"]))
    print("Projeto de consolidação:", roteiro_sem_lacunas["etapas"][2]["itens"][0]["titulo"])


