FROM python:3

RUN pip install Pyro5

RUN pip install pandas

WORKDIR /app

COPY catalog_service.py .

COPY rw_lock.py .

COPY setup.py .

COPY run.sh .

COPY data/ ./data

ENTRYPOINT ["sh", "run.sh"]

EXPOSE 9090