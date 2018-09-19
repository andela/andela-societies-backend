FROM python:3.6.5
MAINTAINER "georgreen <georgreen.ngunga@andela.com>"
LABEL author="georgreen"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["/bin/bash", "-c", "python manage.py db init && python manage.py db migrate && python manage.py db upgrade &&  python manage.py runserver -p 5000 -h 0.0.0.0"]
