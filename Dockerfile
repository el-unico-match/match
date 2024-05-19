FROM python:3.11

# Container workdir
WORKDIR /

# Copies files into workdir
COPY .env /
