# pull the official docker image
FROM python:3.8-slim-buster

# install system dependencies
RUN apt-get update && apt-get install -y cmake

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY . .

# install dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# export port for the container
EXPOSE 8000

CMD ["uvicorn", "aquario.main:app", "--host", "0.0.0.0", "--port", "8000"]

RUN adduser --system backend
USER backend