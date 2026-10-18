
import collections
import collections.abc

collections.Mapping = collections.abc.Mapping

from experta import Fact, KnowledgeEngine, Rule, MATCH, TEST, OR

class Resposta(Fact):
    pass


class MotorInferencia(KnowledgeEngine):

    def __init__(self):
        super().__init__()

        self.pontuacoes = {
            "backend": 0,
            "frontend": 0,
            "ciencia_dados": 0,
            "engenharia_dados": 0,
            "ciberseguranca": 0,
            "devops": 0,
            "nuvem": 0,
            "mobile": 0,
            "qa": 0,
            "gestao_produtos": 0
        }

        self.regras_ativadas = []

    def reset(self, **kwargs):
        super().reset(**kwargs)

        if hasattr(self, "pontuacoes"):
            self.pontuacoes = dict.fromkeys(self.pontuacoes, 0)
        if hasattr(self, "regras_ativadas"):
            self.regras_ativadas.clear()


    def registrar_regra(self, codigo, carreira, pontos, motivo):
        if any(
            registro["regra"] == codigo
            for registro in self.regras_ativadas
        ):
            return

        self.pontuacoes[carreira] += pontos

        self.regras_ativadas.append({
            "regra": codigo,
            "carreira": carreira,
            "pontos": pontos,
            "motivo": motivo
        })


    # R01 - Desenvolvimento Back-end
    @Rule(
        Resposta(pergunta="P2", valor="A"),
        Resposta(pergunta="P8", valor=MATCH.p8),
        TEST(lambda p8: p8 in ("A", "D", "E"))
    )
    def regra_01(self):
        self.registrar_regra(
            "R01",
            "backend",
            3,
            "Interesse em programacao e desenvolvimento de sistemas."
        )

    # R02 - Desenvolvimento Front-end e UI/UX
    @Rule(
        Resposta(pergunta="P2", valor="B"),
        Resposta(pergunta="P8", valor=MATCH.p8),
        TEST(lambda p8: p8 in ("B", "D"))
    )
    def regra_02(self):
        self.registrar_regra(
            "R02",
            "frontend",
            3,
            "Interesse em interfaces visuais e experiencia do usuario."
        )

    # R03 - Ciencia de Dados e Machine Learning
    @Rule(
        Resposta(pergunta="P1", valor=MATCH.p1),
        Resposta(pergunta="P7", valor="B"),
        TEST(lambda p1: p1 in ("media", "alta"))
    )
    def regra_03(self):
        self.registrar_regra(
            "R03",
            "ciencia_dados",
            3,
            "Afinidade com matematica e interesse em modelos de inteligencia artificial."
        )

    # R04 - Engenharia de Dados
    @Rule(
        Resposta(pergunta="P2", valor="D"),
        Resposta(pergunta="P7", valor=MATCH.p7),
        TEST(lambda p7: p7 in ("C", "D"))
    )
    def regra_04(self):
        self.registrar_regra(
            "R04",
            "engenharia_dados",
            3,
            "Interesse em processamento, organizacao e infraestrutura de dados."
        )

    # R05 - Ciberseguranca
    @Rule(
        Resposta(pergunta="P2", valor="E"),
        Resposta(pergunta="P6", valor="A")
    )
    def regra_05(self):
        self.registrar_regra(
            "R05",
            "ciberseguranca",
            3,
            "Interesse em investigar vulnerabilidades e proteger sistemas."
        )

    # R06 - DevOps e SRE
    @Rule(
        Resposta(pergunta="P2", valor="F"),
        Resposta(pergunta="P6", valor="B")
    )
    def regra_06(self):
        self.registrar_regra(
            "R06",
            "devops",
            3,
            "Interesse em infraestrutura e automacao de processos de implantacao."
        )

    # R07 - Computacao em Nuvem
    @Rule(
        Resposta(pergunta="P4", valor="G"),
        Resposta(pergunta="P6", valor="C")
    )
    def regra_07(self):
        self.registrar_regra(
            "R07",
            "nuvem",
            3,
            "Interesse em infraestruturas escalaveis e gerenciamento de ambientes em nuvem."
        )

    # R08 - Desenvolvimento Mobile
    @Rule(
        Resposta(pergunta="P2", valor="G"),
        Resposta(pergunta="P8", valor="C")
    )
    def regra_08(self):
        self.registrar_regra(
            "R08",
            "mobile",
            3,
            "Interesse em desenvolver aplicativos para celulares e dispositivos moveis."
        )

    # R09 - Engenharia de Qualidade e Testes
    @Rule(
        Resposta(pergunta="P2", valor="H"),
        Resposta(pergunta="P9", valor=MATCH.p9),
        TEST(lambda p9: p9 in ("A", "B", "C", "D", "E"))
    )
    def regra_09(self):
        self.registrar_regra(
            "R09",
            "qa",
            3,
            "Interesse em testes, investigacao de defeitos e qualidade de software."
        )

    # R10 - Gestao de Produtos
    @Rule(
        Resposta(pergunta="P2", valor="I"),
        Resposta(pergunta="P10", valor="F")
    )
    def regra_10(self):
        self.registrar_regra(
            "R10",
            "gestao_produtos",
            3,
            "Interesse em planejamento, priorizacao e estrategia de produtos digitais."
        )

    # R11 - Ciencia de Dados e Machine Learning
    @Rule(
        Resposta(pergunta="P7", valor="B"),
        OR(
            Resposta(pergunta="P5", valor="C"),
            Resposta(pergunta="P10", valor="C")
        )
    )
    def regra_11(self):
        self.registrar_regra(
            "R11",
            "ciencia_dados",
            2,
            "Interesse em modelos de inteligencia artificial e analise de dados."
        )

    # R12 - Engenharia de Dados
    @Rule(
        Resposta(pergunta="P4", valor="D"),
        Resposta(pergunta="P7", valor="D")
    )
    def regra_12(self):
        self.registrar_regra(
            "R12",
            "engenharia_dados",
            2,
            "Interesse em organizar, armazenar e disponibilizar grandes volumes de dados."
        )

    # R13 - Ciberseguranca
    @Rule(
        Resposta(pergunta="P6", valor="A"),
        OR(
            Resposta(pergunta="P5", valor="D"),
            Resposta(pergunta="P10", valor="E")
        )
    )
    def regra_13(self):
        self.registrar_regra(
            "R13",
            "ciberseguranca",
            2,
            "Interesse em investigar riscos, identificar vulnerabilidades e proteger sistemas."
        )

    # R14 - Engenharia de Qualidade e Testes
    @Rule(
        Resposta(pergunta="P4", valor="I"),
        Resposta(pergunta="P9", valor="D")
    )
    def regra_14(self):
        self.registrar_regra(
            "R14",
            "qa",
            2,
            "Interesse em qualidade de software e planejamento de cenarios de teste."
        )

    # R15 - DevOps e SRE
    @Rule(
        Resposta(pergunta="P4", valor="F"),
        Resposta(pergunta="P6", valor="E")
    )
    def regra_15(self):
        self.registrar_regra(
            "R15",
            "devops",
            2,
            "Interesse em estabilidade, monitoramento e confiabilidade de sistemas."
        )

    # R16 - Desenvolvimento Back-end
    @Rule(
        Resposta(pergunta="P4", valor="A"),
        OR(
            Resposta(pergunta="P5", valor="A"),
            Resposta(pergunta="P10", valor="A")
        )
    )
    def regra_16(self):
        self.registrar_regra(
            "R16",
            "backend",
            2,
            "Interesse em sistemas eficientes e especializacao em logica e programacao."
        )

    # R17 - Desenvolvimento Front-end e UI/UX
    @Rule(
        Resposta(pergunta="P4", valor="B"),
        OR(
            Resposta(pergunta="P5", valor="B"),
            Resposta(pergunta="P10", valor="B")
        )
    )
    def regra_17(self):
        self.registrar_regra(
            "R17",
            "frontend",
            2,
            "Interesse em interfaces intuitivas, solucoes visuais e experiencia do usuario."
        )

    # R18 - Computacao em Nuvem
    @Rule(
        Resposta(pergunta="P6", valor="C"),
        OR(
            Resposta(pergunta="P2", valor="F"),
            Resposta(pergunta="P10", valor="D")
        )
    )
    def regra_18(self):
        self.registrar_regra(
            "R18",
            "nuvem",
            2,
            "Interesse em infraestrutura e gerenciamento de ambientes de computacao em nuvem."
        )

    # R19 - Desenvolvimento Mobile
    @Rule(
        Resposta(pergunta="P4", valor="H"),
        Resposta(pergunta="P8", valor="C")
    )
    def regra_19(self):
        self.registrar_regra(
            "R19",
            "mobile",
            2,
            "Interesse em entregar aplicativos uteis e desenvolver solucoes para dispositivos moveis."
        )

    # R20 - Gestao de Produtos
    @Rule(
        Resposta(pergunta="P4", valor="J"),
        Resposta(pergunta="P5", valor="F")
    )
    def regra_20(self):
        self.registrar_regra(
            "R20",
            "gestao_produtos",
            2,
            "Interesse em produtos digitais, planejamento estrategico e definicao de prioridades."
        )

    # R21 - Ciencia de Dados e Machine Learning
    @Rule(
        Resposta(pergunta="P2", valor="C"),
        Resposta(pergunta="P7", valor=MATCH.p7),
        TEST(lambda p7: p7 in ("A", "E"))
    )
    def regra_21(self):
        self.registrar_regra(
            "R21",
            "ciencia_dados",
            2,
            "Interesse em analise e visualizacao de dados para apoiar decisoes."
        )

    # R22 - Engenharia de Dados
    @Rule(
        Resposta(pergunta="P4", valor="D"),
        Resposta(pergunta="P7", valor="C")
    )
    def regra_22(self):
        self.registrar_regra(
            "R22",
            "engenharia_dados",
            2,
            "Interesse em dados confiaveis e construcao de processos automatizados de dados."
        )

    # R23 - Engenharia de Qualidade e Testes
    @Rule(
        Resposta(pergunta="P4", valor="I"),
        OR(
            Resposta(pergunta="P5", valor="D"),
            Resposta(pergunta="P10", valor="E")
        )
    )
    def regra_23(self):
        self.registrar_regra(
            "R23",
            "qa",
            2,
            "Interesse em software confiavel, investigacao de falhas e melhoria da qualidade."
        )

    # R24 - Ciberseguranca
    @Rule(
        Resposta(pergunta="P4", valor="E"),
        Resposta(pergunta="P6", valor="A")
    )
    def regra_24(self):
        self.registrar_regra(
            "R24",
            "ciberseguranca",
            2,
            "Interesse em proteger sistemas e prevenir ataques e vulnerabilidades."
        )

    # R25 - DevOps e SRE
    @Rule(
        Resposta(pergunta="P5", valor="E"),
        Resposta(pergunta="P6", valor=MATCH.p6),
        TEST(lambda p6: p6 in ("B", "D"))
    )
    def regra_25(self):
        self.registrar_regra(
            "R25",
            "devops",
            2,
            "Interesse em automacao, otimizacao de processos e administracao de infraestrutura."
        )

    def calcular_resultado(self, respostas):

        mapa_p4 = {
            "A": "backend",
            "B": "frontend",
            "C": "ciencia_dados",
            "D": "engenharia_dados",
            "E": "ciberseguranca",
            "F": "devops",
            "G": "nuvem",
            "H": "mobile",
            "I": "qa",
            "J": "gestao_produtos"
        }

        resposta_p4 = respostas.get("P4")

        if resposta_p4 not in mapa_p4:
            raise ValueError("Resposta invalida ou ausente na Pergunta 4.")

        pontuacoes_finais = {
            carreira: min(pontos, 5)
            for carreira, pontos in self.pontuacoes.items()
        }

        carreira_p4 = mapa_p4[resposta_p4]
        pontuacoes_finais[carreira_p4] += 1

        maior_pontuacao = max(pontuacoes_finais.values())

        carreiras_empatadas = [
            carreira
            for carreira, pontos in pontuacoes_finais.items()
            if pontos == maior_pontuacao
        ]

        return {
            "pontuacoes": pontuacoes_finais,
            "maior_pontuacao": maior_pontuacao,
            "carreiras_empatadas": carreiras_empatadas,
            "carreira_p4": carreira_p4,
            "regras_ativadas": list(self.regras_ativadas)
        }

    def resolver_empate_por_ferramenta(self, resultado, respostas):

        empatadas = resultado["carreiras_empatadas"]

        if len(empatadas) <= 1:
            return {
                "candidatas": list(empatadas),
                "criterio": "pontuacao",
                "precisa_pergunta_extra": False
            }

        mapa_ferramentas = {
            "A": {"backend", "ciberseguranca"},
            "B": {"backend", "ciberseguranca"},
            "C": {"backend", "mobile"},
            "D": {
                "backend", "ciencia_dados",
                "engenharia_dados", "qa", "devops"
            },
            "E": {"frontend", "backend", "mobile"},
            "F": {"backend", "mobile"},
            "G": {"engenharia_dados", "backend", "ciencia_dados"},
            "H": {"ciberseguranca", "devops", "nuvem"},
            "I": set()
        }

        ferramenta = respostas.get("P3")
        carreiras_compativeis = mapa_ferramentas.get(
            ferramenta, set()
        )

        candidatas = [
            carreira
            for carreira in empatadas
            if carreira in carreiras_compativeis
        ]

        if len(candidatas) == 1:
            return {
                "candidatas": candidatas,
                "criterio": "ferramenta",
                "precisa_pergunta_extra": False
            }

        if len(candidatas) > 1:
            return {
                "candidatas": candidatas,
                "criterio": "pergunta_adicional",
                "precisa_pergunta_extra": True
            }

        return {
            "candidatas": list(empatadas),
            "criterio": "pergunta_adicional",
            "precisa_pergunta_extra": True
        }

    def gerar_pergunta_adicional(self, candidatas):

        atividades = {
            "backend": "Desenvolver a logica de sistemas, APIs e regras de negocio.",
            "frontend": "Criar interfaces e melhorar a experiencia dos usuarios.",
            "ciencia_dados": "Analisar dados e desenvolver modelos preditivos.",
            "engenharia_dados": "Construir pipelines e organizar grandes volumes de dados.",
            "ciberseguranca": "Investigar vulnerabilidades e proteger sistemas.",
            "devops": "Automatizar entregas e garantir a confiabilidade dos sistemas.",
            "nuvem": "Planejar e gerenciar infraestruturas em nuvem.",
            "mobile": "Desenvolver aplicativos para celulares e tablets.",
            "qa": "Testar sistemas, investigar erros e garantir a qualidade.",
            "gestao_produtos": "Definir prioridades e planejar produtos digitais."
        }

        if len(candidatas) < 2:
            raise ValueError("A pergunta adicional exige pelo menos duas carreiras.")

        if any(carreira not in atividades for carreira in candidatas):
            raise ValueError("Carreira desconhecida no desempate.")

        return {
            "enunciado": (
                "Entre as atividades abaixo, qual voce preferiria "
                "realizar no seu dia a dia profissional?"
            ),
            "opcoes": {
                carreira: atividades[carreira]
                for carreira in candidatas
            }
        }

    def resolver_pergunta_adicional(self, pergunta, escolha):

        if escolha not in pergunta["opcoes"]:
            raise ValueError("Alternativa invalida para o desempate.")

        return {
            "carreira": escolha,
            "criterio": "pergunta_adicional",
            "justificativa": (
                "O usuario demonstrou maior interesse em: "
                + pergunta["opcoes"][escolha]
            )
        }


