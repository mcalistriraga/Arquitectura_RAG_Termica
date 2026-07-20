from flask import Flask, jsonify
import time
import json
import urllib.request
import os
import threading
import socket


app = Flask(__name__)


# =========================
# CONFIG
# =========================

MONITOR_LOG = True
INTERVAL_LOG = 2

LHM_JSON_URL = "http://localhost:8085/data.json"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FILE = os.path.join(
    BASE_DIR,
    "export_log.txt"
)


# =========================
# DESCUBRIMIENTO IP WINDOWS
# =========================

def create_windows_ip_file():
    """
    Detecta la IP del host Windows y genera
    windows_ip.txt para consumo desde WSL.

    Este archivo permite que thermal_watchdog.py
    descubra dinámicamente el endpoint Windows.
    """

    try:

        s = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )


        # No envía datos.
        # Solo fuerza a Windows a seleccionar
        # la interfaz de red activa.

        s.connect(
            ("10.255.255.255", 1)
        )


        ip_windows = s.getsockname()[0]


        s.close()


        ip_file = os.path.join(
            BASE_DIR,
            "windows_ip.txt"
        )


        with open(
            ip_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(ip_windows)


        print(
            f"📡 IP Windows guardada: {ip_file} -> {ip_windows}"
        )


    except Exception as e:

        print(
            f"⚠ No se pudo generar windows_ip.txt: {e}"
        )



# =========================
# BUSCADOR ROBUSTO EN ÁRBOL
# =========================

def find_cpu_temperature(node):
    """
    Busca específicamente:
    Nuvoton NCT6776F → Temperatures → Temperature #1
    """

    if isinstance(node, dict):

        if node.get("Text") == "Nuvoton NCT6776F":

            children = node.get("Children", [])

            for child in children:

                if child.get("Text") == "Temperatures":

                    for temp in child.get("Children", []):

                        if temp.get("Text") == "Temperature #1":

                            return parse_temp(
                                temp.get("Value")
                            )


        for k, v in node.items():

            if isinstance(v, (dict, list)):

                result = find_cpu_temperature(v)

                if result is not None:

                    return result


    elif isinstance(node, list):

        for item in node:

            result = find_cpu_temperature(item)

            if result is not None:

                return result


    return None



# =========================
# PARSER DE TEMPERATURA
# =========================

def parse_temp(value):

    if not value:

        return 0.0


    try:

        return float(
            str(value)
            .split()[0]
            .replace(",", ".")
        )


    except:

        return 0.0



# =========================
# SENSOR REAL
# =========================

def get_temperature():

    try:

        with urllib.request.urlopen(
            LHM_JSON_URL,
            timeout=2
        ) as r:

            data = json.loads(
                r.read().decode()
            )


        temp = find_cpu_temperature(data)


        if temp is None:

            print(
                "⚠ CPU temp no encontrada"
            )

            return 0.0


        return temp


    except Exception as e:

        print(
            f"❌ Error LHM: {e}"
        )

        return 0.0



# =========================
# LOG SYSTEM
# =========================

def init_log():

    if not MONITOR_LOG:

        return None


    try:

        first_write = not os.path.exists(
            LOG_FILE
        )


        f = open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        )


        if first_write:

            f.write(
                "# Thermal Monitor Log Start\n"
            )

            f.flush()

            print(
                f"📄 LOG creado: {LOG_FILE}"
            )


        return f


    except Exception as e:

        print(
            f"❌ ERROR creando log: {e}"
        )

        return None



def logger_loop():

    f = init_log()


    if f is None:

        print(
            "🛑 Logger abortado"
        )

        return


    while True:

        try:

            temp = get_temperature()


            line = (
                f"{time.time()},{temp}\n"
            )


            f.write(line)

            f.flush()


            time.sleep(
                INTERVAL_LOG
            )


        except Exception as e:

            print(
                f"⚠ Logger error: {e}"
            )

            time.sleep(2)



# =========================
# API
# =========================

@app.route("/data.json")
def data():

    temp = get_temperature()


    return jsonify({

        "id": 0,

        "Text": "CPU Temperature",

        "Value": temp,

        "Min": 0,

        "Max": 100,

        "timestamp": time.time()

    })



# =========================
# MAIN
# =========================

if __name__ == "__main__":

    print(
        "🔥 Export Temp Server v3 (robusto LHM + IP discovery)"
    )


    # Crear archivo de comunicación Windows ↔ WSL

    create_windows_ip_file()



    if MONITOR_LOG:

        t = threading.Thread(
            target=logger_loop,
            daemon=True
        )

        t.start()



    app.run(
        host="0.0.0.0",
        port=5005
    )
