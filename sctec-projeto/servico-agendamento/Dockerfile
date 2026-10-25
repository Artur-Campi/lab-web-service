FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py index.html consultar_banco.py ./

# sem buffer pro log aparecer na hora no docker-compose logs
ENV PYTHONUNBUFFERED=1
EXPOSE 5000
CMD ["python", "app.py"]
