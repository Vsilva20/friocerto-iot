import json
import random
import time
import paho.mqtt.client as mqtt

# Configurações
BROKER = "localhost"
PORTA = 1883
INTERVALO = 2  # 2s no laboratório; 60s em produção
ANOMALIA_APOS = 120 #120s normalmente
DURACAO_ALERTA = 300 #300s normalmente

LOJAS = [f"loja_{i:02d}" for i in range(1, 15)]
LOJA_ANOMALIA = "loja_07"

# Conexão MQTT
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="friocerto-simulador"
)

client.connect(BROKER, PORTA, 60)
client.loop_start()

inicio = time.monotonic()
inicio_anomalia = None
alerta_enviado = False

print("Simulador FrioCerto iniciado!")

try:
    while True:
        tempo_decorrido = time.monotonic() - inicio

        for loja in LOJAS:
            temperatura = round(random.uniform(3, 7), 2)
            umidade = round(random.uniform(55, 70), 2)

            # Anomalia simulada na loja 07
            if loja == LOJA_ANOMALIA and tempo_decorrido >= ANOMALIA_APOS:
                temperatura = 12.4

                if inicio_anomalia is None:
                    inicio_anomalia = time.monotonic()

            payload = {
                "loja_id": loja,
                "temperatura": temperatura,
                "umidade": umidade,
                "timestamp": int(time.time())
            }

            topico = f"friocerto/abc/{loja}/temperatura"

            client.publish(
                topico,
                json.dumps(payload),
                qos=0
            )

            print(f"{loja}: {temperatura} C")

        # Publicar alerta após 5 minutos fora da faixa
        if inicio_anomalia is not None and not alerta_enviado:
            duracao = time.monotonic() - inicio_anomalia

            if duracao > DURACAO_ALERTA:
                alerta = {
                    "loja_id": LOJA_ANOMALIA,
                    "tipo": "temperatura_alta",
                    "temperatura": 12.4,
                    "timestamp": int(time.time())
                }

                topico_alerta = (
                    f"friocerto/abc/{LOJA_ANOMALIA}/alerta"
                )

                client.publish(
                    topico_alerta,
                    json.dumps(alerta),
                    qos=1
                ).wait_for_publish()

                alerta_enviado = True
                print("ALERTA CRITICO: loja_07!")

        print("--------------------")
        time.sleep(INTERVALO)

except KeyboardInterrupt:
    print("Encerrando simulacao...")

finally:
    client.disconnect()
    client.loop_stop()
