from html import escape

import streamlit as st

from motor_inferencia import MotorInferencia, Resposta
from perguntas import PERGUNTAS


NOMES_CARREIRAS = {
    "backend": "Desenvolvimento Back-end",
    "frontend": "Desenvolvimento Front-end e UI/UX",
    "ciencia_dados": "Ciência de Dados e Machine Learning",
    "engenharia_dados": "Engenharia de Dados",
    "ciberseguranca": "Cibersegurança",
    "devops": "DevOps e SRE",
    "nuvem": "Computação em Nuvem",
    "mobile": "Desenvolvimento Mobile",
    "qa": "Engenharia de Qualidade e Testes (QA)",
    "gestao_produtos": "Gestão de Produtos Digitais",
}


st.set_page_config(
    page_title="Consultor Inteligente de Carreiras em TI",
    page_icon="💻",
    layout="wide",
)

st.markdown("""
<style>
    .block-container {
        max-width: 1150px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }
    .stMarkdown p {
        font-size: 1.10rem;
        line-height: 1.6;
    }
    .enunciado-pergunta {
        font-size: 1.35rem !important;
        font-weight: 700;
        line-height: 1.40;
        margin-top: 0.55rem;
        margin-bottom: 0.45rem;
    }
    div[data-testid="stRadio"] [role="radiogroup"] label,
    div[data-testid="stRadio"] [role="radiogroup"] label p,
    div[data-testid="stRadio"] [role="radiogroup"] label span {
        font-size: 1.17rem !important;
        line-height: 1.40 !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] label {
        padding-top: 0.10rem;
        padding-bottom: 0.10rem;
    }
    div[data-testid="stButton"] button {
        min-height: 3.2rem;
        font-size: 1.05rem;
    }
    @media (max-width: 700px) {
        .block-container { padding-top: 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)


VALORES_INICIAIS = {
    "tela": "inicio",
    "indice_pergunta": 0,
    "respostas": {},
    "analise": None,
    "pergunta_extra": None,
    "recomendacao": None,
    "criterio_recomendacao": None,
    "justificativa_desempate": None,
    "rodada_desempate": 0,
}
for nome, valor in VALORES_INICIAIS.items():
    if nome not in st.session_state:
        st.session_state[nome] = valor.copy() if isinstance(valor, dict) else valor

codigos = list(PERGUNTAS)
total = len(codigos)


def validar_respostas(respostas):
    if set(respostas) != set(PERGUNTAS):
        raise ValueError("Todas as dez perguntas precisam ser respondidas.")
    for codigo, escolha in respostas.items():
        if escolha not in PERGUNTAS[codigo]["opcoes"]:
            raise ValueError(f"Alternativa invalida para a pergunta {codigo}.")


def limpar_analise():
    st.session_state.analise = None
    st.session_state.pergunta_extra = None
    st.session_state.recomendacao = None
    st.session_state.criterio_recomendacao = None
    st.session_state.justificativa_desempate = None


def reiniciar_entrevista():
    for codigo in codigos:
        st.session_state.pop(f"alternativa_{codigo}", None)
    limpar_analise()
    st.session_state.respostas = {}
    st.session_state.indice_pergunta = 0
    st.session_state.tela = "inicio"


def processar_entrevista(respostas):
    validar_respostas(respostas)

    motor = MotorInferencia()
    motor.reset()
    for codigo, escolha in respostas.items():
        motor.declare(Resposta(pergunta=codigo, valor=escolha))
    motor.run()

    resultado = motor.calcular_resultado(respostas)
    desempate = motor.resolver_empate_por_ferramenta(resultado, respostas)
    st.session_state.analise = {
        "resultado": resultado,
        "desempate": desempate,
    }
    st.session_state.recomendacao = None
    st.session_state.criterio_recomendacao = None
    st.session_state.justificativa_desempate = None
    st.session_state.pergunta_extra = None
    st.session_state.rodada_desempate += 1

    if desempate["precisa_pergunta_extra"]:
        st.session_state.pergunta_extra = motor.gerar_pergunta_adicional(
            desempate["candidatas"]
        )
        st.session_state.tela = "desempate"
    else:
        st.session_state.recomendacao = desempate["candidatas"][0]
        st.session_state.criterio_recomendacao = desempate["criterio"]
        st.session_state.tela = "resultado"


def conferir_respostas():
    with st.expander("Conferir minhas respostas"):
        for codigo, pergunta in PERGUNTAS.items():
            escolha = st.session_state.respostas.get(codigo)
            st.markdown(f"**{codigo} — {pergunta['enunciado']}**")
            if escolha in pergunta["opcoes"]:
                st.write(pergunta["opcoes"][escolha])
            else:
                st.warning("Esta pergunta ainda nao foi respondida.")


def botoes_finais():
    col_revisar, col_reiniciar = st.columns(2)
    with col_revisar:
        if st.button("Revisar respostas", use_container_width=True):
            limpar_analise()
            st.session_state.indice_pergunta = 0
            st.session_state.tela = "questionario"
            st.rerun()
    with col_reiniciar:
        if st.button("Reiniciar questionário", use_container_width=True):
            reiniciar_entrevista()
            st.rerun()


if st.session_state.tela == "concluido":
    try:
        processar_entrevista(st.session_state.respostas)
    except ValueError:
        st.session_state.tela = "questionario"
        st.session_state.indice_pergunta = 0


if st.session_state.tela == "inicio":
    st.title("💻 Consultor Inteligente de Carreiras em TI")
    st.write(
        "Bem-vindo! Este sistema ajuda você a explorar áreas profissionais "
        "da Tecnologia da Informação de acordo com seus interesses e preferências."
    )
    st.subheader("Como funciona?")
    st.write(
        "Você responderá a 10 perguntas sobre suas afinidades com tecnologia, "
        "atividades profissionais e objetivos."
    )
    st.write(
        "Um motor de inferência baseado em 25 regras analisará suas respostas "
        "e apresentará uma recomendação de carreira, acompanhada das justificativas."
    )
    st.info(
        "O resultado será uma sugestão de orientação profissional, "
        "não uma avaliação definitiva de suas habilidades."
    )
    rotulo = (
        "Continuar questionário"
        if st.session_state.respostas
        else "Iniciar questionário"
    )
    if st.button(rotulo, type="primary"):
        st.session_state.tela = "questionario"
        st.rerun()

elif st.session_state.tela == "questionario":
    indice = st.session_state.indice_pergunta
    codigo = codigos[indice]
    pergunta = PERGUNTAS[codigo]
    alternativas = pergunta["opcoes"]
    chaves = list(alternativas)

    st.title("Questionário de Carreiras em TI")
    st.caption(f"Pergunta {indice + 1} de {total}")
    st.progress(len(st.session_state.respostas) / total)
    st.caption(f"{len(st.session_state.respostas)} de {total} perguntas respondidas")

    resposta_salva = st.session_state.respostas.get(codigo)
    indice_selecionado = (
        chaves.index(resposta_salva) if resposta_salva in chaves else None
    )
    st.markdown(
        f'<div class="enunciado-pergunta">{escape(pergunta["enunciado"])}</div>',
        unsafe_allow_html=True,
    )
    escolha = st.radio(
        pergunta["enunciado"],
        options=chaves,
        format_func=lambda chave: alternativas[chave],
        index=indice_selecionado,
        key=f"alternativa_{codigo}",
        label_visibility="collapsed",
    )

    col_voltar, col_inicio, col_avancar = st.columns(3)
    with col_voltar:
        if st.button("Anterior", disabled=(indice == 0), use_container_width=True):
            if escolha is not None:
                st.session_state.respostas[codigo] = escolha
            st.session_state.indice_pergunta -= 1
            st.rerun()
    with col_inicio:
        if st.button("Voltar ao início", use_container_width=True):
            if escolha is not None:
                st.session_state.respostas[codigo] = escolha
            st.session_state.tela = "inicio"
            st.rerun()
    with col_avancar:
        ultimo = indice == total - 1
        rotulo = "Concluir" if ultimo else "Próxima"
        if st.button(rotulo, type="primary", use_container_width=True):
            if escolha is None:
                st.warning("Selecione uma alternativa para continuar.")
            else:
                st.session_state.respostas[codigo] = escolha
                if ultimo:
                    processar_entrevista(st.session_state.respostas)
                else:
                    st.session_state.indice_pergunta += 1
                st.rerun()

elif st.session_state.tela == "desempate":
    st.title("Precisamos de mais uma resposta")
    st.info(
        "Duas ou mais carreiras receberam pontuações iguais. "
        "Sua escolha ajudará a finalizar a recomendação."
    )
    pergunta = st.session_state.pergunta_extra
    st.markdown(
        f'<div class="enunciado-pergunta">{escape(pergunta["enunciado"])}</div>',
        unsafe_allow_html=True,
    )
    chaves = list(pergunta["opcoes"])
    escolha = st.radio(
        pergunta["enunciado"],
        options=chaves,
        format_func=lambda chave: pergunta["opcoes"][chave],
        index=None,
        key=f"escolha_atividade_extra_{st.session_state.rodada_desempate}",
        label_visibility="collapsed",
    )
    if st.button("Confirmar preferência", type="primary"):
        if escolha is None:
            st.warning("Selecione uma atividade para continuar.")
        else:
            motor = MotorInferencia()
            decisao = motor.resolver_pergunta_adicional(pergunta, escolha)
            st.session_state.recomendacao = decisao["carreira"]
            st.session_state.criterio_recomendacao = decisao["criterio"]
            st.session_state.justificativa_desempate = decisao["justificativa"]
            st.session_state.tela = "resultado"
            st.rerun()
    if st.button("Revisar respostas anteriores"):
        limpar_analise()
        st.session_state.indice_pergunta = 0
        st.session_state.tela = "questionario"
        st.rerun()

elif st.session_state.tela == "resultado":
    analise = st.session_state.analise
    resultado = analise["resultado"]
    carreira = st.session_state.recomendacao
    criterio = st.session_state.criterio_recomendacao

    st.title("Sua recomendação de carreira")
    st.success(f"**{NOMES_CARREIRAS[carreira]}**")
    st.metric("Pontuação da carreira", f"{resultado['pontuacoes'][carreira]} de 6")
    st.caption(
        "Pontuação calculada por regras do sistema, não uma porcentagem "
        "de aptidão ou garantia de sucesso profissional."
    )

    if criterio == "ferramenta":
        carreiras_empatadas = ", ".join(
            NOMES_CARREIRAS[codigo]
            for codigo in resultado["carreiras_empatadas"]
        )
        ferramenta = PERGUNTAS["P3"]["opcoes"][st.session_state.respostas["P3"]]
        st.info(
            f"Houve empate de {resultado['maior_pontuacao']} pontos entre "
            f"{carreiras_empatadas}. A afinidade com {ferramenta}, informada "
            f"na Pergunta 3, foi utilizada para recomendar "
            f"{NOMES_CARREIRAS[carreira]}, sem acrescentar pontos."
        )
    elif criterio == "pergunta_adicional":
        st.info(
            "Houve empate na pontuação, e sua preferência pela atividade "
            "adicional foi utilizada para definir a recomendação."
        )
        st.write(st.session_state.justificativa_desempate)
    else:
        st.write("Esta carreira obteve a maior pontuação na análise das suas respostas.")

    st.subheader("Por que esta carreira foi recomendada?")
    regras_carreira = sorted(
        [
            regra for regra in resultado["regras_ativadas"]
            if regra["carreira"] == carreira
        ],
        key=lambda regra: regra["regra"],
    )
    if regras_carreira:
        for regra in regras_carreira:
            st.markdown(
                f"**{regra['regra']} (+{regra['pontos']} pontos):** "
                f"{regra['motivo']}"
            )
    else:
        st.write(
            "Nenhuma regra cruzada específica para esta carreira foi ativada. "
            "A recomendação se baseou na preferência declarada e nos "
            "critérios de desempate, quando aplicáveis."
        )

    if resultado["carreira_p4"] == carreira:
        st.markdown("**Preferência da Pergunta 4 (+1 ponto):**")
        st.write(PERGUNTAS["P4"]["opcoes"][st.session_state.respostas["P4"]])
    pontos_brutos_regras = sum(regra["pontos"] for regra in regras_carreira)
    if pontos_brutos_regras > 5:
        texto_p4 = (
            " A preferência da Pergunta 4 acrescentou mais 1 ponto."
            if resultado["carreira_p4"] == carreira
            else " A Pergunta 4 não acrescentou pontos para esta carreira."
        )
        st.caption(
            f"As regras ativadas somaram {pontos_brutos_regras} pontos, "
            "mas somente 5 foram contabilizados, conforme o limite do "
            f"sistema.{texto_p4}"
        )
    else:
        st.caption(
            "Cada carreira pode receber até 5 pontos pelas regras, mais 1 "
            "pela preferência da Pergunta 4."
        )

    with st.expander("Comparar pontuações das dez carreiras"):
        ordenadas = sorted(
            resultado["pontuacoes"].items(),
            key=lambda item: (-item[1], NOMES_CARREIRAS[item[0]]),
        )
        st.table({
            "Carreira": [NOMES_CARREIRAS[c] for c, _ in ordenadas],
            "Pontos": [pontos for _, pontos in ordenadas],
        })

    with st.expander("Consultar todas as regras ativadas"):
        if resultado["regras_ativadas"]:
            for regra in sorted(
                resultado["regras_ativadas"], key=lambda item: item["regra"]
            ):
                st.markdown(
                    f"**{regra['regra']} — {NOMES_CARREIRAS[regra['carreira']]} "
                    f"(+{regra['pontos']}):** {regra['motivo']}"
                )
        else:
            st.write("Nenhuma regra cruzada foi ativada nesta entrevista.")

    conferir_respostas()
    st.info(
        "Esta recomendação é uma orientação exploratória baseada nas "
        "preferências informadas. Não substitui aconselhamento profissional."
    )
    botoes_finais()
