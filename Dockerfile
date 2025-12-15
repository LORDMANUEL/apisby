FROM python:3.11-slim

WORKDIR /app

COPY api/ ./api/
COPY instalar_todo.sh ./
COPY README.md ./

RUN python -m venv /app/api/venv \
    && /app/api/venv/bin/pip install --upgrade pip \
    && /app/api/venv/bin/pip install -r /app/api/requirements.txt

ENV PATH="/app/api/venv/bin:$PATH"

EXPOSE 8080

CMD ["python", "api/app.py"]
