FROM selenium/standalone-chromium:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir pixi

WORKDIR /app

COPY . /app

RUN pixi install

CMD ["sleep", "infinity"]