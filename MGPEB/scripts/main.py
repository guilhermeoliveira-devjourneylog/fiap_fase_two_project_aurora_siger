import heapq
import math
import random
from enum import Enum

# =========================
# CORES (terminal)
# =========================
class Cor:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"

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
        cor = Cor.RED if self.severidade == Severidade.CRITICA else Cor.YELLOW
        return f"{cor}[T+{self.tempo:02d}s][{self.severidade.name}] {self.modulo_id} - {self.tipo.value}: {self.descricao}{Cor.RESET}"

# =========================
# FSM
# =========================
class StateMachine:
    def __init__(self, modulo):
        self.modulo = modulo

    def transition(self, novo_estado, motivo, tempo):
        anterior = self.modulo.estado
        self.modulo.estado = novo_estado
        self.modulo.registrar(
            f"TRANSIÇÃO: {anterior.value} → {novo_estado.value} | {motivo}",
            tempo
        )

    def processar_evento(self, evento, tempo):
        m = self.modulo

        if m.estado == Estado.ORBITA:
            if evento == Evento.INICIAR_DESCIDA:
                self.transition(Estado.DESCIDA, "Início da descida", tempo)

        elif m.estado == Estado.DESCIDA:
            if evento == Evento.COMBUSTIVEL_CRITICO:
                self.transition(Estado.ALERTA, "Combustível crítico", tempo)

            elif evento == Evento.FALHA_SENSOR:
                self.transition(Estado.ALERTA, "Falha sensor", tempo)

            elif evento == Evento.AREA_INSEGURA:
                self.transition(Estado.ALERTA, "Área insegura", tempo)

            elif evento == Evento.ALTURA_BAIXA:
                self.transition(Estado.APROXIMACAO, "Entrando em aproximação", tempo)

        elif m.estado == Estado.APROXIMACAO:
            if evento == Evento.POUSO_AUTORIZADO:
                self.transition(Estado.POUSO, "Pouso autorizado", tempo)

            elif evento == Evento.POUSO_ABORTADO:
                self.transition(Estado.ALERTA, "Pouso abortado", tempo)

        elif m.estado == Estado.POUSO:
            self.transition(Estado.FINALIZADO, "Pouso concluído", tempo)

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

    def registrar(self, msg, tempo):
        entry = f"[T+{tempo:02d}s][{self.id}][{self.estado.name}] {msg}"
        self.log.append(entry)
        print(Cor.CYAN + entry + Cor.RESET)

    def status(self):
        return (
            f"{self.id} | {self.estado.name} | "
            f"ALT={self.altura:.1f}m | VEL={self.velocidade:.1f}m/s | "
            f"FUEL={self.combustivel:.1f}"
        )

    def __lt__(self, other):
        return (self.prioridade, -self.criticidade) < (other.prioridade, -other.criticidade)

# =========================
# FÍSICA
# =========================
def altura(t, h0, v0, g=3.71):
    return max(0, h0 - v0*t - 0.5*g*t**2)

def velocidade(t, v0, g=3.71):
    return v0 + g*t

def densidade_ar(h, rho0=0.02, k=0.0001):
    return rho0 * math.exp(-k*h)

# =========================
# DECISÃO
# =========================
def autorizar_pouso(modulo, ambiente):
    C = modulo.combustivel > 20
    A = ambiente["atmosfera"]
    S = ambiente["sensores"]

    resultado = (C and S) and (A or ambiente["modo_emergencia"])

    print(f"🧠 DECISÃO -> C:{C} S:{S} A:{A} => {resultado}")

    return resultado

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
        print(alerta)
        heapq.heappush(self.alertas, alerta)

    def simular(self):
        tempo = 0

        print("\n🚀 INICIANDO SIMULAÇÃO\n")

        while self.fila:
            ambiente = gerar_ambiente()
            modulo = heapq.heappop(self.fila)

            modulo.fsm.processar_evento(Evento.INICIAR_DESCIDA, tempo)

            for t in range(1, 20):
                modulo.altura = altura(t, modulo.altura, modulo.velocidade)
                modulo.velocidade = velocidade(t, modulo.velocidade)

                rho = densidade_ar(modulo.altura)

                modulo.registrar(
                    f"ALT={modulo.altura:.2f}m | VEL={modulo.velocidade:.2f}m/s | "
                    f"FUEL={modulo.combustivel:.1f} | RHO={rho:.5f}",
                    tempo
                )

                modulo.combustivel -= 1.5

                if modulo.combustivel < 10:
                    modulo.fsm.processar_evento(Evento.COMBUSTIVEL_CRITICO, tempo)
                    self.gerar_alerta(modulo, TipoAlerta.COMBUSTIVEL_CRITICO, Severidade.CRITICA, "Combustível crítico", tempo)
                    break

                if not ambiente["sensores"]:
                    modulo.fsm.processar_evento(Evento.FALHA_SENSOR, tempo)
                    self.gerar_alerta(modulo, TipoAlerta.FALHA_SENSOR, Severidade.ALTA, "Falha de sensor", tempo)
                    break

                if not ambiente["area_livre"]:
                    modulo.fsm.processar_evento(Evento.AREA_INSEGURA, tempo)
                    self.gerar_alerta(modulo, TipoAlerta.AREA_NAO_SEGURA, Severidade.ALTA, "Área insegura", tempo)
                    break

                if modulo.altura < 100:
                    modulo.fsm.processar_evento(Evento.ALTURA_BAIXA, tempo)

                if modulo.altura < 10:
                    if autorizar_pouso(modulo, ambiente):
                        modulo.fsm.processar_evento(Evento.POUSO_AUTORIZADO, tempo)
                        self.pousados.append(modulo)
                    else:
                        modulo.fsm.processar_evento(Evento.POUSO_ABORTADO, tempo)
                        self.gerar_alerta(modulo, TipoAlerta.POUSO_ABORTADO, Severidade.ALTA, "Pouso abortado", tempo)
                    break

            print("\n📊 STATUS FINAL DO MÓDULO:")
            print(modulo.status())

            tempo += 1

        self.relatorio()

    def relatorio(self):
        print("\n" + "="*50)
        print("🚀 RELATÓRIO FINAL")
        print("="*50)

        print(f"\n✅ Pousados: {len(self.pousados)}")
        for m in self.pousados:
            print(f"{Cor.GREEN}✔ {m.id}{Cor.RESET}")

        print(f"\n🚨 Alertas: {len(self.alertas)}")

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