FROM python:3.10
COPY src/frontend_service /
COPY src/common /common
COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]