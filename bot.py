import os
import telebot
import requests
from bs4 import BeautifulSoup
import time

# --- CONFIGURACIÓN DE IDENTIDAD ---
# Usa secretos de GitHub para el TOKEN y tu CHAT_ID
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telebot.TeleBot(TOKEN)

# --- TUS 7 SABIOS ---
SABIOS = {
    "JIM SIMONS (RT)": "renaissance-technologies-llc",
    "LI LU (CP)": "himalaya-capital-management-llc",
    "CHASE COLEMAN (TG)": "tiger-global-management-llc",
    "DAVID TEPPER (LAL)": "appaloosa-management-lp",
    "WARREN BUFFETT (BRK)": "berkshire-hathaway-inc",
    "DRUCKENMILLER (Duquesne)": "duquesne-family-office-llc",
    "BILL ACKMAN (PSH)": "pershing-square-capital-management-l-p"
}

def obtener_datos_ww(id_whale):
    """Scraping de WhaleWisdom para obtener el Top 10"""
    url = f"https://whalewisdom.com/filer/{id_whale}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        tabla = soup.find('table', {'id': 'current_holdings_table'})
        filas = tabla.find_all('tr')[1:11]
        
        datos = []
        for f in filas:
            cols = f.find_all('td')
            if len(cols) > 5:
                datos.append({
                    'ticker': cols[1].text.strip(),
                    'var': cols[4].text.strip(),
                    'peso': cols[5].text.strip()
                })
        return datos
    except Exception as e:
        print(f"Error en {id_whale}: {e}")
        return None

def generar_reporte_total():
    """Genera el mensaje de consenso y detalle para los 7 sabios"""
    reporte_completo = "🐋 **WHALE TERMINAL PRO**\n"
    reporte_completo += f"📅 {time.strftime('%d/%m/%Y')}\n"
    reporte_completo += "—" * 10 + "\n\n"
    
    conteo_consenso = {}

    for nombre, id_ww in SABIOS.items():
        holdings = obtener_datos_ww(id_ww)
        if holdings:
            reporte_completo += f"🧙 **{nombre}**\n"
            for h in holdings:
                emoji = "🟢" if "+" in h['var'] or "New" in h['var'] else "🔴" if "-" in h['var'] else "⚪"
                reporte_completo += f"{emoji} {h['ticker']} ({h['peso']})\n"
                
                # Lógica de Consenso
                conteo_consenso[h['ticker']] = conteo_consenso.get(h['ticker'], 0) + 1
            reporte_completo += "\n"

    # Sección de Consenso
    reporte_completo += "🤝 **CONSENSO DETECTADO**\n"
    hay_consenso = False
    for ticker, num in conteo_consenso.items():
        if num >= 2:
            reporte_completo += f"💎 {ticker}: Coinciden {num} sabios\n"
            hay_consenso = True
    
    if not hay_consenso:
        reporte_completo += "Sin coincidencias esta semana.\n"
        
    return reporte_completo

if __name__ == "__main__":
    # Si se ejecuta manualmente o por GitHub Actions
    mensaje = generar_reporte_total()
    bot.send_message(CHAT_ID, mensaje, parse_mode="Markdown")

