FROM python:3.8.9-slim

RUN mkdir /app
WORKDIR /app
COPY ./ ./

RUN pip install -U -r requirements.txt 

CMD ["python", "autosklearn_automl.py"]
