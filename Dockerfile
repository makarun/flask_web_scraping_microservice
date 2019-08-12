FROM python:3.7

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt
RUN python create_db.py

ENTRYPOINT ["python"]

CMD ["app.py"]