FROM python:3.12-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/code:/code/app \
    FLASK_APP=app.main:app \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000

COPY requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run"]
