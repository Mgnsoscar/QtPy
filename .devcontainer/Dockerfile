FROM python:3.12-bullseye

WORKDIR /app

COPY ../src/requirements.txt ./src/requirements.txt

RUN cd src && pip install -r requirements.txt

COPY ../src ./src

CMD ["sleep", "infinity"]