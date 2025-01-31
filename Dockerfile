FROM selenium/standalone-chrome:4.28.1-20250123
USER root
# Instalar paquetes necesarios
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip  \
    python3.12-venv && \
    rm -rf /var/lib/apt/lists/*
# Crear un usuario no root 
RUN groupadd appuser && useradd -m -d /home/appuser -g appuser appuser
# Crear un directorio de trabajo
WORKDIR /app/
# 3. Crear entorno virtual en el home del usuario
RUN python3 -m venv /home/appuser/venv

# 4. Copiar requirements.txt y usar el pip del entorno virtual
COPY --chown=appuser:appuser requirements.txt .
RUN /home/appuser/venv/bin/pip install --no-cache-dir -r requirements.txt

# Cambiar los permisos del directorio y su contenido
RUN chown -R appuser:appuser /app 
# Cambiar al usuario no root
USER appuser
# Copiar el contenido del proyecto al directorio de trabajo
COPY --chown=appuser . .
# Ejecutar el comando de inicio
CMD ["/home/appuser/venv/bin/python3", "src/scraper_ec_verifica.py"]