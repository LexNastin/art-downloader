FROM python:3.11.4

WORKDIR /app

RUN wget -O - https://raw.githubusercontent.com/jontybrook/ffmpeg-install-script/main/install-ffmpeg-static.sh | bash -s -- --stable --force

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

VOLUME [ "/app/data" ]

CMD [ "python3", "main.py" ]
