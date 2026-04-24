import heapq
import math
import random
from enum import Enum

# =========================
# ESTADOS
# =========================
class Estado(Enum):
    ORBITA = "orbita"
    DESCIDA = "descida"
    APROXIMACAO = "aproximacao"
    POUSO = "pouso"
    FINALIZADO = "finalizado"
    ALERTA = "alerta"

# =========================
# EVENTOS
# =========================
class Evento(Enum):
    INICIAR_DESCIDA = "iniciar_descida"
    COMBUSTIVEL_CRITICO = "combustivel_critico"
    FALHA_SENSOR = "falha_sensor"
    AREA_INSEGURA = "area_insegura"
    ALTURA_BAIXA = "altura_baixa"
    POUSO_AUTORIZADO = "pouso_autorizado"
    POUSO_ABORTADO = "pouso_abortado"

# =========================
# DECISÃO
# =========================
class Decisao(Enum):
    GO = "GO"
    HOLD = "HOLD"
    NO_GO = "NO_GO"

# =========================
# ALERTAS
# =========================
class TipoAlerta(Enum):
    COMBUSTIVEL_CRITICO = "combustivel_critico"
    POUSO_ABORTADO = "pouso_abortado"
    FALHA_SENSOR = "falha_sensor"
    AREA_NAO_SEGURA = "area_nao_segura"

class Severidade(Enum):
    BAIXA = 1
    MEDIA = 2
    ALTA = 3
    CRITICA = 4

class Alerta:
    def __init__(self, tipo, severidade, descricao, modulo_id, tempo):
        self.tipo = tipo
        self.severidade = severidade
        self.descricao = descricao
        self.modulo_id = modulo_id
        self.tempo = tempo

    def __lt__(self, other):
        return self.severidade.value > other.severidade.value

    def __str__(self):
        return f"[T{self.tempo}] [ALERTA {self.severidade.name}] {self.modulo_id} - {self.tipo.value}: {self.descricao}"

# =========================
# FSM
# =========================
class StateMachine:
    def __init__(self, modulo):
        self.modulo = modulo

    def transition(self, novo_estado, motivo):
        anterior = self.modulo.estado
        self.modulo.estado = novo_estado
        self.modulo.registrar(
            f"TRANSIÇÃO: {anterior.value} → {novo_estado.value} | {motivo}"
        )

    def processar_evento(self, evento):
        m = self.modulo

        if m.estado == Estado.ORBITA:
            if evento == Evento.INICIAR_DESCIDA:
                self.transition(Estado.DESCIDA, "Início da descida")

        elif m.estado == Estado.DESCIDA:
            if evento == Evento.COMBUSTIVEL_CRITICO:
                self.transition(Estado.ALERTA, "Combustível crítico")

            elif evento == Evento.FALHA_SENSOR:
                self.transition(Estado.ALERTA, "Falha sensor")

            elif evento == Evento.AREA_INSEGURA:
                self.transition(Estado.ALERTA, "Área insegura")

            elif evento == Evento.ALTURA_BAIXA:
                self.transition(Estado.APROXIMACAO, "Entrando em aproximação")

        elif m.estado == Estado.APROXIMACAO:
            if evento == Evento.POUSO_AUTORIZADO:
                self.transition(Estado.POUSO, "Pouso autorizado")

            elif evento == Evento.POUSO_ABORTADO:
                self.transition(Estado.ALERTA, "Pouso abortado")

        elif m.estado == Estado.POUSO:
            self.transition(Estado.FINALIZADO, "Pouso concluído")

# =========================
# MÓDULO
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

        self.fsm = StateMachine(self)

    def registrar(self, msg):
        entry = f"[{self.id} | {self.estado.value}] {msg}"
        self.log.append(entry)
        print(entry)

    def __lt__(self, other):
        return (self.prioridade, -self.criticidade) < (other.prioridade, -other.criticidade)

# =========================
# MODELOS FÍSICOS
# =========================
def altura(t, h0, v0, g=3.71):
    return max(0, h0 - v0*t - 0.5*g*t**2)

def velocidade(t, v0, g=3.71):
    return v0 + g*t

def densidade_ar(h, rho0=0.02, k=0.0001):
    return rho0 * math.exp(-k*h)

