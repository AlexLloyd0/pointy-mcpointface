FROM python:3.6.4

# -- Copy code
COPY /pointy /pointy
COPY /run.py /run.py

# -- Copy logging config
COPY /logs /logs
COPY /logging.yaml /logging.yaml

# -- Copy database directory
COPY /data /data

# -- Copy requirements files
COPY /Pipfile /Pipfile
COPY /Pipfile.lock /Pipfile.lock


# -- Install Pipenv:
RUN set -ex && pip install pipenv --upgrade

# -- Install dependencies:
RUN set -ex && pipenv install --deploy --system

# TODO: something like EXPOSE 80

ENTRYPOINT ["gunicorn", "run:app"]