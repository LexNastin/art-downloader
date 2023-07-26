FROM python:3.11.4

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

VOLUME [ "/app/data" ]

CMD [ "python3", "main.py" ]
