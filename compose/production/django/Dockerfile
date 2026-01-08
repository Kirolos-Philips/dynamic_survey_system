FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/prod.txt

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY . /app

ENTRYPOINT ["/entrypoint"]
