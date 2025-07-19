FROM python:3.8-slim-buster

# Use archive mirrors because buster is EOL
RUN sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list && \
    sed -i '/security.debian.org/d' /etc/apt/sources.list && \
    apt update && apt upgrade -y && \
    apt install git -y

COPY requirements.txt /requirements.txt

RUN pip3 install -U pip && pip3 install -U -r /requirements.txt

RUN mkdir /LazyPrincess
WORKDIR /LazyPrincess

COPY start.sh /start.sh
CMD ["/bin/bash", "/start.sh"]
