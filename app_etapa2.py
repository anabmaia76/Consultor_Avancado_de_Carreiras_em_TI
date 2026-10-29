"""Interface Etapa 2: questionário, Top 3, avaliação técnica e roadmap.

Regras e conteúdos são carregados do JSON 0.3.0; cálculos vêm do motor
ponderado. Este arquivo não altera app.py nem motor_inferencia.py originais.
"""

import json
import streamlit as st

from motor_ponderado import (
    carregar_base_conhecimento, gerar_ranking_top3,
    avaliar_lacunas_competencias, gerar_roadmap_personalizado,
)


st.set_page_config(
    page_title="Consultor Avançado de Carreiras em TI — Etapa 2",
    page_icon="💻",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 1050px; padding-top: 2.5rem; padding-bottom: 3rem; }
    .stMarkdown p { font-size: 1.06rem; line-height: 1.55; }
    div[data-testid="stButton"] button { min-height: 3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    base = carregar_base_conhecimento()
except (FileNotFoundError, ValueError, KeyError) as erro:
    st.error("Não foi possível carregar a base de conhecimento da Etapa 2.")
    st.code(str(erro))
    st.stop()

# A sequência das perguntas e as descrições vêm diretamente da base JSON.
dimensoes = list(base["dimensoes_afinidade"].items())
objetivos = list(base["objetivos_profissionais"].items())
restricoes = list(base["restricoes_atividades"].items())
escala_objetivos = base["escalas"]["objetivo"]
rotulos_objetivos = {
    1: "Não combina com meus objetivos",
    2: "Combina pouco",
    3: "Combina moderadamente",
    4: "Combina bastante",
    5: "Combina muito",
}
escala_afinidade = base["escalas"]["afinidade"]
rotulos_afinidade = escala_afinidade["rotulos"]
nota_minima = escala_afinidade["minimo"]
nota_maxima = escala_afinidade["maximo"]
opcao_desconhecida = "Não conheço esta área o suficiente para avaliar"

if "etapa2_tela" not in st.session_state:
    st.session_state["etapa2_tela"] = "inicio"
if "etapa2_indice" not in st.session_state:
    st.session_state["etapa2_indice"] = 0
if "etapa2_respostas_afinidade" not in st.session_state:
    st.session_state["etapa2_respostas_afinidade"] = {}
if "etapa2_indice_objetivo" not in st.session_state:
    st.session_state["etapa2_indice_objetivo"] = 0
if "etapa2_respostas_objetivos" not in st.session_state:
    st.session_state["etapa2_respostas_objetivos"] = {}
if "etapa2_respostas_restricoes" not in st.session_state:
    st.session_state["etapa2_respostas_restricoes"] = []
if "etapa2_confirmacao_perfil" not in st.session_state:
    st.session_state["etapa2_confirmacao_perfil"] = None
if "etapa2_niveis_por_carreira" not in st.session_state:
    st.session_state["etapa2_niveis_por_carreira"] = {}


def identificador_do_perfil():
    """Confirmação vale apenas para as respostas que foram revisadas."""
    dados = {
        "afinidades": st.session_state.etapa2_respostas_afinidade,
        "objetivos": st.session_state.etapa2_respostas_objetivos,
        "restricoes": sorted(st.session_state.etapa2_respostas_restricoes),
    }
    return json.dumps(dados, sort_keys=True, ensure_ascii=False)


def botoes_revisao():
    """Permite revisar o questionário mesmo após gerar o resultado."""
    col_a, col_o, col_r = st.columns(3)
    with col_a:
        if st.button("Revisar afinidades", use_container_width=True):
            st.session_state.etapa2_indice = 0
            st.session_state.etapa2_tela = "afinidades"
            st.rerun()
    with col_o:
        if st.button("Revisar objetivos", use_container_width=True):
            st.session_state.etapa2_indice_objetivo = 0
            st.session_state.etapa2_tela = "objetivos"
            st.rerun()
    with col_r:
        if st.button("Revisar restrições", use_container_width=True):
            st.session_state.etapa2_tela = "restricoes"
            st.rerun()


def ranking_confirmado():
    """Recalcula a classificação para impedir uso de resultado desatualizado."""
    confirmado = (
        st.session_state.etapa2_confirmacao_perfil == identificador_do_perfil()
    )
    try:
        resultado = gerar_ranking_top3(
            base,
            st.session_state.etapa2_respostas_afinidade,
            st.session_state.etapa2_respostas_objetivos,
            restricoes=st.session_state.etapa2_respostas_restricoes,
            contradicoes_confirmadas=confirmado,
        )
    except (ValueError, TypeError, KeyError) as erro:
        st.error("Não foi possível recuperar o ranking atual.")
        st.code(str(erro))
        st.stop()
    if resultado["status"] != "calculada":
        st.warning("O perfil precisa ser concluído ou revisado antes da avaliação técnica.")
        if st.button("Voltar ao Top 3", key="etapa2_voltar_ranking_invalido"):
            st.session_state.etapa2_tela = "resultado_top3"
            st.rerun()
        st.stop()
    return resultado


st.title("💻 Consultor Avançado de Carreiras em TI")
st.caption(f"Etapa 2 • Base de conhecimento v{base['versao_modelo']}")

if st.session_state.etapa2_tela == "inicio":
    st.subheader("Conheça seu perfil profissional")
    st.write(
        "Este sistema avalia seus interesses e objetivos para sugerir carreiras em "
        "Tecnologia da Informação. Depois, poderá identificar competências a "
        "desenvolver e propor uma trilha de aprendizagem."
    )
    st.markdown(
        "**Como funcionará a avaliação:** interesses técnicos, objetivos "
        "profissionais, restrições, três carreiras mais compatíveis e "
        "trilhas de aprendizagem personalizadas."
    )
    st.info(
        "Os resultados representam índices orientativos de compatibilidade "
        "com base nas respostas, não probabilidades de sucesso profissional."
    )
    if st.button("Iniciar avaliação", type="primary", use_container_width=False):
        st.session_state.etapa2_tela = "afinidades"
        st.session_state.etapa2_indice = 0
        st.rerun()

elif st.session_state.etapa2_tela == "afinidades":
    indice = st.session_state.etapa2_indice
    total = len(dimensoes)
    codigo, dados = dimensoes[indice]
    respostas = st.session_state.etapa2_respostas_afinidade

    st.subheader("Etapa 1 — Afinidades técnicas")
    st.caption(f"Pergunta {indice + 1} de {total} · {codigo}")
    st.progress(indice / total)
    st.write(f"**Quanto interesse você tem em: {dados['nome']}?**")
    st.write(dados["descricao"])

    # A nota padrão (3) fica explícita. Ao avançar, o usuário confirma a nota
    # que está na barra. "Não conheço" é uma resposta distinta, salva como null.
    chave_barra = f"etapa2_barra_{codigo}"
    chave_desconhecida = f"etapa2_desconhecida_{codigo}"
    if chave_barra not in st.session_state:
        nota_salva = respostas.get(codigo)
        st.session_state[chave_barra] = (
            int(nota_salva) if nota_salva is not None else 3
        )
    if chave_desconhecida not in st.session_state:
        st.session_state[chave_desconhecida] = (
            codigo in respostas and respostas[codigo] is None
        )

    nao_conhece = st.checkbox(
        opcao_desconhecida,
        key=chave_desconhecida,
        help="Esta resposta não recebe uma nota e não conta como falta de interesse.",
    )
    nota = st.slider(
        "Seu nível de interesse (1 a 5):",
        min_value=nota_minima,
        max_value=nota_maxima,
        step=1,
        key=chave_barra,
        disabled=nao_conhece,
    )
    # Marcas fixas sob a barra: o Streamlit mostra o valor selecionado,
    # mas não fornece marcas intermediárias permanentes no st.slider.
    # Por isso exibimos os números do intervalo em uma linha própria.
    marcas = "".join(
        f"<span>{numero}</span>"
        for numero in range(nota_minima, nota_maxima + 1)
    )
    st.markdown(
        f"""
        <div aria-hidden="true" style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 9px;
            margin: -12px 0 10px 0;
            font-size: 0.88rem;
            color: inherit;
            opacity: 0.85;
        ">{marcas}</div>
        """,
        unsafe_allow_html=True,
    )

    if nao_conhece:
        st.info("Área marcada como desconhecida. Nenhuma nota será atribuída.")
    else:
        st.markdown(f"**Sua avaliação: {nota}/5 — {rotulos_afinidade[str(nota)]}**")
        st.caption(
            "A barra começa em 3 (interesse moderado). Você pode arrastá-la "
            "ou usar as setas do teclado. Ao clicar em Próxima, confirma a nota exibida."
        )

    st.caption(
        "Escala: 1 = Nenhum interesse · 2 = Pouco interesse · "
        "3 = Moderado · 4 = Bastante interesse · 5 = Muito interesse"
    )

    anterior, inicio, proxima = st.columns([1, 1, 1])
    with anterior:
        if st.button("Anterior", disabled=(indice == 0), use_container_width=True):
            # Preserva também uma alteração feita imediatamente antes de voltar.
            respostas[codigo] = None if nao_conhece else int(nota)
            st.session_state.etapa2_indice -= 1
            st.rerun()
    with inicio:
        if st.button("Voltar ao início", use_container_width=True):
            respostas[codigo] = None if nao_conhece else int(nota)
            st.session_state.etapa2_tela = "inicio"
            st.rerun()
    with proxima:
        texto = "Concluir afinidades" if indice == total - 1 else "Próxima"
        if st.button(texto, type="primary", use_container_width=True):
            # O botão confirma a nota atual da barra (ou a resposta desconhecida).
            respostas[codigo] = None if nao_conhece else int(nota)
            if indice == total - 1:
                st.session_state.etapa2_tela = "afinidades_concluidas"
            else:
                st.session_state.etapa2_indice += 1
            st.rerun()

elif st.session_state.etapa2_tela == "afinidades_concluidas":
    respostas = st.session_state.etapa2_respostas_afinidade
    total = len(dimensoes)
    st.subheader("Afinidades registradas!")
    st.progress(1.0)
    st.success(f"Você respondeu às {total} dimensões de afinidade.")
    desconhecidas = sum(valor is None for valor in respostas.values())
    st.write(f"**Dimensões marcadas como desconhecidas:** {desconhecidas}")
    st.info(
        "Próxima etapa: avaliar oito objetivos profissionais, também de 1 a 5. "
        "As restrições serão apresentadas após os objetivos profissionais."
    )
    col_revisar, col_continuar = st.columns(2)
    with col_revisar:
        if st.button("Revisar afinidades", use_container_width=True):
            st.session_state.etapa2_indice = 0
            st.session_state.etapa2_tela = "afinidades"
            st.rerun()
    with col_continuar:
        if st.button("Continuar para objetivos profissionais", type="primary", use_container_width=True):
            st.session_state.etapa2_tela = "objetivos"
            st.rerun()

elif st.session_state.etapa2_tela == "objetivos":
    indice = st.session_state.etapa2_indice_objetivo
    total = len(objetivos)
    codigo, dados = objetivos[indice]
    respostas = st.session_state.etapa2_respostas_objetivos

    st.subheader("Etapa 2 — Objetivos profissionais")
    st.caption(f"Pergunta {indice + 1} de {total} · {codigo}")
    st.progress(indice / total)
    st.write("**Quanto o objetivo abaixo combina com o que você deseja para sua carreira?**")
    st.write(dados["descricao"])

    chave_barra = f"etapa2_barra_objetivo_{codigo}"
    chave_desconhecida = f"etapa2_desconhecido_objetivo_{codigo}"
    if chave_barra not in st.session_state:
        nota_salva = respostas.get(codigo)
        st.session_state[chave_barra] = int(nota_salva) if nota_salva is not None else 3
    if chave_desconhecida not in st.session_state:
        st.session_state[chave_desconhecida] = codigo in respostas and respostas[codigo] is None

    nao_sabe = st.checkbox(
        "Ainda não consigo avaliar este objetivo",
        key=chave_desconhecida,
        help="A resposta será registrada como desconhecida, não como nota 1.",
    )
    nota = st.slider(
        "Seu alinhamento com este objetivo (1 a 5):",
        min_value=escala_objetivos["minimo"],
        max_value=escala_objetivos["maximo"],
        step=1,
        key=chave_barra,
        disabled=nao_sabe,
    )
    # Mesmo padrão das afinidades: números sempre visíveis sob a barra.
    marcas = "".join(
        f"<span>{numero}</span>"
        for numero in range(escala_objetivos["minimo"], escala_objetivos["maximo"] + 1)
    )
    st.markdown(
        f"""
        <div aria-hidden="true" style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 9px;
            margin: -12px 0 10px 0;
            font-size: 0.88rem;
            color: inherit;
            opacity: 0.85;
        ">{marcas}</div>
        """,
        unsafe_allow_html=True,
    )

    if nao_sabe:
        st.info("Objetivo marcado como não avaliado. Nenhuma nota será atribuída.")
    else:
        st.markdown(f"**Sua avaliação: {nota}/5 — {rotulos_objetivos[nota]}**")
        st.caption("A nota inicial é 3. Você pode ajustar a barra antes de confirmar a resposta.")

    st.caption(
        "Escala: 1 = Não combina · 2 = Combina pouco · 3 = Moderadamente "
        "· 4 = Combina bastante · 5 = Combina muito"
    )

    anterior, inicio, proxima = st.columns([1, 1, 1])
    with anterior:
        if st.button("Anterior", use_container_width=True):
            respostas[codigo] = None if nao_sabe else int(nota)
            if indice == 0:
                st.session_state.etapa2_tela = "afinidades_concluidas"
            else:
                st.session_state.etapa2_indice_objetivo -= 1
            st.rerun()
    with inicio:
        if st.button("Voltar ao início", use_container_width=True):
            respostas[codigo] = None if nao_sabe else int(nota)
            st.session_state.etapa2_tela = "inicio"
            st.rerun()
    with proxima:
        texto = "Concluir objetivos" if indice == total - 1 else "Próxima"
        if st.button(texto, type="primary", use_container_width=True):
            respostas[codigo] = None if nao_sabe else int(nota)
            if indice == total - 1:
                st.session_state.etapa2_tela = "objetivos_concluidos"
            else:
                st.session_state.etapa2_indice_objetivo += 1
            st.rerun()

elif st.session_state.etapa2_tela == "objetivos_concluidos":
    respostas = st.session_state.etapa2_respostas_objetivos
    st.subheader("Objetivos profissionais registrados!")
    st.progress(1.0)
    st.success(f"Você concluiu as {len(objetivos)} perguntas de objetivos profissionais.")
    desconhecidos = sum(valor is None for valor in respostas.values())
    st.write(f"**Objetivos não avaliados:** {desconhecidos}")
    st.info(
        "As 13 afinidades e os oito objetivos já foram registrados. "
        "Agora vamos conhecer as atividades que você prefere evitar. "
        "O Top 3 será integrado em uma etapa posterior."
    )
    col_afinidades, col_objetivos, col_restricoes = st.columns(3)
    with col_afinidades:
        if st.button("Revisar afinidades", use_container_width=True):
            st.session_state.etapa2_tela = "afinidades_concluidas"
            st.rerun()
    with col_objetivos:
        if st.button("Revisar objetivos", use_container_width=True):
            st.session_state.etapa2_indice_objetivo = 0
            st.session_state.etapa2_tela = "objetivos"
            st.rerun()
    with col_restricoes:
        if st.button("Continuar para restrições", type="primary", use_container_width=True):
            st.session_state.etapa2_tela = "restricoes"
            st.rerun()

elif st.session_state.etapa2_tela == "restricoes":
    st.subheader("Etapa 3 — Atividades que prefere evitar")
    st.caption(f"{len(restricoes)} atividades possíveis · Seleção múltipla")
    st.write(
        "**Existe alguma atividade que você prefere evitar no trabalho?** "
        "Marque quantas quiser. Caso nenhuma se aplique, deixe todas desmarcadas."
    )
    st.info(
        "Essas preferências serão utilizadas para ajustar as recomendações. "
        "Marcar uma atividade não elimina automaticamente nenhuma carreira."
    )

    # As seleções persistentes ficam separadas das chaves dos widgets: o
    # Streamlit pode remover chaves de checkboxes ao trocar de tela.
    salvas = set(st.session_state.etapa2_respostas_restricoes)
    escolhidas = []
    for codigo, dados in restricoes:
        chave = f"etapa2_checkbox_restricao_{codigo}"
        if chave not in st.session_state:
            st.session_state[chave] = codigo in salvas
        marcada = st.checkbox(dados["descricao"], key=chave)
        if marcada:
            escolhidas.append(codigo)

    st.session_state.etapa2_respostas_restricoes = escolhidas
    if escolhidas:
        st.caption(f"Atividades selecionadas: {len(escolhidas)}")
    else:
        st.caption("Nenhuma atividade selecionada. Você pode continuar assim.")

    col_voltar, col_inicio, col_continuar = st.columns(3)
    with col_voltar:
        if st.button("Anterior", use_container_width=True):
            st.session_state.etapa2_tela = "objetivos_concluidos"
            st.rerun()
    with col_inicio:
        if st.button("Voltar ao início", use_container_width=True):
            st.session_state.etapa2_tela = "inicio"
            st.rerun()
    with col_continuar:
        if st.button("Concluir restrições", type="primary", use_container_width=True):
            st.session_state.etapa2_tela = "restricoes_concluidas"
            st.rerun()

elif st.session_state.etapa2_tela == "restricoes_concluidas":
    escolhidas = st.session_state.etapa2_respostas_restricoes
    st.subheader("Perfil inicial registrado!")
    st.progress(1.0)
    st.success("As etapas de afinidades, objetivos e restrições foram concluídas.")
    st.write(f"**Afinidades respondidas:** {len(st.session_state.etapa2_respostas_afinidade)} de {len(dimensoes)}")
    st.write(f"**Objetivos respondidos:** {len(st.session_state.etapa2_respostas_objetivos)} de {len(objetivos)}")
    st.write(f"**Atividades que prefere evitar:** {len(escolhidas)}")
    if escolhidas:
        for codigo, dados in restricoes:
            if codigo in escolhidas:
                st.write(f"- {dados['descricao']}")
    else:
        st.write("Você não selecionou nenhuma atividade para evitar.")
    st.info(
        "Você já pode calcular as três carreiras mais compatíveis. "
        "Se houver respostas aparentemente contraditórias, o sistema "
        "solicitará uma confirmação antes de apresentar os resultados."
    )
    botoes_revisao()
    if st.button("Calcular meu Top 3", type="primary", use_container_width=True):
        st.session_state.etapa2_tela = "resultado_top3"
        st.rerun()

elif st.session_state.etapa2_tela == "resultado_top3":
    st.subheader("Etapa 4 — Seu Top 3 de carreiras em TI")
    st.caption("Índices orientativos de compatibilidade, não probabilidades de contratação.")

    afinidades = st.session_state.etapa2_respostas_afinidade
    respostas_objetivos = st.session_state.etapa2_respostas_objetivos
    selecionadas = st.session_state.etapa2_respostas_restricoes
    perfil_atual = identificador_do_perfil()
    confirmado = st.session_state.etapa2_confirmacao_perfil == perfil_atual

    # O motor faz a validação de cobertura e impede apresentar resultados com
    # contradições não confirmadas. A confirmação não sobrevive à edição do perfil.
    try:
        ranking = gerar_ranking_top3(
            base, afinidades, respostas_objetivos,
            restricoes=selecionadas,
            contradicoes_confirmadas=confirmado,
        )
    except (ValueError, TypeError, KeyError) as erro:
        st.error("Não foi possível calcular o ranking com os dados informados.")
        st.code(str(erro))
        botoes_revisao()
        st.stop()

    if ranking["status"] == "revisao_pendente":
        st.warning(
            "Identificamos respostas que podem parecer contraditórias. "
            "Você pode revisá-las ou confirmar que representam suas preferências. "
            "Nenhuma resposta será alterada automaticamente."
        )
        for alerta in ranking["contradicoes"]:
            nome_dimensao = base["dimensoes_afinidade"][alerta["dimensao"]]["nome"]
            st.markdown(
                f"**{alerta['descricao_restricao']}**  "
                f"— afinidade com **{nome_dimensao}**: "
                f"**{alerta['nota_afinidade']}/5**."
            )
        st.caption(
            "Confirmar uma contradição mantém a restrição e permite aplicar "
            "as penalidades cadastradas, quando pertinentes."
        )
        confirmou = st.checkbox(
            "Revisei as respostas e confirmo que desejo mantê-las assim.",
            key="etapa2_aceite_contradicoes",
        )
        if st.button(
            "Confirmar respostas e calcular Top 3",
            type="primary", use_container_width=True, disabled=not confirmou,
        ):
            st.session_state.etapa2_confirmacao_perfil = perfil_atual
            st.rerun()

    elif ranking["status"] == "dados_insuficientes":
        st.warning(ranking["mensagem"])
        st.write(
            f"**Carreiras com cobertura suficiente:** "
            f"{ranking['carreiras_elegiveis']} de {len(base['carreiras'])}."
        )
        with st.expander("Consultar a cobertura por carreira"):
            for item in ranking["carreiras_com_dados_insuficientes"]:
                st.write(
                    f"**{item['carreira']}** — "
                    f"afinidades: {item['cobertura_afinidade']:.1f}% · "
                    f"objetivos: {item['cobertura_objetivos']:.1f}%"
                )
        st.info(
            "Revise as perguntas marcadas como desconhecidas para fornecer "
            "mais informações. A cobertura mínima por carreira é 70% em "
            "afinidades e 70% em objetivos."
        )

    elif ranking["status"] == "calculada":
        st.success("Classificação concluída! Estas são as três carreiras mais compatíveis.")
        st.caption(
            "O resultado considera 80% de afinidades e 20% de objetivos, "
            "descontando as penalidades por restrições declaradas."
        )
        for item in ranking["top_3"]:
            st.markdown(f"### {item['posicao']}º — {item['carreira']}")
            st.metric("Compatibilidade estimada", f"{item['compatibilidade_final_percentual']:.2f}%")
            st.progress(max(0.0, min(1.0, item["compatibilidade_final_percentual"] / 100)))
            with st.expander(f"Entenda o resultado de {item['carreira']}"):
                st.write(
                    f"Afinidade ponderada: **{item['afinidade_percentual']:.2f}%** · "
                    f"Objetivos profissionais: **{item['objetivos_percentual']:.2f}%**."
                )
                st.write(
                    f"Compatibilidade antes das penalidades: "
                    f"**{item['compatibilidade_inicial_percentual']:.2f}%**."
                )
                st.write(
                    f"Penalidade aplicada: "
                    f"**{item['penalidade_aplicada_pontos_percentuais']} ponto(s) percentual(is)**."
                )
                st.write(
                    f"Cobertura: afinidades **{item['cobertura_afinidade_percentual']:.1f}%**, "
                    f"objetivos **{item['cobertura_objetivos_percentual']:.1f}%**."
                )
                carreira = base["carreiras"][item["codigo_carreira"]]
                principais_afinidades = sorted(
                    (
                        (peso * (afinidades[codigo] - 1), peso, codigo, afinidades[codigo])
                        for codigo, peso in carreira["pesos_afinidade"].items()
                        if afinidades.get(codigo) is not None
                    ),
                    reverse=True,
                )[:3]
                if principais_afinidades:
                    st.write("**Afinidades que mais contribuíram:**")
                    for _, peso, codigo, nota in principais_afinidades:
                        nome = base["dimensoes_afinidade"][codigo]["nome"]
                        st.write(f"- {nome}: interesse {nota}/5, peso {peso}/5")
                principais_objetivos = sorted(
                    (
                        (peso * (respostas_objetivos[codigo] - 1), peso, codigo, respostas_objetivos[codigo])
                        for codigo, peso in carreira["pesos_objetivos"].items()
                        if respostas_objetivos.get(codigo) is not None
                    ),
                    reverse=True,
                )[:2]
                if principais_objetivos:
                    st.write("**Objetivos que mais contribuíram:**")
                    for _, peso, codigo, nota in principais_objetivos:
                        descricao = base["objetivos_profissionais"][codigo]["descricao"]
                        st.write(f"- {descricao}: alinhamento {nota}/5, peso {peso}/5")
                if item["justificativas_penalidades"]:
                    st.write("**Restrições consideradas:**")
                    for regra in item["justificativas_penalidades"]:
                        st.write(
                            f"- {regra['descricao']} "
                            f"(−{regra['pontos_percentuais']} p.p. antes do limite acumulado)"
                        )
                else:
                    st.write("Nenhuma penalidade aplicada a esta carreira.")

        if ranking["empates_no_corte"]:
            st.info(
                "Existem outras carreiras empatadas com a terceira colocada: "
                + ", ".join(
                    f"{item['carreira']} ({item['compatibilidade_final_percentual']:.2f}%)"
                    for item in ranking["empates_no_corte"]
                )
            )
        with st.expander("Ver classificação completa e critério de desempate"):
            for item in ranking["classificacao_completa"]:
                st.write(
                    f"{item['posicao']}º — {item['carreira']}: "
                    f"{item['compatibilidade_final_percentual']:.2f}%"
                )
            st.caption(ranking["criterio_ordenacao"])
        st.info(
            "Agora você pode escolher uma das três carreiras, avaliar suas "
            "cinco competências e obter uma trilha de aprendizagem personalizada."
        )
        if st.button(
            "Avaliar competências e montar meu roadmap",
            type="primary", use_container_width=True,
        ):
            st.session_state.etapa2_tela = "competencias"
            st.rerun()

    else:
        st.error(f"O motor retornou uma situação inesperada: {ranking['status']}")

    st.divider()
    botoes_revisao()


elif st.session_state.etapa2_tela == "competencias":
    ranking = ranking_confirmado()
    st.subheader("Etapa 5 — Avaliação das competências técnicas")
    st.write(
        "Escolha uma das carreiras do seu Top 3. Vamos comparar seu conhecimento "
        "atual com cinco níveis de referência para iniciar uma carreira Júnior."
    )
    st.info(
        "Esta avaliação é autodeclarada e serve apenas para orientar os estudos. "
        "Ela não altera os percentuais de compatibilidade do Top 3."
    )

    opcoes = [item["codigo_carreira"] for item in ranking["top_3"]]
    nomes_opcoes = {
        item["codigo_carreira"]: (
            f"{item['posicao']}º — {item['carreira']} "
            f"({item['compatibilidade_final_percentual']:.2f}%)"
        )
        for item in ranking["top_3"]
    }
    if (
        "etapa2_carreira_escolhida" not in st.session_state
        or st.session_state["etapa2_carreira_escolhida"] not in opcoes
    ):
        st.session_state["etapa2_carreira_escolhida"] = opcoes[0]

    codigo_carreira = st.radio(
        "Qual carreira você gostaria de explorar primeiro?",
        options=opcoes,
        format_func=lambda codigo: nomes_opcoes[codigo],
        key="etapa2_carreira_escolhida",
    )
    carreira = base["carreiras"][codigo_carreira]
    competencias = carreira["competencias"]
    por_carreira = st.session_state.etapa2_niveis_por_carreira
    if codigo_carreira not in por_carreira:
        por_carreira[codigo_carreira] = {}
    niveis = por_carreira[codigo_carreira]

    st.markdown(f"#### Competências de {carreira['nome']}")
    st.caption(
        "Escala: 0 = Nenhum conhecimento · 1 = Básico · "
        "2 = Intermediário · 3 = Prático com relativa autonomia. "
        "As barras iniciam em 0: confira e ajuste cada uma antes de concluir."
    )

    for competencia in competencias:
        codigo = competencia["codigo"]
        chave_barra = f"etapa2_conhecimento_barra_{codigo}"
        chave_desconhecida = f"etapa2_conhecimento_desconhecido_{codigo}"
        if chave_barra not in st.session_state:
            nivel_salvo = niveis.get(codigo)
            st.session_state[chave_barra] = (
                nivel_salvo if isinstance(nivel_salvo, int) else 0
            )
        if chave_desconhecida not in st.session_state:
            st.session_state[chave_desconhecida] = (
                codigo in niveis and niveis[codigo] is None
            )

        st.markdown(f"**{competencia['nome']}**")
        st.caption(
            f"Referência Júnior: nível {competencia['nivel_junior']}/3 "
            "(parâmetro orientativo da base de conhecimento)"
        )
        desconhecida = st.checkbox(
            "Ainda não consigo avaliar esta competência",
            key=chave_desconhecida,
        )
        nivel = st.slider(
            f"Meu conhecimento em {competencia['nome']} (0 a 3)",
            min_value=0,
            max_value=3,
            step=1,
            key=chave_barra,
            disabled=desconhecida,
        )
        # Mantém os quatro números fixos e distribuídos sob toda a barra.
        # As propriedades flex precisam estar DENTRO do atributo style.
        st.markdown(
            """
            <div aria-hidden="true" style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 9px;
                margin: -12px 0 12px 0;
                font-size: 0.88rem;
                color: inherit;
                opacity: 0.85;
            "><span>0</span><span>1</span><span>2</span><span>3</span></div>
            """,
            unsafe_allow_html=True,
        )
        niveis[codigo] = None if desconhecida else int(nivel)
        if desconhecida:
            st.caption("Não avaliada — essa competência não será considerada nível zero.")
        else:
            lacuna = max(0, competencia["nivel_junior"] - int(nivel))
            if lacuna:
                st.caption(f"Diferença para a referência: {lacuna} nível(is).")
            else:
                st.caption("Referência Júnior atendida nesta competência.")
        st.divider()

    col_voltar, col_gerar = st.columns(2)
    with col_voltar:
        if st.button("Voltar ao Top 3", use_container_width=True):
            st.session_state.etapa2_tela = "resultado_top3"
            st.rerun()
    with col_gerar:
        if st.button("Gerar minha trilha de aprendizagem", type="primary", use_container_width=True):
            st.session_state.etapa2_tela = "roadmap"
            st.rerun()

elif st.session_state.etapa2_tela == "roadmap":
    ranking = ranking_confirmado()
    opcoes = [item["codigo_carreira"] for item in ranking["top_3"]]
    codigo_carreira = st.session_state.get("etapa2_carreira_escolhida")
    if codigo_carreira not in opcoes:
        st.warning("Escolha uma carreira do Top 3 para analisar as competências.")
        if st.button("Escolher carreira"):
            st.session_state.etapa2_tela = "competencias"
            st.rerun()
        st.stop()

    niveis = st.session_state.etapa2_niveis_por_carreira.get(codigo_carreira, {})
    try:
        avaliacao = avaliar_lacunas_competencias(base, codigo_carreira, niveis)
        roteiro = gerar_roadmap_personalizado(base, codigo_carreira, niveis)
    except (ValueError, TypeError, KeyError) as erro:
        st.error("Não foi possível gerar a trilha de aprendizagem.")
        st.code(str(erro))
        if st.button("Revisar competências"):
            st.session_state.etapa2_tela = "competencias"
            st.rerun()
        st.stop()

    st.subheader(f"Etapa 6 — Seu roadmap: {roteiro['carreira']}")
    st.caption(
        "Orientações baseadas no conhecimento informado e nos níveis de referência "
        "Júnior do JSON. Não constituem avaliação profissional formal."
    )
    if roteiro["status"] == "avaliacao_incompleta":
        st.warning("Algumas competências não foram avaliadas. O roadmap definitivo não foi gerado.")
        mapa_nomes = {
            competencia["codigo"]: competencia["nome"]
            for competencia in base["carreiras"][codigo_carreira]["competencias"]
        }
        for codigo in roteiro["competencias_pendentes"]:
            st.write(f"- {mapa_nomes[codigo]}")
        if st.button("Voltar e preencher os conhecimentos", type="primary"):
            st.session_state.etapa2_tela = "competencias"
            st.rerun()
    else:
        if roteiro["status"] == "sem_lacunas":
            st.success("Você informou níveis que já atendem a todas as referências Júnior cadastradas.")
        else:
            st.success("Roadmap personalizado gerado a partir das lacunas identificadas!")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Competências avaliadas", avaliacao["quantidade_respondida"])
        with col_b:
            st.metric("Competências com lacuna", roteiro["competencias_com_lacuna"])
        with col_c:
            st.metric("Níveis a desenvolver", roteiro["total_niveis_de_lacuna"])

        st.markdown("#### Comparação de competências")
        linhas = []
        for item in avaliacao["detalhes"]:
            linhas.append({
                "Competência": item["competencia"],
                "Atual": item["nivel_atual"],
                "Referência Júnior": item["nivel_junior"],
                "Lacuna": item["lacuna"],
                "Situação": (
                    "Referência atendida" if item["lacuna"] == 0
                    else "Desenvolver"
                ),
            })
        st.table(linhas)

        if roteiro["ordem_priorizada"]:
            nomes = {
                comp["codigo"]: comp["nome"]
                for comp in base["carreiras"][codigo_carreira]["competencias"]
            }
            st.write(
                "**Ordem recomendada de estudo:** "
                + " → ".join(nomes[codigo] for codigo in roteiro["ordem_priorizada"])
            )
        else:
            st.info("Sem lacunas a desenvolver: use o projeto sugerido para consolidar sua experiência.")

        st.markdown("#### Sua trilha de aprendizagem")
        for indice, etapa in enumerate(roteiro["etapas"], start=1):
            with st.expander(f"{indice}. {etapa['nome']}", expanded=(indice == 1)):
                st.caption(etapa["objetivo"])
                for item in etapa["itens"]:
                    if etapa["codigo"] == "fundamentos":
                        st.markdown(f"**{item['competencia']}** — {item['abordagem']}")
                        if item["pre_requisitos"]:
                            st.caption(
                                "Pré-requisitos: " + ", ".join(
                                    prereq["competencia"] for prereq in item["pre_requisitos"]
                                )
                            )
                        for conteudo in item["conteudos"]:
                            st.write(f"- {conteudo}")
                    elif etapa["codigo"] == "desenvolvimento_tecnico":
                        st.markdown(f"**{item['competencia']}**")
                        for atividade in item["atividades"]:
                            st.write(f"- {atividade}")
                        if item["tecnologias_sugeridas"]:
                            st.caption("Tecnologias: " + ", ".join(item["tecnologias_sugeridas"]))
                    elif etapa["codigo"] == "projeto_portfolio":
                        st.markdown(f"**{item['titulo']}**")
                        st.write(item["descricao"])
                        st.caption(item["orientacao"])
                        st.markdown("**Entregáveis sugeridos:**")
                        for entregavel in item["entregaveis"]:
                            st.write(f"- {entregavel}")
                        if item["competencias_relacionadas_com_lacuna"]:
                            st.caption(
                                "Competências que o projeto ajudará a desenvolver: "
                                + ", ".join(
                                    comp["competencia"]
                                    for comp in item["competencias_relacionadas_com_lacuna"]
                                )
                            )
                        st.caption(f"Plataforma sugerida: {item['plataforma_sugerida']}")
                    elif etapa["codigo"] == "consolidacao":
                        for acao in item["acoes"]:
                            st.write(f"- {acao}")
                        certs = item["certificacoes_opcionais"]
                        if certs:
                            st.markdown("**Certificações opcionais:**")
                            for cert in certs:
                                st.markdown(f"- [{cert['nome']}]({cert['url_oficial']}) — {cert['observacao']}")
        st.caption(
            "As certificações são opcionais; consulte os sites oficiais para "
            "confirmar condições atuais, preços e disponibilidade."
        )

    st.divider()
    col_revisar, col_top3 = st.columns(2)
    with col_revisar:
        if st.button("Revisar competências", use_container_width=True):
            st.session_state.etapa2_tela = "competencias"
            st.rerun()
    with col_top3:
        if st.button("Voltar ao Top 3", use_container_width=True, key="etapa2_top3_do_roadmap"):
            st.session_state.etapa2_tela = "resultado_top3"
            st.rerun()
