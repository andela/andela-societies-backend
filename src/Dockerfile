FROM python:3.6.5
MAINTAINER "georgreen <georgreen.ngunga@andela.com>"
LABEL author="georgreen"
COPY . /app
WORKDIR /app
RUN pip install pipenv==2018.10.13
RUN pipenv lock -r > requirements.txt
RUN pipenv lock -r -d > dev-requirements.txt
RUN exit
RUN pip install -r  requirements.txt
RUN pip install -r  dev-requirements.txt

CMD ["/bin/bash", "-c", "python manage.py db init && python manage.py db migrate && python manage.py db upgrade &&  python manage.py run -p 5000 -h 0.0.0.0"]
