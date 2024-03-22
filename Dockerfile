FROM python:3.12.2-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_CREATE=False
WORKDIR /app/

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry==1.8.2

RUN poetry --version
RUN poetry install  && \
    rm -rf ~/.cache/pypoetry/{cache,artifacts}

COPY . .
