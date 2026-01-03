import requests
from bs4 import BeautifulSoup
import os
from collections import defaultdict

# --- CONFIGURACIÓN ---
TOKEN = "8271951374:AAGsrKVoHFttCEQXb0_fagtCwfJPzuQHXeQ"
CHAT_ID = "1045927607"

# EL CONSEJO DE LOS 7 SABIOS (Los más rentables de los últimos 15 años)
INVERSORES = {
    "JIM SIMONS (RT)": "RT",           # Algoritmos / IA
    "LI LU (Himalaya)": "CP",          # Francotirador / Calidad
    "CHASE COLEMAN (Tiger)": "TG",     # Tecnología / Crecimiento
    "DAVID TEPPER (Appaloosa)": "LAL",  # Macro / Timing
    "WARREN BUFFETT (Berkshire)": "BRK",# Valor / Seguridad
    "STAN DRUCKENMILLER (Duquesne)": "Duquesne", # El Invicto / Macro
    "BILL ACKMAN (Pershing)": "PSH"    # Activismo / Convicción
}

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # Telegram permite max 4096 caracteres. Cortamos si es necesario.
    if len(mensaje) > 4000: mensaje = mensaje[:4000] + "..."
    requests.post(url, data={'chat_id': CHAT_ID, 'text': mensaje, 'parse_mode': 'Markdown'})

def ejecutar_bot():
    headers = {'User-Agent': 'Mozilla/5.0'}
    consenso = defaultdict(list)
    reporte_cambios = ""
    hubo_cambios_totales = False

    for nombre, id_dataroma in INVERSORES.items():
        url = f"https://www.dataroma.com/m/holdings.php?m={id_dataroma}"
        try:
            r = requests.get(url, headers=headers, timeout=20)
            soup = BeautifulSoup(r.text, 'html.parser')
            tabla = soup.find('table', id='grid')
            
            if not tabla: continue

            posiciones_actuales = []
            filas = tabla.find_all('tr')[1:16] # Analizamos Top 15 de cada uno
            
            for fila in filas:
                cols = fila.find_all('td')
                if len(cols) >= 5:
                    ticker = cols[1].get_text(strip=True)
                    cambio = cols[4].get_text(strip=True)
                    
                    # Guardamos para el análisis de consenso
                    consenso[ticker].append(nombre)
                    
                    # Marcamos visualmente la tendencia
                    icono = "🟢" if ("New" in cambio or "+" in cambio) else "🔴" if "-" in cambio else "⚪"
                    posiciones_actuales.append(f"{icono} {ticker} ({cambio})")

            # Lógica de persistencia para detectar novedades reales
            estado_actual = "|".join(posiciones_actuales)
            archivo_estado = f"estado_{id_dataroma}.txt"
            
            estado_previo = ""
            if os.path.exists(archivo_estado):
                with open(archivo_estado, "r") as f: estado_previo = f.read()

            if estado_actual != estado_previo:
                hubo_cambios_totales = True
                with open(archivo_estado, "w") as f: f.write(estado_actual)
                reporte_cambios += f"🏛️ *{nombre}*\n" + "\n".join(posiciones_actuales[:10]) + "\n\n"

        except Exception as e:
            print(f"Error con {nombre}: {e}")

    # --- GENERACIÓN DE SECCIÓN DE CONSENSO ---
    mensaje_consenso = "🤝 *CONSENSO DE ALTA CONVICCIÓN*\n_(Acciones compartidas por los Sabios)_\n\n"
    hay_coincidencias = False
    
    # Ordenamos por número de coincidencias (de más a menos)
    consenso_ordenado = sorted(consenso.items(), key=lambda x: len(x[1]), reverse=True)
    
    for ticker, fans in consenso_ordenado:
        if len(fans) >= 2: # Solo si coinciden 2 o más
            hay_coincidencias = True
            mensaje_consenso += f"💎 *{ticker}* → {len(fans)} coincidencias\n"
            mensaje_consenso += f"   _{', '.join(fans)}_\n\n"

    # --- ENVÍO DE RESULTADOS ---
    if hubo_cambios_totales:
        enviar_telegram("🚀 **NUEVOS MOVIMIENTOS DETECTADOS**")
        enviar_telegram(reporte_cambios)
        if hay_coincidencias:
            enviar_telegram(mensaje_consenso)
    else:
        print("Sin cambios relevantes hoy.")

if __name__ == "__main__":
    ejecutar_bot()
                    
