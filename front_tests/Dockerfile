FROM python:latest
RUN apt-get update -y
COPY /. /app
WORKDIR /app
ENV FLASK_APP=app.py
RUN pip install gunicorn flask
EXPOSE 5000
ENTRYPOINT [ "gunicorn" ]
CMD [ "--bind", "0.0.0.0:5000", "wsgi:app"]
