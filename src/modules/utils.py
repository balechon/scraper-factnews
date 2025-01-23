import re
import unicodedata
import time
import random
from datetime import datetime




MESES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12
}



def esperar_aleatoriamente(min_segundos=2, max_segundos=5):
    time.sleep(random.uniform(min_segundos, max_segundos))
    
def crear_titulo_archivo(titulo, fecha):
    #limpiar el texto del titulo
    titulo = titulo.lower()
    # Eliminar espacios al inicio y final
    titulo = titulo.strip()
    # Remover acentos
    titulo = unicodedata.normalize('NFKD', titulo).encode('ascii', 'ignore').decode('utf-8')
    # Eliminar símbolos especiales
    titulo = re.sub(r'[^a-z0-9\s]', '', titulo)
    #limitar el tamaño del titulo
    titulo = f"{titulo[:50]}"
    titulo = titulo.strip()
    #limpiar el texto de la fecha, minusculas 
    fecha = fecha.lower()
    #convertir el texo a fecha formato dd-mm-aaaa
    fecha = re.sub(r' de ', '-', fecha)
    #split para separar el dia, mes y año
    fecha = fecha.split('-')
    fecha_dt = datetime(int(fecha[2]), MESES[fecha[1]], int(fecha[0]))
    #convertir la fecha a string formato dd-mm-aaaa
    fecha = fecha_dt.strftime('%d-%m-%Y')
    titulo_archivo = f"{fecha}_{titulo}.txt"
    return titulo_archivo

    
    
