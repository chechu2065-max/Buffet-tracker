import requests
from bs4 import BeautifulSoup
import os
import time
from collections import defaultdict

TOKEN = "8271951374:AAGsrKVoHFttCEQXb0_fagtCwfJPzuQHXeQ"
CHAT_ID = "1045927607"

INVERSORES = {
    "JIM SIMONS (RT)": "RT",
    "LI LU (CP)": "CP",
    "CHASE COLEMAN (TG)": "TG",
    "DAVID TEPPER (LAL)": "LAL",
    "WARREN BUFFETT (BRK)": "BRK",
    "DRUCKENMILLER (Duquesne)": "Duquesne",
    "BILL ACKMAN (PSH)": "PSH"
}

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        # Timeout corto para que no se quede colgado
        requests.post(url, data={'chat_id': CHAT_ID, 'text': mensaje, 'parse_mode': 'Markdown'}, timeout=10)
    except:
        print("Error al enviar a Telegram")

def ejecutar_bot():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    consenso = defaultdict(list)
    reporte_cambios = ""
    hubo_cambios_totales = False

    for nombre, id_dataroma in INVERSORES.items():
        print(f"Rastreando a {nombre}...")
        url = f"https://www.dataroma.com/m/holdings.php?m={id_dataroma}"
        try:
            # Timeout de 10 segundos para no bloquear el bot
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            tabla = soup.find('table', id='grid')
            
            if not tabla: 
                print(f"Tabla no encontrada para {nombre}")
                continue

            posiciones_actuales = []
            for fila in tabla.find_all('tr')[1:11]: # Reducimos a Top 10 para ir más rápido
                cols = fila.find_all('td')
                if len(cols) >= 5:
                    ticker = cols[1].get_text(strip=True)
                    cambio = cols[4].get_text(strip=True)
                    consenso[ticker].append(nombre)
                    icono = "🟢" if ("New" in cambio or "+" in cambio) else "🔴" if "-" in cambio else "⚪"
                    posiciones_actuales.append(f"{icono} {ticker} ({cambio})")

            estado_actual = "|".join(posiciones_actuales)
            archivo_estado = f"estado_{id_dataroma}.txt"
            
            if not os.path.exists(archivo_estado) or open(archivo_estado, "r").read() != estado_actual:
                hubo_cambios_totales = True
                with open(archivo_estado, "w") as f: f.write(estado_actual)
                reporte_cambios += f"🏛️ *{nombre}*\n" + "\n".join(posiciones_actuales[:5]) + "\n\n"

            time.sleep(2) # Pausa de seguridad para evitar bloqueos

        except Exception as e:
            print(f"Error con {nombre}: {e}")

    if hubo_cambios_totales:
        enviar_telegram("🚀 **NUEVOS MOVIMIENTOS**")
        enviar_telegram(reporte_cambios)
        
        # Lógica de Consenso (Simplificada para velocidad)
        msg_c = "🤝 *CONSENSO*\n"
        hay_c = False
        for t, fans in consenso.items():
            if len(fans) >= 2:
                hay_c = True
                msg_c += f"💎 *{t}* ({', '.join(fans)})\n"
        if hay_c: enviar_telegram(msg_c)

if __name__ == "__main__":
    ejecutar_bot()
                    
