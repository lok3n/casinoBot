FROM python:3.12

ENV PYTHONUNBUFFERED 1
ENV V Docerfile
ENV TZ=Europe/Moscow


RUN mkdir /code
WORKDIR /code
COPY . /code

# RUN apt-get update

RUN pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir uvicorn


# CMD ["python","main.py"]
# CMD ["uvicorn", "coll:app"]