FROM python:3.11.4

# Create app directory
WORKDIR /usr/src/app

COPY . .
RUN pip install poetry && \
  poetry install --no-root --no-interaction --no-ansi

CMD [ "poetry", "run", "python", "main.py" ]
