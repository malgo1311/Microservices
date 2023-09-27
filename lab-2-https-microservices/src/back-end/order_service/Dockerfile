FROM python:3

RUN pip install Pyro5

RUN pip install pandas

WORKDIR /app

COPY order_service.py .

COPY setup.py .

COPY data/ ./data

COPY run.sh .

ENTRYPOINT ["sh", "run.sh"]
