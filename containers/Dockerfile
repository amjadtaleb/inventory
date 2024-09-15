FROM python:3.12.3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update
# install python mysqlclient build requirements
RUN apt-get install -y python3-dev default-libmysqlclient-dev build-essential pkg-config
# on Fedora/RedHat we would `dnf install mysql-devel`

WORKDIR /centribal

COPY ../orders/requirements.txt /centribal/

RUN pip install -r requirements.txt
