import requests
from bs4 import BeautifulSoup
import os

# --- CONFIGURACIÓN (Tus datos ya vinculados) ---
TOKEN = "8271951374:AAGsrKVoHFttCEQXb0_fagtCwfJPzuQHXeQ"
CHAT_ID = "1045927607"
URL = "https://www.dataroma.com/m/holdings.php?m=BRK"
FILE = "cartera.txt"

def enviar_telegram(mensaje):
    """Envía notificaciones a Telegram"""
    url_tg = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': mensaje,
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(url_tg, data=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

def obtener_cartera():
    """Extrae los símbolos de las acciones de Dataroma"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(URL, headers=headers, timeout=30)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        acciones = []
        
        # Buscamos los símbolos en los enlaces de la tabla
        for link in soup.find_all('a', href=True):
            if 'stock.php?sym=' in link['href']:
                simbolo = link.get_text(strip=True)
                if simbolo and len(simbolo) < 10:
                    acciones.append(simbolo)
        
        return sorted(list(set(acciones)))
    except Exception as e:
        print(f"Error conectando a Dataroma: {e}")
        return None

def ejecutar():
    print("🕵️ Iniciando rastreo en la nube...")
    lista_actual = obtener_cartera()
    
    if not lista_actual:
        print("❌ No se pudieron leer los datos de Datar
