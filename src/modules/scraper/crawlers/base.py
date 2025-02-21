# modules/base_connector.py
import random
from abc import ABC, abstractmethod
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

# Configuración común
from modules.config import USER_AGENTS
from modules.utils import esperar_aleatoriamente

class BaseCrawler(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.driver = self._setup_driver()
        self.output_path = Path("data")
        self._create_output_dir()
    
    def _setup_driver(self):
        """Configuración común de Selenium"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        return webdriver.Chrome(options=chrome_options)
    
    def _create_output_dir(self):
        self.output_path.mkdir(exist_ok=True)
    
    def safe_quit(self):
        if self.driver:
            self.driver.quit()
    