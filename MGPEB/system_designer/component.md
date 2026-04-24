# Component Diagram - MGPEB

[MGPEB Core]
    |
    |-- [Fila de Prioridade (heapq)]
    |-- [Módulo Física]
    |       |-- altura()
    |       |-- velocidade()
    |       |-- densidade_ar()
    |
    |-- [Módulo Lógica]
    |       |-- autorizar_pouso()
    |
    |-- [Módulo Ambiente]
    |       |-- gerar_ambiente()
    |
    |-- [Módulo Log]
    |
    |-- [Módulo Relatório]

[Entrada]
    -> Sensores
    -> Dados dos módulos

[Saída]
    -> Status de pouso
    -> Alertas
    -> Logs