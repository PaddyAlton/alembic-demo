FROM python:3.8-slim

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /apolitical/fun-with-alembic

# install dependencies
RUN python3 -m pip install -U pip && pip install pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --three --system

# prepare to run application
COPY src src
ENV PYTHONPATH="${PYTHONPATH}:/apolitical/fun-with-alembic"

# don't run as root
RUN adduser --disabled-password my_new_user && chown -R my_new_user /apolitical
USER my_new_user

CMD ["python3", "src/app.py"]
