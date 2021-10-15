FROM python:2.7

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3111
#RUN "python init_db.py"
CMD [ "python", "./init_db.py" ]
CMD [ "python", "./app.py" ]