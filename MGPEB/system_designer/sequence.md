# Sequence Diagram - MGPEB

Operador -> MGPEB: iniciar_simulacao()
MGPEB -> Fila: ordenar_prioridade()
MGPEB -> Ambiente: gerar_ambiente()

loop para cada módulo
    MGPEB -> Modulo: iniciar_descida()
    Modulo -> Física: calcular_altura()
    Modulo -> Física: calcular_velocidade()
    Modulo -> Ambiente: obter_densidade()

    MGPEB -> Lógica: autorizar_pouso()

    alt pouso autorizado
        MGPEB -> Modulo: status = POUSO
    else
        MGPEB -> Modulo: status = ALERTA
    end
end

MGPEB -> Relatório: gerar()