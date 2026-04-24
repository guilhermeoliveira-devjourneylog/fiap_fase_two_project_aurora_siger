# Transições de Estado

ORBITA → DESCIDA
    trigger: início da simulação

DESCIDA → APROXIMACAO
    condição: altura < 100

APROXIMACAO → POUSO
    condição: altura < 10 AND lógica OK

APROXIMACAO → ALERTA
    condição: falha lógica

DESCIDA → ALERTA
    condição: combustível < 10

POUSO → FINALIZADO
    condição: pouso concluído