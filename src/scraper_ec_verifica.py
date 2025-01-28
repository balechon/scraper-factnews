import requests
import os
from bs4 import BeautifulSoup
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random
from modules.utils import crear_titulo_archivo, esperar_aleatoriamente
import logging
from modules.logging_config import configurar_logger
from modules.config import USER_AGENTS, URL_EC_VERIFICA, OUTPUT_PATH
from selenium.common.exceptions import NoSuchElementException
from httpcore import TimeoutException

import warnings
warnings.filterwarnings("ignore")

configurar_logger()

def setup_driver():
    """Configura y retorna una instancia del driver de Selenium."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=chrome_options)

def extract_article_details(article_soup):
    """Extrae los detalles de un artículo a partir de su contenido HTML."""
    title = article_soup.find('div', class_='entry-title').get_text(strip=True) if article_soup.find('div', class_='entry-title') else "Título no encontrado"
    metadate = article_soup.find('li', class_='meta-date').get_text(strip=True) if article_soup.find('li', class_='meta-date') else "Fecha no encontrada"
    metacategory = article_soup.find('li', class_='meta-category').get_text(strip=True) if article_soup.find('li', class_='meta-category') else "Categoría no encontrada"
    content_div = article_soup.find('div', class_='entry-content')
    if content_div:
        for script in content_div(["script", "style"]):
            script.decompose()
        content = content_div.get_text(separator="\n", strip=True)
    else:
        content = "Contenido no encontrado"
    return title, metadate, metacategory, content

def save_article_to_file(dir_data_path, title, link, metadate, metacategory, content):
    """Guarda los detalles de un artículo en un archivo."""
    with open(dir_data_path, "w", encoding='utf-8') as file:
        file.write(f"Título: {title}\n\n")
        file.write(f"Enlace: {link}\n\n")
        file.write(f"Fecha: {metadate}\n\n")
        file.write(f"Categoría: {metacategory}\n\n")
        file.write(f"Contenido:\n{content}")

def process_article(article, dir_data_path):
    """Procesa un artículo individual y lo guarda en un archivo."""
    link = article.find('a', class_='ultimate-layouts-title-link')['href']
    logging.info(f"Extrayendo artículo: {link}")
    
    esperar_aleatoriamente(1, 3)
    
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    article_response = requests.get(link, headers=headers)
    article_soup = BeautifulSoup(article_response.content, 'html.parser')

    title, metadate, metacategory, content = extract_article_details(article_soup)
    
    filename = crear_titulo_archivo(title, metadate)
    dir_data_path = dir_data_path / filename
    
    if dir_data_path.exists():
        logging.info(f"Artículo descargado previamente, saltando")
        return False
    
    save_article_to_file(dir_data_path, title, link, metadate, metacategory, content)
    logging.info(f"Descarga completa")
    return True

def navigate_to_next_page(driver, current_page):
    """Navega a la siguiente página de artículos."""
    try:
        next_page = current_page + 1
        next_page_link = driver.find_element(By.CSS_SELECTOR, f'.paginationjs-page[data-num="{next_page}"]')
        if next_page_link:
            next_page_link.click()
            time.sleep(2)  # Esperar a que la nueva página cargue
            return next_page
        else:
            logging.info("No se encontró el enlace a la siguiente página. Finalizando la extracción.")
            return None
    except NoSuchElementException:
        logging.info("No hay más páginas para navegar. Finalizando la extracción.")
        return None

def extraer_articulos(driver,dir_data_path):
    """Extrae todos los artículos de la página."""
    total_articles = 0
    current_page = 1
    
    while True:
        logging.info(f"Procesando página {current_page}")
  
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ultimate-layouts-item')))
        except TimeoutException:
            logging.error(f"Tiempo de espera agotado en la página {current_page}. Finalizando la extracción.")
            break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('article', class_='ultimate-layouts-item')
    
        for article in articles:
            if process_article(article, dir_data_path):
                total_articles += 1

        next_page = navigate_to_next_page(driver, current_page)
        if next_page is None:
            break
        current_page = next_page

    logging.info(f"Total de artículos extraídos: {total_articles}")

def check_project_structure():
    """Verifica y crea la estructura de directorios necesaria."""
    main_path = Path(__file__).resolve().parent.parent
    dir_data_path = main_path / OUTPUT_PATH
    if not dir_data_path.exists():
        os.makedirs(dir_data_path)
    return dir_data_path

def run():
    """Función principal que ejecuta el proceso de scraping."""
    dir_data_path = check_project_structure()
    driver = setup_driver()
    driver.get(URL_EC_VERIFICA)
    esperar_aleatoriamente(4, 5)

    extraer_articulos(driver,dir_data_path)
    driver.quit()

if __name__ == "__main__":
    logging.info("Iniciando scraping a la página Ecuador Verifica")
    run()
    logging.info("Scraping finalizado")
