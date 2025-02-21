from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import BaseCrawler
from bs4 import BeautifulSoup
from modules.utils import crear_titulo_archivo, esperar_aleatoriamente
import logging
import re
import time
import random

class EcuadorVerificaScraper(BaseCrawler):
    def __init__(self):
        super().__init__("https://ecuadorverifica.org/category/verificaciones/page/{}/")
        self.links = []
    
    def extract_articles(self):
        """Implementación concreta para extraer enlaces"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        for articulo in soup.select('article.post'):
            titulo_tag = articulo.select_one('.entry-title h2 a')
            if titulo_tag:
                # titulo = titulo_tag.get_text(strip=True)
                link = titulo_tag['href'] 
                self.links.append(link)

        
    def _validate_article_date(self,year_cutoff):
        """Valida la fecha de un artículo en base a su url con regex y retorna true si es mayor a 2023"""
        #last url in self.links
        article_url = self.links[-1]
        pattern = r'/(\d{4})/(\d{2})/(\d{2})/'
        match = re.search(pattern, article_url)
        if match:
            year = int(match.group(1))
            return year < year_cutoff
        return False
    

    def get_all_links(self, year_cutoff:int=2023):
        """Método principal para obtener todos los enlaces"""
        page=1
        while True:
            logging.info(f"Extrayendo enlaces de la página {page}")

            self.driver.get(self.base_url.format(page))
            # Esperar carga de artículos
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article.post"))
            )
            self.extract_articles()
            if self._validate_article_date(year_cutoff):
                break
            # Verificar si hay más páginas
            next_page = self.driver.find_elements(By.CSS_SELECTOR, "li.pagination-next")
            if not next_page:
                logging.info("No hay más páginas disponibles")
                break

            page+=1
            # Delay humanoide (2-5 segundos)
            time.sleep(random.uniform(2, 5))


    def extract_article_content(self, article_url):
        """Extrae el contenido y metadata de un artículo."""
        self.driver.get(article_url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        title = soup.find('div', class_='entry-title').get_text(strip=True) if soup.find('div', class_='entry-title') else "Título no encontrado"
        metadate = soup.find('li', class_='meta-date').get_text(strip=True) if soup.find('li', class_='meta-date') else "Fecha no encontrada"
        metacategory = soup.find('li', class_='meta-category').get_text(strip=True) if soup.find('li', class_='meta-category') else "Categoría no encontrada"
        content_div = soup.find('div', class_='entry-content')
        if content_div:
            for script in content_div(["script", "style"]):
                script.decompose()
            content = content_div.get_text(separator="\n", strip=True)
        else:
            content = "Contenido no encontrado"

        return title, metadate, metacategory, content
