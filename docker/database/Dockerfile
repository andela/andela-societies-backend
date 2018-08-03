FROM python:2.7

MAINTAINER "Crispus Kamau <crispus.kamau@andela.com>"

RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /usr/local/bin/cloud_sql_proxy

RUN chmod +x /usr/local/bin/cloud_sql_proxy

COPY scripts/database.sh /usr/local/bin/

EXPOSE 3300

CMD ["bash", "database.sh"]