# =========================
# DECISION ENGINE
# =========================
def decision_engine(modulo, ambiente, alertas):
    score = 100
    motivos = []

    if modulo.combustivel < 10:
        score -= 50
        motivos.append("Combustível crítico")
    elif modulo.combustivel < 25:
        score -= 20
        motivos.append("Combustível baixo")

    if modulo.velocidade > 50:
        score -= 20
        motivos.append("Velocidade alta")

    if not ambiente["sensores"]:
        score -= 30
        motivos.append("Sensores offline")

    if not ambiente["area_livre"]:
        score -= 25
        motivos.append("Área insegura")

    if not ambiente["atmosfera"]:
        score -= 10
        motivos.append("Atmosfera instável")

    for alerta in alertas:
        if alerta.modulo_id == modulo.id:
            score -= alerta.severidade.value * 5

    score = max(0, score)

    if score >= 70:
        decisao = Decisao.GO
    elif score >= 40:
        decisao = Decisao.HOLD
    else:
        decisao = Decisao.NO_GO

    return decisao, score, motivos

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
# SISTEMA
# =========================
class MGPEB:
    def __init__(self):
        self.fila = []
        self.pousados = []
        self.alertas = []

    def adicionar_modulo(self, modulo):
        heapq.heappush(self.fila, modulo)

    def gerar_alerta(self, modulo, tipo, severidade, descricao, tempo):
        alerta = Alerta(tipo, severidade, descricao, modulo.id, tempo)
        modulo.registrar(str(alerta))
        heapq.heappush(self.alertas, alerta)

    def simular(self):
        tempo = 0

        while self.fila:
            ambiente = gerar_ambiente()
            modulo = heapq.heappop(self.fila)

            modulo.fsm.processar_evento(Evento.INICIAR_DESCIDA)

            for t in range(1, 20):
                modulo.altura = altura(t, modulo.altura, modulo.velocidade)
                modulo.velocidade = velocidade(t, modulo.velocidade)

                rho = densidade_ar(modulo.altura)

                modulo.registrar(
                    f"Altura={modulo.altura:.2f} Vel={modulo.velocidade:.2f} Densidade={rho:.5f}"
                )

                modulo.combustivel -= 1.5

                # ALERTAS
                if modulo.combustivel < 10:
                    modulo.fsm.processar_evento(Evento.COMBUSTIVEL_CRITICO)
                    self.gerar_alerta(modulo, TipoAlerta.COMBUSTIVEL_CRITICO, Severidade.CRITICA, "Combustível crítico", tempo)
                    break

                if not ambiente["sensores"]:
                    modulo.fsm.processar_evento(Evento.FALHA_SENSOR)
                    self.gerar_alerta(modulo, TipoAlerta.FALHA_SENSOR, Severidade.ALTA, "Falha sensor", tempo)
                    break

                if not ambiente["area_livre"]:
                    modulo.fsm.processar_evento(Evento.AREA_INSEGURA)
                    self.gerar_alerta(modulo, TipoAlerta.AREA_NAO_SEGURA, Severidade.ALTA, "Área insegura", tempo)
                    break

                if modulo.altura < 100:
                    modulo.fsm.processar_evento(Evento.ALTURA_BAIXA)

                # DECISÃO FINAL
                if modulo.altura < 10:
                    decisao, score, motivos = decision_engine(modulo, ambiente, self.alertas)

                    modulo.registrar(f"DECISÃO: {decisao.value} | Score={score}")
                    for m in motivos:
                        modulo.registrar(f" - {m}")

                    if decisao == Decisao.GO:
                        modulo.fsm.processar_evento(Evento.POUSO_AUTORIZADO)
                        self.pousados.append(modulo)

                    elif decisao == Decisao.HOLD:
                        modulo.registrar("HOLD - aguardando condições melhores")

                    else:
                        modulo.fsm.processar_evento(Evento.POUSO_ABORTADO)
                        self.gerar_alerta(
                            modulo,
                            TipoAlerta.POUSO_ABORTADO,
                            Severidade.CRITICA,
                            f"NO-GO Score={score}",
                            tempo
                        )
                    break

            tempo += 1

        self.relatorio()

    def relatorio(self):
        print("\n===== RELATÓRIO FINAL =====")
        print(f"Pousados: {len(self.pousados)}")
        print(f"Alertas: {len(self.alertas)}")

        print("\n--- ALERTAS PRIORIZADOS ---")
        while self.alertas:
            print(heapq.heappop(self.alertas))

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