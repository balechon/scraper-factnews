import requests
from bs4 import BeautifulSoup
import os
import re

# URL de la página principal
url = "https://ecuadorverifica.org/discurso-publico/"

# Modificar las cabeceras de la solicitud para incluir un User-Agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

# Crear un directorio para guardar los artículos
if not os.path.exists("articulos"):
    os.makedirs("articulos")

# Hacer una solicitud a la página web con las cabeceras modificadas
response = requests.get(url, headers=headers)

# Verificar que la solicitud fue exitosa
if response.status_code == 200:
    # Parsear el contenido HTML de la página con BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar todas las publicaciones en la página principal
    articles = soup.find_all('article', class_='ultimate-layouts-item')
    print(f"Se encontraron {len(articles)} publicaciones en la página principal.\n")
    
    # Iterar sobre cada publicación encontrada
    for index, article in enumerate(articles, start=1):
        # Obtener el enlace a la publicación individual
        link = article.find('a', class_='ultimate-layouts-title-link')['href']
        print(f"Enlace a la publicación: {link}")
        
        # Hacer una solicitud a la página de la publicación individual con las cabeceras modificadas
        article_response = requests.get(link, headers=headers)
        article_soup = BeautifulSoup(article_response.content, 'html.parser')

        # Extraer el título de la publicación
        title = article_soup.find('div', class_='entry-title').get_text(strip=True)
        
        # Extraer el contenido de la publicación
        content_div = article_soup.find('div', class_='entry-content')
        if content_div:
            # Eliminar scripts y estilos
            for script in content_div(["script", "style"]):
                script.decompose()
            content = content_div.get_text(separator="\n", strip=True)
        else:
            content = "Contenido no encontrado"
        
        # Crear un nombre de archivo válido basado en el título
        filename = re.sub(r'[^\w\-_\. ]', '_', title)
        filename = f"articulo_{index}_{filename[:50]}.txt"  # Limitar la longitud del nombre del archivo
        
        # Guardar el artículo en un archivo
        with open(os.path.join("articulos", filename), "w", encoding='utf-8') as file:
            file.write(f"Título: {title}\n\n")
            file.write(f"Enlace: {link}\n\n")
            file.write(f"Contenido:\n{content}")
        
        print(f"Artículo guardado: {filename}")
        print("="*80)
else:
    print(f"Error al acceder a la página: {response.status_code}")