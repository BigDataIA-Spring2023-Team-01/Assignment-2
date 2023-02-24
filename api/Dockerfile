FROM python:3.10.6-buster

WORKDIR /ass2

COPY . .

ADD requirements.txt /ass2/

RUN pip install --no-cache-dir --upgrade -r /ass2/requirements.txt

EXPOSE 8080

CMD ["uvicorn", "api.mainAPI:app", "--host", "0.0.0.0","--reload","--port","8080"]

