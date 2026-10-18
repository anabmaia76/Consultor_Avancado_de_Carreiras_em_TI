
from motor_inferencia import MotorInferencia, Resposta
from perguntas import PERGUNTAS


def executar_perfil(respostas):
    assert set(respostas) == set(PERGUNTAS)

    for pergunta, valor in respostas.items():
        assert valor in PERGUNTAS[pergunta]["opcoes"]

    motor = MotorInferencia()
    motor.reset()

    for pergunta, valor in respostas.items():
        motor.declare(Resposta(pergunta=pergunta, valor=valor))

    motor.run()

    resultado = motor.calcular_resultado(respostas)
    desempate = motor.resolver_empate_por_ferramenta(
        resultado, respostas
    )

    return motor, resultado, desempate


# Perfil com interesses em Ciencia de Dados e QA
respostas = {
    "P1": "alta",
    "P2": "H",
    "P3": "I",
    "P4": "J",
    "P5": "A",
    "P6": "F",
    "P7": "B",
    "P8": "F",
    "P9": "A",
    "P10": "F"
}


# TESTE 1 - Empate que exige pergunta adicional
motor, resultado, desempate = executar_perfil(respostas)

regras = {r["regra"] for r in resultado["regras_ativadas"]}

assert regras == {"R03", "R09"}
assert resultado["pontuacoes"]["ciencia_dados"] == 3
assert resultado["pontuacoes"]["qa"] == 3
assert set(desempate["candidatas"]) == {"ciencia_dados", "qa"}
assert desempate["precisa_pergunta_extra"] is True

pergunta = motor.gerar_pergunta_adicional(
    desempate["candidatas"]
)

escolha = motor.resolver_pergunta_adicional(pergunta, "qa")

assert escolha["carreira"] == "qa"

print("Teste 1 - Empate e pergunta adicional: APROVADO")


# TESTE 2 - Desempate pela ferramenta SQL
respostas_sql = {**respostas, "P3": "G"}

motor, resultado, desempate = executar_perfil(respostas_sql)

assert set(resultado["carreiras_empatadas"]) == {
    "ciencia_dados", "qa"
}
assert desempate["candidatas"] == ["ciencia_dados"]
assert desempate["criterio"] == "ferramenta"
assert desempate["precisa_pergunta_extra"] is False

print("Teste 2 - Desempate pela Pergunta 3: APROVADO")


# TESTE 3 - Preferencia da P4 resolve o empate
respostas_qa = {**respostas, "P4": "I"}

motor, resultado, desempate = executar_perfil(respostas_qa)

assert resultado["pontuacoes"]["ciencia_dados"] == 3
assert resultado["pontuacoes"]["qa"] == 4
assert desempate["candidatas"] == ["qa"]
assert desempate["precisa_pergunta_extra"] is False

print("Teste 3 - Preferencia da P4: APROVADO")

print("\nTODOS OS TESTES DE CONFLITO PASSARAM!")
