import machine
import time

# Configuração dos Pinos
PINO_LDR = 34
PINO_BOTAO = 4

# Inicialização do ADC (LDR) e Botão
adc = machine.ADC(machine.Pin(PINO_LDR))
adc.atten(machine.ADC.ATTN_11DB) # Permite leitura de 0 a 3.3V (0-4095)
btn = machine.Pin(PINO_BOTAO, machine.Pin.IN, machine.Pin.PULL_UP)

# Variáveis de Estado
total_pecas = 0
peca_passando = False
tempo_bloqueio_inicio = 0
alerta_parada_emitido = False

# Limiares Parametrizados
LIMIAR_BLOQUEIO = 2500 
LIMITE_PARADA_MS = 5000 

print("Contador de Producao Inicializado")

while True:
    valor_ldr = adc.read()
    
    # Se a luz cai abruptamente, a tensão e a leitura do ADC no Wokwi diminuem.
    bloqueado = valor_ldr < LIMIAR_BLOQUEIO
    
    if bloqueado:
        if not peca_passando:
            peca_passando = True
            tempo_bloqueio_inicio = time.ticks_ms()
            alerta_parada_emitido = False
        else:
            tempo_bloqueado = time.ticks_diff(time.ticks_ms(), tempo_bloqueio_inicio)
            if not alerta_parada_emitido and tempo_bloqueado >= LIMITE_PARADA_MS:
                print("Alerta: Micro-parada detectada!")
                alerta_parada_emitido = True
    else:
        if peca_passando:
            # Borda de subida (a peça terminou de passar e a luz voltou)
            total_pecas += 1
            print(f"Peca detectada! Total: {total_pecas}")
            peca_passando = False
            alerta_parada_emitido = False

    # Rotina de Reset de Turno com Debounce
    if btn.value() == 0:
        time.sleep_ms(50)
        if btn.value() == 0:
            total_pecas = 0
            peca_passando = False
            alerta_parada_emitido = False
            print("Turno resetado com sucesso. Contadores zerados.")
            
            # Trava para aguardar o operador soltar o botão
            while btn.value() == 0:
                time.sleep_ms(20)

    # Suspiro da CPU para o Simulador
    time.sleep_ms(20)