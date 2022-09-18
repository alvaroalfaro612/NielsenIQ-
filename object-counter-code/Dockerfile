FROM python:3.8

WORKDIR /app

COPY . .
#RUN apk update
RUN pip install --upgrade pip
#RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install -r requirements.txt

CMD [ "python", "-m" , "counter.entrypoints.webapp"]


