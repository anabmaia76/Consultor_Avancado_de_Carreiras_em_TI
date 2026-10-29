r"""Testes automatizados — Consultor Avançado de Carreiras em TI.

Execute a partir da pasta principal do projeto:
    .\.venv\Scripts\python.exe teste.py
"""

import copy
import json
import tempfile
import unittest
from pathlib import Path

import motor_ponderado as motor


class TestesConsultorCarreiras(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = motor.carregar_base_conhecimento()
        cls.carreiras = cls.base["carreiras"]
        cls.afinidades = cls.base["dimensoes_afinidade"]
        cls.objetivos = cls.base["objetivos_profissionais"]

    @classmethod
    def perfil(cls, carreira_codigo, afinidades_fortes=None, objetivos_fortes=None):
        carreira = cls.carreiras[carreira_codigo]
        afinidades_fortes = (
            set(carreira["pesos_afinidade"])
            if afinidades_fortes is None else set(afinidades_fortes)
        )
        objetivos_fortes = (
            set(carreira["pesos_objetivos"])
            if objetivos_fortes is None else set(objetivos_fortes)
        )
        afinidades = {k: (5 if k in afinidades_fortes else 1) for k in cls.afinidades}
        objetivos = {k: (5 if k in objetivos_fortes else 1) for k in cls.objetivos}
        return afinidades, objetivos

    @classmethod
    def niveis(cls, carreira_codigo, valor=None, referencia=False):
        return {
            c["codigo"]: (c["nivel_junior"] if referencia else valor)
            for c in cls.carreiras[carreira_codigo]["competencias"]
        }

    def test_01_base_v030_com_10_carreiras_e_50_competencias(self):
        self.assertEqual(self.base["versao_modelo"], "0.3.0")
        self.assertEqual(len(self.afinidades), 13)
        self.assertEqual(len(self.objetivos), 8)
        self.assertEqual(len(self.base["restricoes_atividades"]), 8)
        self.assertEqual(len(self.carreiras), 10)
        self.assertEqual(len(self.base["penalidades_logicas"]), 23)
        self.assertEqual(len(self.base["verificacao_contradicoes"]["comparacoes_restricao_afinidade"]), 8)
        self.assertEqual(sum(len(c["competencias"]) for c in self.carreiras.values()), 50)
        for codigo, carreira in self.carreiras.items():
            with self.subTest(carreira=codigo):
                self.assertEqual(len(carreira["competencias"]), 5)
                self.assertTrue(carreira["pesos_afinidade"])
                self.assertTrue(carreira["pesos_objetivos"])
                self.assertTrue(carreira["projeto_portfolio"]["titulo"])

    def test_02_leitura_do_json_em_caminho_explicitamente_informado(self):
        arquivo = Path(__file__).resolve().parent / "regras_carreiras.json"
        carregada = motor.carregar_base_conhecimento(arquivo)
        self.assertEqual(carregada, self.base)

    def test_03_json_inexistente_gera_erro_claro(self):
        with tempfile.TemporaryDirectory() as pasta:
            with self.assertRaises(FileNotFoundError):
                motor.carregar_base_conhecimento(Path(pasta) / "nao_existe.json")

    def test_04_json_invalido_gera_erro_claro(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "invalido.json"
            arquivo.write_text('{"carreiras": ', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON inválido"):
                motor.carregar_base_conhecimento(arquivo)

    def test_05_validador_rejeita_secao_ausente(self):
        alterada = copy.deepcopy(self.base)
        del alterada["carreiras"]
        with self.assertRaisesRegex(ValueError, "carreiras"):
            motor.validar_base_conhecimento(alterada)

    def test_06_validador_rejeita_referencia_de_peso_inexistente(self):
        alterada = copy.deepcopy(self.base)
        alterada["carreiras"]["backend"]["pesos_afinidade"]["D99"] = 1
        with self.assertRaises(ValueError):
            motor.validar_base_conhecimento(alterada)

    def test_07_validador_rejeita_participacoes_que_nao_somam_um(self):
        alterada = copy.deepcopy(self.base)
        alterada["parametros_calculo"]["participacao_afinidades"] = 0.9
        with self.assertRaises(ValueError):
            motor.validar_base_conhecimento(alterada)

    def test_08_validador_rejeita_penalidade_duplicada(self):
        alterada = copy.deepcopy(self.base)
        alterada["penalidades_logicas"].append(copy.deepcopy(alterada["penalidades_logicas"][0]))
        with self.assertRaisesRegex(ValueError, "duplicada"):
            motor.validar_base_conhecimento(alterada)

    def test_09_afinidades_extremos_0_e_100_para_todas_as_carreiras(self):
        for carreira in self.carreiras:
            with self.subTest(carreira=carreira):
                minimo = motor.calcular_afinidade_ponderada(
                    self.base, carreira, {k: 1 for k in self.afinidades}
                )
                maximo = motor.calcular_afinidade_ponderada(
                    self.base, carreira, {k: 5 for k in self.afinidades}
                )
                self.assertEqual(minimo["afinidade_percentual"], 0.0)
                self.assertEqual(maximo["afinidade_percentual"], 100.0)
                self.assertEqual(minimo["cobertura_percentual"], 100.0)
                self.assertEqual(maximo["status"], "calculada")

    def test_10_objetivos_extremos_0_e_100_para_todas_as_carreiras(self):
        for carreira in self.carreiras:
            with self.subTest(carreira=carreira):
                minimo = motor.calcular_objetivos_ponderados(
                    self.base, carreira, {k: 1 for k in self.objetivos}
                )
                maximo = motor.calcular_objetivos_ponderados(
                    self.base, carreira, {k: 5 for k in self.objetivos}
                )
                self.assertEqual(minimo["objetivos_percentual"], 0.0)
                self.assertEqual(maximo["objetivos_percentual"], 100.0)
                self.assertEqual(maximo["cobertura_percentual"], 100.0)

    def test_11_exemplo_aprovado_de_afinidade_backend(self):
        notas = {"D01": 5, "D02": 5, "D06": 4, "D12": 3, "D09": 2}
        r = motor.calcular_afinidade_ponderada(self.base, "backend", notas)
        self.assertEqual(r["afinidade_percentual"], 80.88)
        self.assertEqual(r["cobertura_percentual"], 100.0)

    def test_12_exemplo_aprovado_de_objetivos_backend(self):
        r = motor.calcular_objetivos_ponderados(self.base, "backend", {"O01": 5, "O04": 3})
        self.assertEqual(r["objetivos_percentual"], 85.71)

    def test_13_combinacao_80_porcento_afinidades_e_20_objetivos(self):
        a = {"D01": 5, "D02": 5, "D06": 4, "D12": 3, "D09": 2}
        r = motor.calcular_compatibilidade_inicial(self.base, "backend", a, {"O01": 5, "O04": 3})
        self.assertEqual(r["compatibilidade_inicial_percentual"], 81.85)
        self.assertEqual(r["status"], "calculada")
        self.assertFalse(r["penalidades_aplicadas"])

    def test_14_afinidade_com_cobertura_abaixo_de_70_porcento(self):
        r = motor.calcular_afinidade_ponderada(self.base, "backend", {"D01": 5, "D02": 5, "D06": None})
        self.assertEqual(r["status"], "dados_insuficientes")
        self.assertEqual(r["cobertura_percentual"], 58.82)
        self.assertIsNone(r["afinidade_percentual"])

    def test_15_afinidade_com_cobertura_suficiente_e_respostas_parciais(self):
        r = motor.calcular_afinidade_ponderada(self.base, "backend", {"D01": 5, "D02": 1, "D06": 3})
        self.assertEqual(r["status"], "calculada")
        self.assertEqual(r["cobertura_percentual"], 76.47)
        self.assertEqual(r["afinidade_percentual"], 50.0)

    def test_16_objetivos_com_cobertura_insuficiente(self):
        r = motor.calcular_objetivos_ponderados(self.base, "backend", {"O04": 5})
        self.assertEqual(r["cobertura_percentual"], 28.57)
        self.assertIsNone(r["objetivos_percentual"])

    def test_17_objetivos_com_cobertura_suficiente(self):
        r = motor.calcular_objetivos_ponderados(self.base, "backend", {"O01": 5})
        self.assertEqual(r["cobertura_percentual"], 71.43)
        self.assertEqual(r["objetivos_percentual"], 100.0)

    def test_18_resposta_desconhecida_nao_equivale_ao_minimo(self):
        r = motor.calcular_afinidade_ponderada(
            self.base, "backend", {"D01": 5, "D02": 5, "D06": None, "D12": 5, "D09": 5}
        )
        self.assertEqual(r["afinidade_percentual"], 100.0)
        self.assertLess(r["cobertura_percentual"], 100.0)
        minimo = motor.calcular_afinidade_ponderada(
            self.base, "backend", {"D01": 5, "D02": 5, "D06": 1, "D12": 5, "D09": 5}
        )
        self.assertLess(minimo["afinidade_percentual"], 100.0)
        self.assertEqual(minimo["cobertura_percentual"], 100.0)

    def test_19_valores_invalidos_sao_rejeitados(self):
        for nota in (-1, 0, 6, 3.5, True, "5"):
            with self.subTest(tipo="afinidade", valor=nota):
                with self.assertRaises(ValueError):
                    motor.calcular_afinidade_ponderada(self.base, "backend", {"D01": nota})
            with self.subTest(tipo="objetivo", valor=nota):
                with self.assertRaises(ValueError):
                    motor.calcular_objetivos_ponderados(self.base, "backend", {"O01": nota})
        with self.assertRaises(ValueError):
            motor.calcular_afinidade_ponderada(self.base, "backend", {"D99": 5})
        with self.assertRaises(ValueError):
            motor.calcular_objetivos_ponderados(self.base, "backend", {"O99": 5})
        with self.assertRaises(ValueError):
            motor.calcular_afinidade_ponderada(self.base, "carreira_inexistente", {})

    def test_20_as_23_regras_de_penalidade_individualmente(self):
        for regra in self.base["penalidades_logicas"]:
            with self.subTest(carreira=regra["carreira"], restricao=regra["restricao"]):
                r = motor.calcular_penalidades(self.base, regra["carreira"], [regra["restricao"]])
                self.assertEqual(r["total_bruto_pontos_percentuais"], regra["pontos_percentuais"])
                self.assertEqual(r["total_aplicado_pontos_percentuais"], regra["pontos_percentuais"])
                self.assertEqual(len(r["regras_ativadas"]), 1)
                self.assertEqual(r["regras_ativadas"][0]["tipo"], regra["tipo"])

    def test_21_limite_de_penalidades_de_16_pontos(self):
        r = motor.calcular_penalidades(self.base, "devops", ["RSTR01", "RSTR04", "RSTR07"])
        self.assertEqual(r["total_bruto_pontos_percentuais"], 20)
        self.assertEqual(r["total_aplicado_pontos_percentuais"], 16)
        self.assertEqual(r["reducao_pelo_limite"], 4)

    def test_22_restricao_duplicada_nao_desconta_duas_vezes(self):
        r = motor.calcular_penalidades(self.base, "backend", ["RSTR01", "RSTR01"])
        self.assertEqual(r["total_aplicado_pontos_percentuais"], 8)
        self.assertEqual(len(r["regras_ativadas"]), 1)

    def test_23_restricoes_invalidas_sao_rejeitadas(self):
        with self.assertRaises(ValueError):
            motor.calcular_penalidades(self.base, "backend", ["RSTR99"])
        with self.assertRaises(TypeError):
            motor.calcular_penalidades(self.base, "backend", "RSTR01")

    def test_24_contradicoes_8_comparacoes_limiar_4_e_resposta_null(self):
        mapa = self.base["verificacao_contradicoes"]["comparacoes_restricao_afinidade"]
        for restricao, dimensao in mapa.items():
            for nota, deve_avisar in ((3, False), (4, True), (5, True), (None, False)):
                with self.subTest(restricao=restricao, nota=nota):
                    respostas = {k: 1 for k in self.afinidades}
                    respostas[dimensao] = nota
                    avisos = motor.detectar_contradicoes(self.base, respostas, [restricao])
                    self.assertEqual(bool(avisos), deve_avisar)
                    if deve_avisar:
                        self.assertEqual(avisos[0]["restricao"], restricao)

    def test_25_contradicao_pendente_bloqueia_comp_final(self):
        a = {k: 5 for k in self.afinidades}
        o = {k: 5 for k in self.objetivos}
        r = motor.calcular_compatibilidade_final(self.base, "backend", a, o, ["RSTR01"])
        self.assertEqual(r["status"], "revisao_pendente")
        self.assertTrue(r["confirmacao_pendente"])
        self.assertIsNone(r["compatibilidade_final_percentual"])

    def test_26_confirmar_contradicao_preserva_restricao_e_aplica_penalidade(self):
        a = {"D01": 5, "D02": 5, "D06": 4, "D12": 3, "D09": 2}
        o = {"O01": 5, "O04": 3}
        r = motor.calcular_compatibilidade_final(
            self.base, "backend", a, o, ["RSTR01"], contradicoes_confirmadas=True
        )
        self.assertEqual(r["compatibilidade_inicial_percentual"], 81.85)
        self.assertEqual(r["penalidades"]["total_aplicado_pontos_percentuais"], 8)
        self.assertEqual(r["compatibilidade_final_percentual"], 73.85)
        self.assertEqual(r["status"], "calculada")

    def test_27_contradicao_sem_penalidade_para_carreira_nao_relacionada(self):
        a = {k: 1 for k in self.afinidades}
        a["D07"] = 5
        o = {k: 3 for k in self.objetivos}
        r = motor.calcular_compatibilidade_final(
            self.base, "gestao_produtos", a, o, ["RSTR05"], contradicoes_confirmadas=True
        )
        self.assertEqual(len(r["contradicoes"]), 1)
        self.assertEqual(r["penalidades"]["total_aplicado_pontos_percentuais"], 0)
        self.assertEqual(r["compatibilidade_final_percentual"], r["compatibilidade_inicial_percentual"])

    def test_28_compatibilidade_nao_fica_negativa(self):
        a = {k: 1 for k in self.afinidades}
        o = {k: 1 for k in self.objetivos}
        r = motor.calcular_compatibilidade_final(
            self.base, "backend", a, o, ["RSTR01"], contradicoes_confirmadas=True
        )
        self.assertEqual(r["compatibilidade_final_percentual"], 0.0)


    def test_29_ranking_exemplo_desenvolvimento_aprovado(self):
        a = {k: 2 for k in self.afinidades}
        a.update({"D01": 5, "D02": 5, "D06": 4, "D09": 3, "D12": 3})
        o = {k: 2 for k in self.objetivos}
        o.update({"O01": 5, "O04": 4})
        r = motor.gerar_ranking_top3(self.base, a, o)
        self.assertEqual(r["status"], "calculada")
        self.assertEqual(r["carreiras_elegiveis"], 10)
        self.assertEqual(
            [(c["codigo_carreira"], c["compatibilidade_final_percentual"]) for c in r["top_3"]],
            [("backend", 85.63), ("engenharia_dados", 60.53), ("frontend", 58.96)],
        )

    def test_30_dez_perfis_especificos_recomendam_a_carreira_correta(self):
        especiais = {
            "engenharia_dados": ({"D06", "D01", "D09"}, {"O03", "O04"}),
            "mobile": ({"D11", "D01", "D12"}, {"O08", "O01"}),
        }
        for codigo in self.carreiras:
            with self.subTest(perfil=codigo):
                a, o = self.perfil(codigo, *especiais.get(codigo, (None, None)))
                ranking = motor.gerar_ranking_top3(self.base, a, o)
                self.assertEqual(ranking["status"], "calculada")
                self.assertEqual(ranking["top_3"][0]["codigo_carreira"], codigo)
                self.assertEqual(len(ranking["top_3"]), 3)
                self.assertEqual(len(ranking["classificacao_completa"]), 10)

    def test_31_top3_bloqueado_quando_nao_ha_cobertura(self):
        r = motor.gerar_ranking_top3(self.base, {"D01": 5}, {"O01": 5})
        self.assertEqual(r["status"], "dados_insuficientes")
        self.assertEqual(r["top_3"], [])
        self.assertEqual(r["carreiras_elegiveis"], 0)

    def test_31a_top3_bloqueado_com_apenas_duas_carreiras_elegiveis(self):
        a = {k: 3 for k in self.afinidades}
        r = motor.gerar_ranking_top3(self.base, a, {"O04": 5, "O05": 5})
        self.assertEqual(r["status"], "dados_insuficientes")
        self.assertEqual(r["carreiras_elegiveis"], 2)
        self.assertEqual(r["top_3"], [])

    def test_31b_top3_com_cobertura_parcial_para_quatro_carreiras(self):
        a = {k: 3 for k in self.afinidades}
        r = motor.gerar_ranking_top3(self.base, a, {"O04": 5, "O05": 5, "O06": 5})
        self.assertEqual(r["status"], "calculada")
        self.assertEqual(r["carreiras_elegiveis"], 4)
        self.assertEqual(len(r["top_3"]), 3)
        self.assertEqual(len(r["carreiras_com_dados_insuficientes"]), 6)

    def test_32_top3_bloqueado_por_contradicao_nao_confirmada(self):
        a = {k: 5 for k in self.afinidades}
        o = {k: 5 for k in self.objetivos}
        r = motor.gerar_ranking_top3(self.base, a, o, ["RSTR01"])
        self.assertEqual(r["status"], "revisao_pendente")
        self.assertEqual(r["top_3"], [])
        self.assertGreaterEqual(len(r["contradicoes"]), 1)
        confirmado = motor.gerar_ranking_top3(
            self.base, a, o, ["RSTR01"], contradicoes_confirmadas=True
        )
        self.assertEqual(confirmado["status"], "calculada")
        self.assertEqual(len(confirmado["top_3"]), 3)

    def test_33_empate_de_todas_as_carreiras_segue_ordem_deterministica(self):
        a = {k: 3 for k in self.afinidades}
        o = {k: 3 for k in self.objetivos}
        r = motor.gerar_ranking_top3(self.base, a, o)
        nomes = [c["carreira"] for c in r["classificacao_completa"]]
        self.assertEqual(nomes, sorted(nomes, key=str.casefold))
        self.assertTrue(all(c["compatibilidade_final_percentual"] == 50 for c in r["classificacao_completa"]))
        self.assertEqual(len(r["empates_no_corte"]), 7)
        self.assertEqual(r["top_3"], r["classificacao_completa"][:3])
        self.assertEqual(r["classificacao_completa"], motor.gerar_ranking_top3(self.base, a, o)["classificacao_completa"])

    def test_34_cinco_competencias_em_dez_carreiras_sem_conhecimento(self):
        for codigo, carreira in self.carreiras.items():
            with self.subTest(carreira=codigo):
                r = motor.avaliar_lacunas_competencias(self.base, codigo, self.niveis(codigo, 0))
                self.assertEqual(r["status"], "avaliacao_completa")
                self.assertEqual(r["total_competencias"], 5)
                self.assertEqual(r["competencias_com_lacuna"], 5)
                self.assertEqual(r["total_niveis_de_lacuna"], sum(c["nivel_junior"] for c in carreira["competencias"]))
                self.assertFalse(r["altera_ranking_top3"])

    def test_35_competencias_ja_atendidas_em_todas_as_carreiras(self):
        for codigo in self.carreiras:
            with self.subTest(carreira=codigo):
                r = motor.avaliar_lacunas_competencias(self.base, codigo, self.niveis(codigo, referencia=True))
                self.assertEqual(r["competencias_atendidas"], 5)
                self.assertEqual(r["competencias_com_lacuna"], 0)
                self.assertEqual(r["total_niveis_de_lacuna"], 0)

    def test_36_nivel_tres_nao_gera_lacuna_em_nenhuma_carreira(self):
        for codigo in self.carreiras:
            with self.subTest(carreira=codigo):
                r = motor.avaliar_lacunas_competencias(self.base, codigo, self.niveis(codigo, 3))
                self.assertEqual(r["total_niveis_de_lacuna"], 0)

    def test_37_qa_duas_lacunas_confirmadas(self):
        niveis = {"QA_01": 2, "QA_02": 2, "QA_03": 3, "QA_04": 0, "QA_05": 0}
        r = motor.avaliar_lacunas_competencias(self.base, "qa", niveis)
        self.assertEqual(r["competencias_com_lacuna"], 2)
        self.assertEqual(r["total_niveis_de_lacuna"], 2)
        self.assertEqual([d["lacuna"] for d in r["detalhes"]], [0, 0, 0, 1, 1])

    def test_38_conhecimento_none_nao_vira_zero_nas_dez_carreiras(self):
        for codigo in self.carreiras:
            with self.subTest(carreira=codigo):
                niveis = self.niveis(codigo, referencia=True)
                primeira = next(iter(niveis))
                niveis[primeira] = None
                r = motor.avaliar_lacunas_competencias(self.base, codigo, niveis)
                self.assertEqual(r["status"], "avaliacao_incompleta")
                self.assertEqual(r["competencias_pendentes"], [primeira])
                self.assertIsNone(r["total_niveis_de_lacuna"])
                self.assertIsNone(next(x for x in r["detalhes"] if x["codigo"] == primeira)["lacuna"])

    def test_39_niveis_tecnicos_invalidos_sao_rejeitados(self):
        for nivel in (-1, 4, 1.5, True, "2"):
            with self.subTest(nivel=nivel):
                with self.assertRaises(ValueError):
                    motor.avaliar_lacunas_competencias(self.base, "qa", {"QA_01": nivel})
        with self.assertRaises(ValueError):
            motor.avaliar_lacunas_competencias(self.base, "qa", {"CODIGO_INEXISTENTE": 1})

    def test_40_roadmaps_com_lacunas_para_todas_as_dez_carreiras(self):
        for codigo, carreira in self.carreiras.items():
            with self.subTest(carreira=codigo):
                r = motor.gerar_roadmap_personalizado(self.base, codigo, self.niveis(codigo, 0))
                self.assertEqual(r["status"], "roadmap_gerado")
                self.assertEqual(r["competencias_com_lacuna"], 5)
                self.assertEqual(len(r["etapas"]), 4)
                self.assertEqual([len(e["itens"]) for e in r["etapas"]], [5, 5, 1, 1])
                self.assertEqual(set(r["ordem_priorizada"]), {c["codigo"] for c in carreira["competencias"]})
                self.assertEqual(r["etapas"][2]["itens"][0]["titulo"], carreira["projeto_portfolio"]["titulo"])
                self.assertFalse(r["altera_ranking_top3"])
                pos = {comp: i for i, comp in enumerate(r["ordem_priorizada"])}
                for c in carreira["competencias"]:
                    for pre in c.get("pre_requisitos", []):
                        self.assertLess(pos[pre], pos[c["codigo"]])

    def test_41_roadmaps_sem_lacunas_em_todas_as_dez_carreiras(self):
        for codigo in self.carreiras:
            with self.subTest(carreira=codigo):
                r = motor.gerar_roadmap_personalizado(self.base, codigo, self.niveis(codigo, referencia=True))
                self.assertEqual(r["status"], "sem_lacunas")
                self.assertEqual(r["ordem_priorizada"], [])
                self.assertEqual(r["total_niveis_de_lacuna"], 0)
                self.assertEqual([len(e["itens"]) for e in r["etapas"]], [0, 0, 1, 1])
                self.assertIn("consolidação", r["etapas"][2]["itens"][0]["orientacao"])

    def test_42_roadmap_incompleto_nao_fabrica_trilha_definitiva(self):
        for codigo in self.carreiras:
            with self.subTest(carreira=codigo):
                niveis = self.niveis(codigo, 0)
                primeira = next(iter(niveis))
                niveis[primeira] = None
                r = motor.gerar_roadmap_personalizado(self.base, codigo, niveis)
                self.assertEqual(r["status"], "avaliacao_incompleta")
                self.assertEqual(r["etapas"], [])
                self.assertEqual(r["competencias_pendentes"], [primeira])

    def test_43_ordem_qa_respeita_dependencias(self):
        niveis = {"QA_01": 2, "QA_02": 2, "QA_03": 3, "QA_04": 0, "QA_05": 0}
        r = motor.gerar_roadmap_personalizado(self.base, "qa", niveis)
        self.assertEqual(r["ordem_priorizada"], ["QA_04", "QA_05"])
        self.assertEqual(len(r["etapas"][0]["itens"]), 2)
        self.assertEqual(len(r["etapas"][1]["itens"]), 2)

    def test_44_dependencia_ciclica_e_rejeitada(self):
        alterada = copy.deepcopy(self.base)
        itens = alterada["carreiras"]["qa"]["competencias"]
        itens[0]["pre_requisitos"] = [itens[1]["codigo"]]
        with self.assertRaisesRegex(ValueError, "cíclicas"):
            motor.gerar_roadmap_personalizado(alterada, "qa", self.niveis("qa", 0))

    def test_45_dependencia_inexistente_e_rejeitada(self):
        alterada = copy.deepcopy(self.base)
        alterada["carreiras"]["qa"]["competencias"][0]["pre_requisitos"] = ["NAO_EXISTE"]
        with self.assertRaises(ValueError):
            motor.gerar_roadmap_personalizado(alterada, "qa", self.niveis("qa", 0))

    def test_46_etapas_de_roadmap_fora_de_ordem_sao_rejeitadas(self):
        alterada = copy.deepcopy(self.base)
        etapas = alterada["parametros_roadmap"]["etapas"]
        etapas[0], etapas[1] = etapas[1], etapas[0]
        with self.assertRaisesRegex(ValueError, "Etapas do roadmap"):
            motor.gerar_roadmap_personalizado(alterada, "qa", self.niveis("qa", 0))

    def test_47_avaliar_competencias_nao_altera_ranking_top3(self):
        a, o = self.perfil("qa")
        anterior = motor.gerar_ranking_top3(self.base, a, o)
        motor.avaliar_lacunas_competencias(self.base, "qa", self.niveis("qa", 0))
        motor.gerar_roadmap_personalizado(self.base, "qa", self.niveis("qa", 0))
        posterior = motor.gerar_ranking_top3(self.base, a, o)
        self.assertEqual(anterior, posterior)

    def test_48_chamadas_nao_modificam_base_em_memoria(self):
        copia = copy.deepcopy(self.base)
        a, o = self.perfil("nuvem")
        motor.gerar_ranking_top3(self.base, a, o, ["RSTR07"], contradicoes_confirmadas=True)
        motor.gerar_roadmap_personalizado(self.base, "nuvem", self.niveis("nuvem", 0))
        self.assertEqual(self.base, copia)


if __name__ == "__main__":
    unittest.main(verbosity=2)
