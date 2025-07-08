# Dockerfile para el proyecto Gradio + Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

COPY . /app

# Instala las dependencias
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expone el puerto por defecto de Gradio
EXPOSE 7860

# Comando para lanzar la app (ajusta si usas otro entrypoint)
CMD ["python", "main.py"]
