FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 4567

# Server starten
CMD ["uvicorn", "src.load_app:app", "--host", "0.0.0.0", "--port", "4567"]
