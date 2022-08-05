FROM python:3.10-buster

ENV PYTHONUNBUFFERED=1

WORKDIR /modbus
COPY . /modbus/

RUN pip install --upgrade pip \
 && pip install -r requirements.txt

CMD [ "python3", "./main.py" ]