FROM python:3

RUN pip install Pyro5

RUN pip install pandas

WORKDIR /app

COPY service.py .

COPY setup.py .

COPY run.sh .

ENTRYPOINT ["sh", "run.sh"]