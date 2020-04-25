FROM python:3

COPY . /usr/src/app

WORKDIR = /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache -r requirements.txt

EXPOSE 5000 5001

COPY . .

CMD [ "python", "./ComposteServer.py" ]

