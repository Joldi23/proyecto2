FROM python:3.8.18

RUN mkdir /app
WORKDIR /app

ADD ./web .

RUN pip install Flask==1.1.4 markupsafe==2.0.1 python-dotenv bcrypt PyMySQL

EXPOSE 8080

CMD ["python", "app.py", "runserver"]
