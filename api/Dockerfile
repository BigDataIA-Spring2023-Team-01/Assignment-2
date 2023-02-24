FROM python:3.10.6-buster

WORKDIR /ass2

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*


COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

EXPOSE 8080

CMD ["uvicorn", "api.mainAPI:app", "--host", "0.0.0.0","--reload","--port","8080"]

