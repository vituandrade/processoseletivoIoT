# Relatório do Candidato: Contador de Produção Não-Intrusivo

### Identificação do Candidato
- **Nome completo:** Victor Henrick Santos Andrade
- **GitHub:** https://github.com/vituandrade/processoseletivoIoT

---

## Visão Geral da Solução
O projeto é um sistema embarcado inteligente para contagem automatizada de produção em esteiras industriais. Ele elimina a dependência de CLPs pesados, utilizando um sensor óptico LDR para identificar a interrupção de feixes de luz sempre que uma peça transita pela linha. O sistema contabiliza lotes, atua como auditor para micro-paradas não planejadas (gargalos) e possui interface simplificada de hardware para o reinício de novos turnos de operação.

---

## Arquitetura do Sistema Embarcado
A arquitetura foi baseada na detecção de transições lógicas (bordas de descida e subida):
- A rotina principal lê continuamente um pino analógico (`ADC`). Quando a peça bloqueia a luz, uma flag de intertravamento (`peca_passando`) é acionada. A contagem efetiva só ocorre na "borda de subida" (quando a luz retorna), garantindo que peças longas não sejam contadas múltiplas vezes.
- Um temporizador não-bloqueante (`time.ticks_diff`) corre paralelamente quando a linha está obstruída. Se o tempo exceder 5000ms, o log de micro-parada é disparado.
- A rotina do botão possui uma trava de software de 50ms (*debounce*) e uma trava em laço `while` para impedir *floods* caso o operador mantenha o dedo pressionado.

---

## Componentes Utilizados na Simulação
No `diagram.json`, modelou-se a seguinte estrutura:
- **ESP32 DevKit C v4:** Módulo controlador principal.
- **Sensor LDR (wokwi-photoresistor-sensor):** Mapeado no pino 34 (ADC1), encarregado de traduzir a luminosidade dinâmica em variação de tensão (`0-4095`).
- **Pushbutton:** Instalado com ativação em baixa lógica (GND), com seu estado de *Pull-Up* estabilizado internamente pelo código MicroPython no GPIO 4.

---

## Decisões Técnicas Relevantes
- **Parametrização Analógica:** A escolha técnica de tratar o LDR como entrada analógica (ao invés de digital) permite flexibilidade para ajustar a sensibilidade do equipamento no chão de fábrica sem soldas, apenas variando a constante `LIMIAR_BLOQUEIO` no firmware.
- **Não-bloqueio:** Excluiu-se funções de atraso (`sleep`) prolongadas. A priorização da CPU via intervalos em milissegundos garante a passagem do tempo na virtualização do Wokwi, mitigando riscos de *Timeout* na esteira de validação automática (CI).

---

## Resultados Obtidos
O sistema obteve exatidão total nos testes operacionais:
- Detecta e incrementa de forma segura as passagens.
- Monitora pausas de 5s ativando o sistema de alarme com sucesso.
- Zera todas as variáveis de contagem e estado simultaneamente ao receber o pulso do botão.
