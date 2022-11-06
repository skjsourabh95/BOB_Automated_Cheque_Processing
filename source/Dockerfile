
FROM  --platform=linux/amd64 python:3.8

ENV  DOCKER_DEFAULT_PLATFORM=linux/amd64

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc
RUN apt-get install ffmpeg libsm6 libxext6  -y

# Install production dependencies.
RUN pip install -r requirements.txt
RUN pip uninstall werkzeug -y
RUN pip install -v https://github.com/pallets/werkzeug/archive/refs/tags/2.0.3.tar.gz

EXPOSE 8050

# CMD exec gunicorn --bind 0.0.0.0:80 --workers 1 --threads 8 --timeout 0 index:app


CMD [ "python", "index.py" ]
