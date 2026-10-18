
import collections
import collections.abc

# Compatibilidade do Experta com Python 3.12
collections.Mapping = collections.abc.Mapping

from experta import Fact, KnowledgeEngine, Rule


class MotorTeste(KnowledgeEngine):

    @Rule(Fact(interesse="programacao"))
    def recomendar(self):
        print("Regra executada com sucesso!")


motor = MotorTeste()
motor.reset()
motor.declare(Fact(interesse="programacao"))
motor.run()
