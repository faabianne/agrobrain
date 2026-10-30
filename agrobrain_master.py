import serial
import serial.tools.list_ports
import time
import re
import sys
import numpy as np
from sklearn.tree import DecisionTreeClassifier

# --- CÓDIGOS DE COLOR ANSI (ESTILO INDUSTRIAL SCADA) ---
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"

def limpiar_pantalla():
    # Opcional: limpia la terminal si deseas simular un dashboard dinámico
    pass

def encontrar_puerto_arduino():
    puertos = serial.tools.list_ports.comports()
    for puerto in puertos:
        if "ACM" in puerto.device or "USB" in puerto.device:
            print(f"{GREEN}✅ [SYSTEM INIT]: Arduino detectado en -> {puerto.device}{RESET}")
            return puerto.device
    return None

# --- CONFIGURACIÓN DE CONEXIÓN ---
PORT = encontrar_puerto_arduino()
BAUD = 9600

if PORT is None:
    print(f"{RED}❌ [CRITICAL ERROR]: No se encontró ningún dispositivo Arduino conectado.{RESET}")
    sys.exit(1)

# --- ENTRENAMIENTO DEL MODELO DE IA (AGROBRAIN AI CORE) ---
print(f"{CYAN}⚙️ [AI ENGINE]: Entrenando modelo de árbol de decisión agronómico...{RESET}")
X_train = np.array([
    [22.0, 50.0, 20.0, 80.0],  # Suelo seco -> Riego (1)
    [25.0, 45.0, 30.0, 90.0],  # Suelo seco -> Riego (1)
    [21.0, 60.0, 50.0, 60.0],  # Suelo óptimo -> Reposo (0)
    [23.0, 55.0, 65.0, 70.0],  # Suelo óptimo -> Reposo (0)
    [20.0, 70.0, 80.0, 40.0],  # Suelo saturado -> Exceso (2)
    [28.0, 40.0, 25.0, 95.0],  # Estrés hídrico -> Riego (1)
])
y_train = np.array([1, 1, 0, 0, 2, 1])

modelo_riego = DecisionTreeClassifier(random_state=42)
modelo_riego.fit(X_train, y_train)
print(f"{GREEN}🚀 [AI READY]: Modelo entrenado y listo para inferencia en tiempo real.{RESET}\n")

