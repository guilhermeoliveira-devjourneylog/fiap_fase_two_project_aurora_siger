# Activity Diagram - Fluxo MGPEB

Start
 ↓
Carregar módulos
 ↓
Organizar fila (heap)
 ↓
Loop módulos
 ↓
Simular descida
 ↓
Atualizar altura/velocidade
 ↓
Verificar combustível
 ├── Combustível crítico → ALERTA → Fim módulo
 ↓
Verificar altura < 10
 ├── Não → continuar descida
 ↓
Aplicar lógica booleana
 ├── Verdadeiro → POUSO
 ├── Falso → ALERTA
 ↓
Fim loop
 ↓
Gerar relatório
 ↓
End