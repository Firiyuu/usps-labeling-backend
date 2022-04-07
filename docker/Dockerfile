FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y gettext libgettextpo-dev
RUN mkdir /uw-logistics
WORKDIR /uw-logistics
ADD requirements.txt /uw-logistics/
RUN pip install --default-timeout=100 -r requirements.txt
ADD . /uw-logistics/
RUN chmod +x /uw-logistics/docker/start.sh

CMD ["/uw-logistics/docker/start.sh"]
