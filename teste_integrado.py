
from motor_inferencia import MotorInferencia, Resposta
from perguntas import PERGUNTAS

respostas = {
    "P1": "baixa",
    "P2": "H",
    "P3": "D",
    "P4": "I",
    "P5": "D",
    "P6": "F",
    "P7": "F",
    "P8": "F",
    "P9": "A",
    "P10": "E"
}

assert set(respostas) == set(PERGUNTAS)

for pergunta, valor in respostas.items():
    assert valor in PERGUNTAS[pergunta]["opcoes"]

motor = MotorInferencia()
motor.reset()

for pergunta, valor in respostas.items():
    motor.declare(
        Resposta(pergunta=pergunta, valor=valor)
    )

motor.run()

resultado = motor.calcular_resultado(respostas)

desempate = motor.resolver_empate_por_ferramenta(
    resultado, respostas
)

print("\n=== TESTE INTEGRADO ===")

print("\nRegras ativadas:")
for regra in resultado["regras_ativadas"]:
    print(regra["regra"], "-", regra["motivo"])

print("\nPontuacao final:")
for carreira, pontos in resultado["pontuacoes"].items():
    if pontos > 0:
        print(carreira, ":", pontos)

print("\nCarreira recomendada:")
print(desempate["candidatas"])

regras = {
    regra["regra"]
    for regra in resultado["regras_ativadas"]
}

assert regras == {"R09", "R23"}
assert resultado["pontuacoes"]["qa"] == 6
assert desempate["candidatas"] == ["qa"]
assert desempate["precisa_pergunta_extra"] is False

print("\nTESTE INTEGRADO APROVADO!")

personas = [
    {
        "nome": "Perfil Analitico",
        "esperada": "ciencia_dados",
        "respostas": {
            "P1": "alta",
            "P2": "C",
            "P3": "D",
            "P4": "C",
            "P5": "C",
            "P6": "F",
            "P7": "B",
            "P8": "F",
            "P9": "F",
            "P10": "C"
        }
    },
    {
        "nome": "Perfil Seguranca",
        "esperada": "ciberseguranca",
        "respostas": {
            "P1": "baixa",
            "P2": "E",
            "P3": "H",
            "P4": "E",
            "P5": "D",
            "P6": "A",
            "P7": "F",
            "P8": "F",
            "P9": "F",
            "P10": "E"
        }
    },
    {
        "nome": "Perfil Visual e Front-end",
        "esperada": "frontend",
        "respostas": {
            "P1": "baixa",
            "P2": "B",
            "P3": "E",
            "P4": "B",
            "P5": "B",
            "P6": "F",
            "P7": "F",
            "P8": "B",
            "P9": "F",
            "P10": "B"
        }
    },
    {
        "nome": "Perfil Negocios e Produto",
        "esperada": "gestao_produtos",
        "respostas": {
            "P1": "baixa",
            "P2": "I",
            "P3": "I",
            "P4": "J",
            "P5": "F",
            "P6": "F",
            "P7": "F",
            "P8": "F",
            "P9": "F",
            "P10": "F"
        }
    }
]

personas.extend([
    {
        "nome": "Perfil Desenvolvimento Back-end",
        "esperada": "backend",
        "respostas": {
            "P1": "media",
            "P2": "A",
            "P3": "F",
            "P4": "A",
            "P5": "A",
            "P6": "F",
            "P7": "F",
            "P8": "A",
            "P9": "F",
            "P10": "A"
        }
    },
    {
        "nome": "Perfil Engenharia de Dados",
        "esperada": "engenharia_dados",
        "respostas": {
            "P1": "media",
            "P2": "D",
            "P3": "G",
            "P4": "D",
            "P5": "E",
            "P6": "F",
            "P7": "C",
            "P8": "F",
            "P9": "F",
            "P10": "D"
        }
    },
    {
        "nome": "Perfil DevOps e SRE",
        "esperada": "devops",
        "respostas": {
            "P1": "media",
            "P2": "F",
            "P3": "H",
            "P4": "F",
            "P5": "E",
            "P6": "B",
            "P7": "F",
            "P8": "F",
            "P9": "F",
            "P10": "D"
        }
    },
    {
        "nome": "Perfil Computacao em Nuvem",
        "esperada": "nuvem",
        "respostas": {
            "P1": "baixa",
            "P2": "F",
            "P3": "H",
            "P4": "G",
            "P5": "E",
            "P6": "C",
            "P7": "F",
            "P8": "F",
            "P9": "F",
            "P10": "D"
        }
    },
    {
        "nome": "Perfil Desenvolvimento Mobile",
        "esperada": "mobile",
        "respostas": {
            "P1": "baixa",
            "P2": "G",
            "P3": "C",
            "P4": "H",
            "P5": "A",
            "P6": "F",
            "P7": "F",
            "P8": "C",
            "P9": "F",
            "P10": "A"
        }
    }
])

print(f"Total de personas cadastradas: {len(personas)}")
assert len(personas) == 9, "As cinco novas personas nao foram cadastradas corretamente."

print("\n=== VALIDACAO COM PERSONAS ===")

for persona in personas:
    respostas = persona["respostas"]

    assert set(respostas) == set(PERGUNTAS)

    for pergunta, valor in respostas.items():
        assert valor in PERGUNTAS[pergunta]["opcoes"]

    motor = MotorInferencia()
    motor.reset()

    for pergunta, valor in respostas.items():
        motor.declare(
            Resposta(pergunta=pergunta, valor=valor)
        )

    motor.run()

    resultado = motor.calcular_resultado(respostas)

    desempate = motor.resolver_empate_por_ferramenta(
        resultado, respostas
    )

    carreira = persona["esperada"]

    regras = [
        registro["regra"]
        for registro in resultado["regras_ativadas"]
    ]

    print(f"\nPersona: {persona['nome']}")
    print(f"Regras ativadas: {sorted(regras)}")
    print(f"Pontuacao: {resultado['pontuacoes'][carreira]}")
    print(f"Recomendacao: {desempate['candidatas']}")

    assert resultado["pontuacoes"][carreira] == 6
    assert desempate["candidatas"] == [carreira]
    assert desempate["precisa_pergunta_extra"] is False

    print("Resultado: APROVADO")


print("\nTODAS AS PERSONAS FORAM VALIDADAS!")
