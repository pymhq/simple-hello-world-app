FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install -r requirement.txt

EXPOSE 8000

ENV HOME=/

ENV OTEL_RESOURCE_ATTRIBUTES='service.name=My App Runner service'

CMD python3 hello.py
