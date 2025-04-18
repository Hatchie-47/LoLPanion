FROM python:3.10
COPY src/data_service /
COPY src/database /database
COPY src/common /common
COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]