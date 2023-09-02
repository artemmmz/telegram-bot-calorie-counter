FROM python:3.11
WORKDIR /opt/project
COPY bot .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD [ "python3.11", "main.py" ]
