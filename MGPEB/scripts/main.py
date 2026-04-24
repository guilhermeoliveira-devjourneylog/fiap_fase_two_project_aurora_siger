import heapq
import math
import random
from enum import Enum

# =========================
# ESTADOS DO MÓDULO
# =========================
class Estado(Enum):
    ORBITA = "orbita"
    DESCIDA = "descida"
    APROXIMACAO = "aproximacao"
    POUSO = "pouso"
    FINALIZADO = "finalizado"
    ALERTA = "alerta"

# =========================
# TIPOS DE ALERTA
# =========================
class TipoAlerta(Enum):
    COMBUSTIVEL_CRITICO = "combustivel_critico"
    POUSO_ABORTADO = "pouso_abortado"
    FALHA_SENSOR = "falha_sensor"
    AREA_NAO_SEGURA = "area_nao_segura"
    VELOCIDADE_ALTA = "velocidade_alta"

# =========================
# SEVERIDADE
# =========================
class Severidade(Enum):
    BAIXA = 1
    MEDIA = 2
    ALTA = 3
    CRITICA = 4

# =========================
# CLASSE ALERTA
# =========================
class Alerta:
    def __init__(self, tipo, severidade, descricao, modulo_id, tempo):
        self.tipo = tipo
        self.severidade = severidade
        self.descricao = descricao
        self.modulo_id = modulo_id
        self.tempo = tempo

    def __lt__(self, other):
        return self.severidade.value > other.severidade.value  # prioridade maior primeiro

    def __str__(self):
        return f"[T{self.tempo}] [ALERTA {self.severidade.name}] {self.modulo_id} - {self.tipo.value}: {self.descricao}"

# =========================
# CLASSE DO MÓDULO
# =========================
class Modulo:
    def __init__(self, id, prioridade, combustivel, massa, criticidade, eta):
        self.id = id
        self.prioridade = prioridade
        self.combustivel = combustivel
        self.massa = massa
        self.criticidade = criticidade
        self.eta = eta

        self.estado = Estado.ORBITA
        self.altura = 1000
        self.velocidade = 0
        self.log = []

    def registrar(self, msg):
        entry = f"[{self.id} | {self.estado.value}] {msg}"
        self.log.append(entry)
        print(entry)

    def __lt__(self, other):
        return (self.prioridade, -self.criticidade) < (other.prioridade, -other.criticidade)

# =========================
# MODELOS MATEMÁTICOS
# =========================
def altura(t, h0, v0, g=3.71):
    return max(0, h0 - v0*t - 0.5*g*t**2)

def velocidade(t, v0, g=3.71):
    return v0 + g*t

def densidade_ar(h, rho0=0.02, k=0.0001):
    return rho0 * math.exp(-k*h)

# =========================
# LÓGICA DE POUSO
# =========================
def autorizar_pouso(modulo, ambiente):
    C = modulo.combustivel > 20
    A = ambiente["atmosfera"]
    L = ambiente["area_livre"]
    S = ambiente["sensores"]

    return (C and S) and (A or ambiente["modo_emergencia"])

# =========================
# AMBIENTE
# =========================
def gerar_ambiente():
    return {
        "atmosfera": random.choice([True, True, False]),
        "area_livre": random.choice([True, True, False]),
        "sensores": random.choice([True, True, True, False]),
        "modo_emergencia": False
    }

# =========================
# SISTEMA MGPEB
# =========================
class MGPEB:
    def __init__(self):
        self.fila = []
        self.pousados = []
        self.alertas = []

    def adicionar_modulo(self, modulo):
        heapq.heappush(self.fila, modulo)

    # =========================
    # GERADOR DE ALERTA
    # =========================
    def gerar_alerta(self, modulo, tipo, severidade, descricao, tempo):
        alerta = Alerta(tipo, severidade, descricao, modulo.id, tempo)

        modulo.estado = Estado.ALERTA
        modulo.registrar(str(alerta))

        heapq.heappush(self.alertas, alerta)

    # =========================
    # SIMULAÇÃO
    # =========================
    def simular(self):
        tempo = 0

        while self.fila:
            ambiente = gerar_ambiente()
            modulo = heapq.heappop(self.fila)

            modulo.registrar("Iniciando descida")

            for t in range(1, 20):
                modulo.estado = Estado.DESCIDA

                modulo.altura = altura(t, modulo.altura, modulo.velocidade)
                modulo.velocidade = velocidade(t, modulo.velocidade)

                rho = densidade_ar(modulo.altura)

                modulo.registrar(
                    f"Altura={modulo.altura:.2f}m Vel={modulo.velocidade:.2f}m/s Densidade={rho:.5f}"
                )

                # Consumo
                modulo.combustivel -= 1.5

                # ALERTA: combustível crítico
                if modulo.combustivel < 10:
                    self.gerar_alerta(
                        modulo,
                        TipoAlerta.COMBUSTIVEL_CRITICO,
                        Severidade.CRITICA,
                        "Combustível abaixo de 10",
                        tempo
                    )
                    break

                # ALERTA: falha sensor
                if not ambiente["sensores"]:
                    self.gerar_alerta(
                        modulo,
                        TipoAlerta.FALHA_SENSOR,
                        Severidade.ALTA,
                        "Sensores offline",
                        tempo
                    )
                    break

                # ALERTA: área insegura
                if not ambiente["area_livre"]:
                    self.gerar_alerta(
                        modulo,
                        TipoAlerta.AREA_NAO_SEGURA,
                        Severidade.ALTA,
                        "Área de pouso obstruída",
                        tempo
                    )
                    break

                # Aproximação
                if modulo.altura < 100:
                    modulo.estado = Estado.APROXIMACAO

                # Pouso
                if modulo.altura < 10:
                    if autorizar_pouso(modulo, ambiente):
                        modulo.estado = Estado.POUSO
                        modulo.registrar("Pouso autorizado")
                        self.pousados.append(modulo)
                    else:
                        self.gerar_alerta(
                            modulo,
                            TipoAlerta.POUSO_ABORTADO,
                            Severidade.ALTA,
                            "Condições não atendidas",
                            tempo
                        )
                    break

            tempo += 1

        self.relatorio()

    # =========================
    # RELATÓRIO
    # =========================
    def relatorio(self):
        print("\n===== RELATÓRIO FINAL =====")
        print(f"Pousados: {len(self.pousados)}")
        print(f"Alertas: {len(self.alertas)}")

        print("\n--- ALERTAS PRIORIZADOS ---")
        while self.alertas:
            alerta = heapq.heappop(self.alertas)
            print(alerta)


# =========================
# EXECUÇÃO
# =========================
if __name__ == "__main__":
    sistema = MGPEB()

    modulos = [
        Modulo("M1", 1, 40, 1200, 5, 10),
        Modulo("M2", 2, 60, 900, 3, 15),
        Modulo("M3", 1, 25, 1500, 5, 5),
        Modulo("M4", 3, 80, 800, 2, 20)
    ]

    for m in modulos:
        sistema.adicionar_modulo(m)

    sistema.simular()