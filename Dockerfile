FROM python:3.10.6-buster

WORKDIR /ass2

COPY ./ /ass2

RUN pip install --no-cache-dir --upgrade -r /ass2/requirements.txt

EXPOSE 8000

CMD ["uvicorn", "api.mainAPI:app", "--host", "0.0.0.0","--reload"]

