from machine import Pin, ADC
import time

# ============================================================
# Contador de Producao Nao-Intrusivo - Firmware ESP32
# ============================================================

# --- Configuracao de Hardware ---
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)           # Habilita leitura em toda a faixa 0-3.3V (0-4095)

btn = Pin(4, Pin.IN, Pin.PULL_UP)  # Pull-up interno, acionamento em GND

# --- Constantes de Configuracao ---
LIMIAR_ESCURO = 2000                # ADC > 2000 = peca bloqueando o sensor (sombra)
TEMPO_MICROPARADA_MS = 5000          # 5s continuos bloqueado = alerta de microparada
DEBOUNCE_MS = 50                     # Debounce simples do botao de reset

# --- Variaveis de Estado ---
contador_pecas = 0
estado_anterior_escuro = False
tempo_inicio_escuro = 0
alerta_emitido = False

print("Contador de Producao Inicializado")

while True:
    # --- Leitura continua do sensor optico ---
    leitura = ldr.read()
    escuro_agora = leitura > LIMIAR_ESCURO

    # --- Borda de subida: peca comecou a bloquear a luz ---
    if escuro_agora and not estado_anterior_escuro:
        tempo_inicio_escuro = time.ticks_ms()
        alerta_emitido = False

    # --- Enquanto bloqueado: monitora microparada (nao-bloqueante) ---
    if escuro_agora:
        tempo_bloqueado = time.ticks_diff(time.ticks_ms(), tempo_inicio_escuro)
        if tempo_bloqueado >= TEMPO_MICROPARADA_MS and not alerta_emitido:
            print("Alerta: Micro-parada detectada!")
            alerta_emitido = True

    # --- Borda de descida: luz normalizou, peca concluiu a passagem ---
    if not escuro_agora and estado_anterior_escuro:
        contador_pecas += 1
        print(f"Peca detectada! Total: {contador_pecas}")

    estado_anterior_escuro = escuro_agora

    # --- Botao de reset (Pull-Up / ativo em nivel baixo) ---
    if btn.value() == 0:
        time.sleep_ms(DEBOUNCE_MS)          # debounce simples
        if btn.value() == 0:                # confirma pressionamento apos debounce
            contador_pecas = 0
            estado_anterior_escuro = False
            alerta_emitido = False

            while btn.value() == 0:         # trava ate o operador soltar o botao
                pass

            print("Turno resetado com sucesso. Contadores zerados.")

    time.sleep_ms(10)   # pequena pausa para nao saturar a CPU