FROM python:3.13.1-alpine3.20

WORKDIR /opt/amber

RUN apk add --no-cache supercronic \
    && addgroup -S amber && adduser -S amber -G amber \
    && mkdir -p data \
    && mkdir -p config \
    && chown amber:amber data \
    && apk --no-cache upgrade \
    && apk add --no-cache tzdata

USER amber

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV TZ=australia\Brisbane 


VOLUME /opt/amber/data \
  /opt/amber/config

ENTRYPOINT ["python", "app.py"]

LABEL org.opencontainers.image.authors="cabberley <chris@abberley.com.au>"
