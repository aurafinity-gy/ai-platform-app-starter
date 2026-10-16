FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml ./
COPY starter ./starter
COPY tests ./tests
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn","starter.api:app","--host","0.0.0.0","--port","8000"]