def ejecutar_panel_scada(conexion, temp, hum_aire, hum_suelo, luz, nivel_agua):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Cabecera de Grado Industrial
    print(f"\n{BOLD}{BLUE}============================================================{RESET}")
    print(f"{BOLD}{BLUE}  AGROBRAIN SCADA TERMINAL v2.5 | TIMESTAMP: {timestamp} {RESET}")
    print(f"{BOLD}{BLUE}============================================================{RESET}")
    
    # Bloque de Telemetría de Sensores
    print(f"{CYAN} [TELEMETRÍA DE NODOS FÍSICOS]:{RESET}")
    print(f"   ├─ 🌡️ Temperatura Ambiental : {BOLD}{temp} °C{RESET}")
    print(f"   ├─ 💧 Humedad Ambiental     : {BOLD}{hum_aire} %{RESET}")
    print(f"   ├─ 🌱 Humedad del Suelo     : {BOLD}{hum_suelo} %{RESET}")
    print(f"   ├─ ☀️ Intensidad Lumínica   : {BOLD}{luz} %{RESET}")
    
    # Estado del Tanque con colores de alerta
    if nivel_agua == 1:
        print(f"   └─ 🛢️ Nivel del Tanque      : {GREEN}{BOLD}SUFICIENTE [OK - LED VERDE]{RESET}")
    else:
        print(f"   └─ 🛢️ Nivel del Tanque      : {RED}{BOLD}ALERTA: BAJO NIVEL [LED ROJO]{RESET}")
    
    print(f"{BLUE}------------------------------------------------------------{RESET}")

    # 1. Capa de Seguridad Mecánica (Boya / Tanque)
    if nivel_agua == 0:
        print(f"{RED}{BOLD} [ALARMA CRÍTICA]: Tanque de agua vacío.{RESET}")
        print(f"{YELLOW} ➔ ACCIÓN DE SEGURIDAD: Bomba bloqueada por protección hidráulica.{RESET}")
        try:
            conexion.write(b'0')
        except:
            pass
        print(f"{BLUE}============================================================{RESET}\n")
        return

    # 2. Inferencia del Motor de Inteligencia Artificial
    entrada_actual = np.array([[temp, hum_aire, hum_suelo, luz]])
    prediccion_ia = modelo_riego.predict(entrada_actual)[0]

    print(f"{MAGENTA} [MOTOR DE INFERENCIA IA]:{RESET}")
    if prediccion_ia == 1:
        print(f"   {YELLOW}⚡ [DIAGNÓSTICO]: Se detectó déficit hídrico en la raíz.{RESET}")
        print(f"   {GREEN}➔ COMANDO SCADA: ACTIVAR SISTEMA DE RIEGO (Orden enviada).{RESET}")
        try:
            conexion.write(b'1')
        except:
            pass
    elif prediccion_ia == 0:
        print(f"   {GREEN}✅ [DIAGNÓSTICO]: Condiciones hídricas estables y óptimas.{RESET}")
        print(f"   {BLUE}➔ COMANDO SCADA: SISTEMA EN REPOSO (Sin acción requerida).{RESET}")
        try:
            conexion.write(b'0')
        except:
            pass
    else:
        print(f"   {CYAN}🌧️ [DIAGNÓSTICO]: Saturación de humedad detectada.{RESET}")
        print(f"   {YELLOW}➔ COMANDO SCADA: RIEGO SUSPENDIDO (Protección anti-encharcamiento).{RESET}")
        try:
            conexion.write(b'0')
        except:
            pass

    # 3. Diagnóstico Predictivo de Cultivos
    print(f"{BLUE}------------------------------------------------------------{RESET}")
    print(f"{CYAN} [ANÁLISIS FITOSANITARIO PREDICTIVO]:{RESET}")
    if 20 <= temp <= 28 and 40 <= hum_suelo <= 70:
        print(f"   {GREEN}🌽 MAÍZ / GRANO: [ÓPTIMO] Desarrollo vegetativo favorable.{RESET}")
    elif hum_suelo < 35:
        print(f"   {YELLOW}⚠️ ALERTA DE CULTIVO: Estrés hídrico inminente en zona radicular.{RESET}")
    else:
        print(f"   {CYAN}🌱 ESTADO GENERAL: Monitoreo continuo de variables activo.{RESET}")
    
    print(f"{BOLD}{BLUE}============================================================{RESET}\n")

def iniciar_monitoreo():
    print(f"{CYAN}🔗 [CONNECT]: Abriendo socket serial en {PORT} a {BAUD} baudios...{RESET}")
    try:
        conexion = serial.Serial(PORT, BAUD, timeout=2)
        time.sleep(2)
        print(f"{GREEN}✨ [ONLINE]: Telemetría enlazada con éxito. Esperando tramas del Arduino...\n{RESET}")
        
        temp, hum_aire, hum_suelo, luz, nivel_agua = 22.0, 50.0, 40, 50, 1
        
        while True:
            if conexion.in_waiting > 0:
                linea = conexion.readline().decode('utf-8', errors='ignore').strip()
                
                # Parseo de datos sincronizado con el Arduino
                if "Humedad:" in linea and "Temperatura:" in linea:
                    res = re.findall(r"[-+]?\d*\.\d+|\d+", linea)
                    if len(res) >= 2:
                        hum_aire, temp = float(res[0]), float(res[1])
                elif "Suelo" in linea and "Humedad:" in linea:
                    res = re.findall(r"\d+", linea)
                    if len(res) >= 1: 
                        hum_suelo = int(res[-1])
                elif "Luz" in linea:
                    res = re.findall(r"\d+", linea)
                    if len(res) >= 1: 
                        luz = int(res[-1])
                elif "Tanque" in linea:
                    nivel_agua = 1 if "SUFICIENTE" in linea or "Verde" in linea else 0
                    
                    # Dispara el panel industrial cada vez que se completa un ciclo de lectura
                    ejecutar_panel_scada(conexion, temp, hum_aire, hum_suelo, luz, nivel_agua)

    except serial.SerialException:
        print(f"{RED}❌ [ERROR DE PUERTO]: Se perdió la comunicación con {PORT}. Verifica la conexión.{RESET}")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}🛑 [SHUTDOWN]: Operador detuvo el sistema SCADA. Sesión finalizada con éxito.{RESET}")

if __name__ == "__main__":
    iniciar_monitoreo()
