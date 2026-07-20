import time
import requests
from collections import deque
import subprocess
import os
from datetime import datetime


# ==============================================================================
# DESCUBRIMIENTO DE ENDPOINT BASADO EN ARCHIVO (RUTA INTER-SISTEMA)
# ==============================================================================

def load_windows_ip():
    """
    Lee la IP del anfitrión Windows desde /mnt/e/.
    Si falla utiliza la IP del gateway WSL.
    """

    ip_file = "/mnt/e/Developer/Tools/LibreHardwareMonitor/python/windows_ip.txt"

    if os.path.exists(ip_file):
        try:
            with open(ip_file, "r", encoding="utf-8") as f:
                ip = f.read().strip()

                if ip:
                    print(
                        f"📖 IP Windows detectada desde archivo: {ip}"
                    )
                    return ip

        except Exception as e:
            print(f"⚠ Error leyendo windows_ip.txt: {e}")


    # Fallback WSL
    try:
        cmd = "ip route | grep default | awk '{print $3}'"

        ip_gateway = subprocess.check_output(
            cmd,
            shell=True
        ).decode().strip()

        if ip_gateway:
            print(
                f"📡 IP detectada mediante gateway WSL: {ip_gateway}"
            )

            return ip_gateway

    except Exception:
        pass


    return "127.0.0.1"



WINDOWS_IP = load_windows_ip()

URL = f"http://{WINDOWS_IP}:5005/data.json"



# ==============================================================================
# CONFIGURACIÓN TÉRMICA
# ==============================================================================

INTERVAL = 3

WINDOW_SIZE = 5


TEMP_WARNING = 58

TEMP_CRITICAL = 62

TEMP_HARD_LIMIT = 70


TEMP_RECOVERY = 58



# ==============================================================================
# LOG DE EVENTOS CRÍTICOS
# ==============================================================================

LOG_FILE = "thermal_watchdog_log.txt"



# ==============================================================================
# ESTADO GLOBAL
# ==============================================================================

temps = deque(maxlen=WINDOW_SIZE)

last_state = "NORMAL"

critical_latch = False



# ==============================================================================
# SENSOR
# ==============================================================================

def read_temp():
    """
    Lee temperatura desde Flask en Windows.
    """

    try:

        r = requests.get(
            URL,
            timeout=2
        )

        data = r.json()

        temp = float(data["Value"])


        # filtro sanitario

        if temp <= 0 or temp > 120:
            return None


        return temp


    except:

        return None



# ==============================================================================
# PROMEDIO MÓVIL
# ==============================================================================

def avg_temp():

    if len(temps) == 0:
        return None

    return sum(temps) / len(temps)



# ==============================================================================
# REGISTRO DE EVENTOS CRÍTICOS
# ==============================================================================

def write_thermal_log(temp, avg, reason):

    """
    Guarda evidencia cuando el watchdog ejecuta una acción crítica.
    """

    try:

        fecha = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        avg_str = (
            f"{avg:.2f}"
            if avg is not None
            else "N/A"
        )


        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as f:


            f.write("\n")
            f.write(
                "==================================================\n"
            )

            f.write(
                "THERMAL WATCHDOG EVENT\n"
            )

            f.write(
                f"Fecha: {fecha}\n"
            )

            f.write(
                f"Motivo: {reason}\n"
            )

            f.write(
                f"Temperatura actual: {temp:.2f} °C\n"
            )

            f.write(
                f"Promedio móvil: {avg_str} °C\n"
            )

            f.write(
                f"Endpoint: {URL}\n"
            )

            f.write(
                "Acción: pkill -f query.py\n"
            )

            f.write(
                "==================================================\n"
            )


        print(
            f"📄 Evento registrado en {LOG_FILE}"
        )


    except Exception as e:

        print(
            f"⚠ Error escribiendo log térmico: {e}"
        )



# ==============================================================================
# CONTROL QUERY
# ==============================================================================

def stop_query_process():

    try:

        subprocess.run(
            [
                "bash",
                "-c",
                "pkill -f query.py"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


        print(
            "🛑 query.py detenido por sobretemperatura"
        )


    except:

        print(
            "⚠ No se pudo detener query.py"
        )



# ==============================================================================
# SHUTDOWN TÉRMICO
# ==============================================================================

def trigger_shutdown(temp, avg, reason):

    global critical_latch


    critical_latch = True


    avg_str = (
        f"{avg:.2f}"
        if avg is not None
        else "N/A"
    )


    print("\n🔥 ALERTA CRÍTICA ACTIVADA")

    print(
        f"Motivo: {reason}"
    )

    print(
        f"Temp actual: {temp:.2f}°C | Promedio: {avg_str}°C"
    )


    # NUEVO:
    # registrar evidencia antes de matar proceso

    write_thermal_log(
        temp,
        avg,
        reason
    )


    stop_query_process()



# ==============================================================================
# EVALUACIÓN
# ==============================================================================

def evaluate(temp):

    global last_state, critical_latch


    temps.append(temp)

    avg = avg_temp()



    # HARD LIMIT

    if temp >= TEMP_HARD_LIMIT:

        if not critical_latch:

            trigger_shutdown(
                temp,
                avg,
                "HARD_LIMIT"
            )


        return "CRITICAL", avg



    # CRITICAL

    if temp >= TEMP_CRITICAL:


        if not critical_latch:

            trigger_shutdown(
                temp,
                avg,
                "TEMP_CRITICAL"
            )


        critical_latch = True


        return "CRITICAL", avg



    # WARNING

    if avg is not None and avg >= TEMP_WARNING:

        return "WARNING", avg



    return "NORMAL", avg



# ==============================================================================
# RECUPERACIÓN
# ==============================================================================

def recovery_check(temp):

    global critical_latch


    avg = avg_temp()


    if critical_latch:


        if (
            temp < TEMP_RECOVERY
            and
            (avg is None or avg < TEMP_WARNING)
        ):


            critical_latch = False


            print(
                "\n🟢 Sistema recuperado → watchdog desbloqueado\n"
            )



# ==============================================================================
# MAIN LOOP
# ==============================================================================

def main():

    print(
        f"🟢 Thermal Watchdog iniciado"
    )

    print(
        f"🌐 Endpoint: {URL}"
    )


    while True:


        temp = read_temp()


        if temp is None:


            print(
                "⚠ Sensor inválido o sin conexión"
            )


        else:


            state, avg = evaluate(temp)


            recovery_check(temp)


            avg_str = (
                f"{avg:.2f}"
                if avg is not None
                else "N/A"
            )


            print(
                f"🌡 CPU: {temp:.2f}°C | "
                f"Avg({len(temps)}): {avg_str}°C | "
                f"Estado: {state}"
            )



        time.sleep(INTERVAL)



if __name__ == "__main__":

    main()
