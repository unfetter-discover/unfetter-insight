FROM python:2.7-slim
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install -y swig
RUN apt-get install -y libpulse-dev
COPY . /app
COPY gunicorn_config.py /gunicorn_config.py

EXPOSE 5000
WORKDIR /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]
