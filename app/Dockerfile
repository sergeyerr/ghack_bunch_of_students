FROM python:latest
RUN apt-get update -y
COPY /. /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENV FLASK_APP=app.py
RUN pip install gunicorn flask
EXPOSE 8080
ENTRYPOINT [ "gunicorn" ]
CMD [ "--bind", "0.0.0.0:8080", "--timeout", "120", "app:app"]
