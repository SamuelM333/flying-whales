FROM python:3.6

WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN python3 -m pip install -r requirements.txt

ADD . /app
EXPOSE 5000

CMD ["./start.sh"]
