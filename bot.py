import requests
from bs4 import BeautifulSoup
import os

TOKEN = "8271951374:AAGsrKVoHFttCEQXb0_fagtCwfJPzuQHXeQ"
CHAT_ID = "1045927607"
URL = "https://www.dataroma.com/m/holdings.php?m=BRK"
FILE = "cartera.txt"

def enviar(msg):
    u = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(u, data={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'})

def ejecutar():
    h = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(URL, headers=h, timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')
        acciones = []
        for a in soup.find_all('a', href=True):
            if 'stock.php?sym=' in a['href']:
                s = a.get_text(strip=True)
                if s and len(s) < 10: acciones.append(s)
        
        if not acciones:
            print("Error: No se leyeron acciones")
            return

        lista_actual = ",".join(sorted(list(set(acciones))))

        if not os.path.exists(FILE):
            with open(FILE, "w") as f: f.write(lista_actual)
            enviar("🚀 *¡BOT EN LA NUBE ACTIVADO!*")
        else:
            with open(FILE, "r") as f: anterior = f.read()
            if lista_actual != anterior:
                enviar("🔔 *¡CAMBIO EN LA CARTERA!*")
                with open(FILE, "w") as f: f.write(lista_actual)
            else:
                print("Sin cambios")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    enviar("Prueba de conexión desde GitHub")
    ejecutar()