if __name__ == "__main__":


    cenarios = [
        ("R01", "backend", {"P2": "A", "P8": "E"}),
        ("R02", "frontend", {"P2": "B", "P8": "B"}),

        ("R03", "ciencia_dados", {"P1": "media", "P7": "B"}),
        ("R03", "ciencia_dados", {"P1": "alta", "P7": "B"}),

        ("R04", "engenharia_dados", {"P2": "D", "P7": "C"}),
        ("R04", "engenharia_dados", {"P2": "D", "P7": "D"}),

        ("R05", "ciberseguranca", {"P2": "E", "P6": "A"}),
        ("R06", "devops", {"P2": "F", "P6": "B"}),
        ("R07", "nuvem", {"P4": "G", "P6": "C"}),
        ("R08", "mobile", {"P2": "G", "P8": "C"}),

        ("R09", "qa", {"P2": "H", "P9": "A"}),
        ("R09", "qa", {"P2": "H", "P9": "B"}),
        ("R09", "qa", {"P2": "H", "P9": "C"}),
        ("R09", "qa", {"P2": "H", "P9": "D"}),
        ("R09", "qa", {"P2": "H", "P9": "E"}),

        ("R10", "gestao_produtos", {"P2": "I", "P10": "F"}),

        ("R11", "ciencia_dados", {"P7": "B", "P5": "C"}),
        ("R11", "ciencia_dados", {"P7": "B", "P10": "C"}),
        ("R11", "ciencia_dados", {"P7": "B", "P5": "C", "P10": "C"}),

        ("R12", "engenharia_dados", {"P4": "D", "P7": "D"}),

        ("R13", "ciberseguranca", {"P6": "A", "P5": "D"}),
        ("R13", "ciberseguranca", {"P6": "A", "P10": "E"}),
        ("R13", "ciberseguranca", {"P6": "A", "P5": "D", "P10": "E"}),

        ("R14", "qa", {"P4": "I", "P9": "D"}),
        ("R15", "devops", {"P4": "F", "P6": "E"}),

        ("R16", "backend", {"P4": "A", "P5": "A"}),
        ("R16", "backend", {"P4": "A", "P10": "A"}),
        ("R16", "backend", {"P4": "A", "P5": "A", "P10": "A"}),

        ("R17", "frontend", {"P4": "B", "P5": "B"}),
        ("R17", "frontend", {"P4": "B", "P10": "B"}),
        ("R17", "frontend", {"P4": "B", "P5": "B", "P10": "B"}),

        ("R18", "nuvem", {"P6": "C", "P2": "F"}),
        ("R18", "nuvem", {"P6": "C", "P10": "D"}),
        ("R18", "nuvem", {"P6": "C", "P2": "F", "P10": "D"}),

        ("R19", "mobile", {"P4": "H", "P8": "C"}),
        ("R20", "gestao_produtos", {"P4": "J", "P5": "F"}),

        ("R21", "ciencia_dados", {"P2": "C", "P7": "A"}),
        ("R21", "ciencia_dados", {"P2": "C", "P7": "E"}),

        ("R22", "engenharia_dados", {"P4": "D", "P7": "C"}),

        ("R23", "qa", {"P4": "I", "P5": "D"}),
        ("R23", "qa", {"P4": "I", "P10": "E"}),
        ("R23", "qa", {"P4": "I", "P5": "D", "P10": "E"}),

        ("R24", "ciberseguranca", {"P4": "E", "P6": "A"}),

        ("R25", "devops", {"P5": "E", "P6": "B"}),
        ("R25", "devops", {"P5": "E", "P6": "D"})

    ]

    for regra_esperada, carreira, respostas in cenarios:
        motor = MotorInferencia()
        motor.reset()

        for pergunta, valor in respostas.items():
            motor.declare(Resposta(pergunta=pergunta, valor=valor))

        motor.run()

        regras = [r["regra"] for r in motor.regras_ativadas]
        pontos = motor.pontuacoes[carreira]

        print(f"{regra_esperada}: {regras} - {pontos} pontos")

        assert regras == [regra_esperada]

        assert pontos == (3 if int(regra_esperada[1:]) <= 10 else 2)
    print("45 cenarios de regras aprovados!")


    respostas_qa = {
        "P2": "H",
        "P4": "I",
        "P5": "D",
        "P9": "A",
        "P10": "E"
    }

    motor = MotorInferencia()
    motor.reset()

    for pergunta, valor in respostas_qa.items():
        motor.declare(Resposta(pergunta=pergunta, valor=valor))

    motor.run()
    resultado = motor.calcular_resultado(respostas_qa)

    assert resultado["pontuacoes"]["qa"] == 6
    assert resultado["carreiras_empatadas"] == ["qa"]
    print("Teste pontuacao QA: aprovado")


    # Teste de limite de pontuacao - Ciberseguranca
    respostas_seguranca = {
        "P2": "E",
        "P4": "E",
        "P5": "D",
        "P6": "A"
    }

    motor = MotorInferencia()
    motor.reset()

    for pergunta, valor in respostas_seguranca.items():
        motor.declare(Resposta(pergunta=pergunta, valor=valor))

    motor.run()
    resultado = motor.calcular_resultado(respostas_seguranca)

    assert motor.pontuacoes["ciberseguranca"] == 7
    assert resultado["pontuacoes"]["ciberseguranca"] == 6
    print("Teste limite de pontuacao: aprovado")


    # Teste sem ativacao de regras cruzadas
    respostas_basicas = {
        "P4": "B"
    }

    motor = MotorInferencia()
    motor.reset()

    motor.declare(Resposta(pergunta="P4", valor="B"))
    motor.run()

    resultado = motor.calcular_resultado(respostas_basicas)

    assert resultado["regras_ativadas"] == []
    assert resultado["pontuacoes"]["frontend"] == 1
    assert resultado["carreiras_empatadas"] == ["frontend"]
    print("Teste recomendacao basica: aprovado")

    # Testes dos criterios de desempate
    cenarios_desempate = [
        (
            ["ciencia_dados", "nuvem"],
            "D",
            ["ciencia_dados"],
            False
        ),
        (
            ["backend", "ciencia_dados"],
            "D",
            ["backend", "ciencia_dados"],
            True
        ),
        (
            ["qa", "ciberseguranca"],
            "I",
            ["qa", "ciberseguranca"],
            True
        ),
        (
            ["qa", "ciberseguranca"],
            "H",
            ["ciberseguranca"],
            False
        ),
        (
            ["backend"],
            "I",
            ["backend"],
            False
        )
    ]

    motor = MotorInferencia()

    for empatadas, p3, esperadas, pergunta_extra in cenarios_desempate:

        resultado_simulado = {
            "carreiras_empatadas": empatadas
        }

        desempate = motor.resolver_empate_por_ferramenta(
            resultado_simulado,
            {"P3": p3}
        )

        assert desempate["candidatas"] == esperadas
        assert desempate["precisa_pergunta_extra"] == pergunta_extra

        print(
            f"Desempate P3={p3}: "
            f"{desempate['candidatas']} "
            f"- Pergunta extra: {pergunta_extra}"
        )

    print("Testes de desempate concluidos com sucesso!")


    # Teste da pergunta adicional
    motor = MotorInferencia()

    pergunta = motor.gerar_pergunta_adicional(
        ["backend", "ciencia_dados"]
    )

    assert len(pergunta["opcoes"]) == 2
    assert "backend" in pergunta["opcoes"]
    assert "ciencia_dados" in pergunta["opcoes"]

    resultado_extra = motor.resolver_pergunta_adicional(
        pergunta, "ciencia_dados"
    )

    assert resultado_extra["carreira"] == "ciencia_dados"
    assert resultado_extra["criterio"] == "pergunta_adicional"

    print("Teste da pergunta adicional: aprovado")

    # Teste com tres carreiras empatadas
    pergunta = motor.gerar_pergunta_adicional(
        ["backend", "frontend", "mobile"]
    )

    assert len(pergunta["opcoes"]) == 3

    print("Teste com tres carreiras empatadas: aprovado")

    # Verifica se uma escolha invalida e rejeitada
    try:
        motor.resolver_pergunta_adicional(pergunta, "qa")
    except ValueError:
        print("Teste de alternativa invalida: aprovado")
    else:
        raise AssertionError("Uma alternativa invalida foi aceita.")

    # Testa duas entrevistas sucessivas no mesmo objeto
    motor_reutilizado = MotorInferencia()
    motor_reutilizado.reset()
    motor_reutilizado.declare(Resposta(pergunta="P2", valor="A"))
    motor_reutilizado.declare(Resposta(pergunta="P8", valor="A"))
    motor_reutilizado.run()
    assert {r["regra"] for r in motor_reutilizado.regras_ativadas} == {"R01"}

    motor_reutilizado.reset()
    assert all(pontos == 0 for pontos in motor_reutilizado.pontuacoes.values())
    assert motor_reutilizado.regras_ativadas == []

    motor_reutilizado.declare(Resposta(pergunta="P2", valor="B"))
    motor_reutilizado.declare(Resposta(pergunta="P8", valor="B"))
    motor_reutilizado.run()

    assert {r["regra"] for r in motor_reutilizado.regras_ativadas} == {"R02"}
    assert motor_reutilizado.pontuacoes["backend"] == 0
    assert motor_reutilizado.pontuacoes["frontend"] == 3
    print("Teste de reutilizacao do motor: aprovado")
