# syntax=docker/dockerfile:1

FROM python:3.11.5

WORKDIR /pixel-diagnose

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]   