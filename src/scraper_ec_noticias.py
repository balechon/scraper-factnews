from httpcore import TimeoutException
import requests
from bs4 import BeautifulSoup
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random

# Lista de User-Agents para rotar
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0'
]

# URL base de la página principal
base_url = "https://ecuadorverifica.org/cierto/"

# Configurar opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Inicializar el driver de Selenium
driver = webdriver.Chrome(options=chrome_options)

# Crear un directorio para guardar los artículos
if not os.path.exists("articulos"):
    os.makedirs("articulos")

def esperar_aleatoriamente(min_segundos=2, max_segundos=5):
    time.sleep(random.uniform(min_segundos, max_segundos))

def extraer_articulos(driver):
    total_articles = 0
    current_page = 1
    
    while True:
        print(f"Procesando página {current_page}")
        
        # Esperar a que los artículos se carguen
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ultimate-layouts-item')))
        except TimeoutException:
            print(f"Tiempo de espera agotado en la página {current_page}. Finalizando la extracción.")
            break

        # Obtener el contenido de la página
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('article', class_='ultimate-layouts-item')
        
        print(f"Se encontraron {len(articles)} publicaciones en la página {current_page}.\n")
        
        for article in articles:
            total_articles += 1
            link = article.find('a', class_='ultimate-layouts-title-link')['href']
            print(f"Enlace a la publicación: {link}")
            
            esperar_aleatoriamente(1, 3)
            
            headers = {'User-Agent': random.choice(user_agents)}
            article_response = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_response.content, 'html.parser')

            title = article_soup.find('div', class_='entry-title').get_text(strip=True) if article_soup.find('div', class_='entry-title') else "Título no encontrado"
            
            content_div = article_soup.find('div', class_='entry-content')
            if content_div:
                for script in content_div(["script", "style"]):
                    script.decompose()
                content = content_div.get_text(separator="\n", strip=True)
            else:
                content = "Contenido no encontrado"
            
            filename = re.sub(r'[^\w\-_\. ]', '_', title)
            filename = f"articulo_{total_articles}_{filename[:50]}.txt"
            
            with open(os.path.join("articulos", filename), "w", encoding='utf-8') as file:
                file.write(f"Título: {title}\n\n")
                file.write(f"Enlace: {link}\n\n")
                file.write(f"Contenido:\n{content}")
            
            print(f"Artículo guardado: {filename}")
            print("="*80)

        # Buscar la siguiente página
        try:
            next_page = current_page + 1
            next_page_link = driver.find_element(By.CSS_SELECTOR, f'.paginationjs-page[data-num="{next_page}"]')
            if next_page_link:
                next_page_link.click()
                current_page = next_page
                time.sleep(2)  # Esperar a que la nueva página cargue
            else:
                print("No se encontró el enlace a la siguiente página. Finalizando la extracción.")
                break
        except NoSuchElementException: # type: ignore
            print("No hay más páginas para navegar. Finalizando la extracción.")
            break

    print(f"Total de artículos extraídos: {total_articles}")

# Navegar a la URL base
driver.get(base_url)
time.sleep(5)  # Esperar 5 segundos para asegurar que la página se cargue completamente

# Extraer artículos
extraer_articulos(driver)

# Cerrar el navegador
driver.quit()