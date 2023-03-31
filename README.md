alembic-demo
============

An old demonstration project, provided here in case it helps someone in future. Some dependencies have been updated, but this caused some problems with the QA checks that I haven't fixed for now.

Introduction
------------

So, what is `alembic` then? Alembic is a _database migration tool_, a method for capturing database schema changes in version control.

Alembic is designed to work with `sqlalchemy`, a powerful ORM for Python. This project is designed to help you understand how to build projects with `sqlalchemy` and `alembic`. In particular, we'll give an example using a `FastAPI` web application.

(This demo was created largely by following [this tutorial](https://www.compose.com/articles/schema-migrations-with-alembic-python-and-postgresql/))

Setting up
----------

### Key tools

You're going to need two tools for this, Docker and Pipenv.

Docker is our usual containerisation tool, and here we are using it mainly to get a `postgres` database up and running. Here we assume you've already got Docker working on your machine.

Pipenv is our standard environment/dependency management tool for Python. Assuming you have Python on your machine, getting this is as simple as `pip install pipenv` (or possibly `pip3 install pipenv` on some systems).

### Environment set-up

This repo's `Pipfile` contains some handy scripts. Simply run `pipenv run setup` to run a custom script that does the following:

- configure pre-commit/pre-push Git hooks
- create a `.env` file if you didn't already have one locally
- set up a virtual environment with all production and development dependencies installed

Future commands executed using `pipenv run ...` will run the commands in the virtual environment.

Next, we're going to want a `postgres` database for our work. This repo's `docker-compose.yml` will sort that out for us.

`docker-compose up` will:

- create a volume called `alembic-stuff-data` for you (this volume will be persistent storage for the DB)
- start a container called `postgres-alembic-stuff`, running `postgres:14.2` in detached (background) mode
- make the database accessible on localhost, port 5555 (`127.0.0.1:5555/alembic-stuff`)
- start a container called `demo-api`; this will serve a `FastAPI` app on localhost, port 8765 (`http://127.0.0.1:8765/`)

**OUTCOME:** you now have a Python environment with all the relevant dependencies, a `postgres` database running on port 5555, and a demonstration `FastAPI` application.

_(see 'When you're done', below, for how to shut down the database and tidy up)_

Alembic
-------

### Preamble

The central idea behind `alembic` is to allow you to automatically create a database with the right schema, and roll out new versions/roll back old versions.

There are two things in the repository related to `alembic` that we need to bear in mind:

1. `/alembic.ini`, a configuration file for `alembic` (the only change from the default is `sqlalchemy.url` which points at our `postgres` database, assuming you use the default `make` command)
2. `/alembic`, a subdirectory containing the version-controlled migration scripts. In particular `/alembic/env.py` has been modified to import our actual source code (implemented using `sqlalchemy`). Don't worry about anything else in this subdirectory.

These already exist in this project. 

If you were setting up a fresh project, the command `pipenv run alembic init alembic` could be run. This sets up all the default file structures.

### Developing with Alembic

Here life is made easier by the use of Pipenv scripts (it is worth looking at the Pipfile to see exactly what is being executed in the virtual environment):

- `pipenv run alembic-revision -m "YOUR MESSAGE HERE"` will create a new `alembic` revision

What's a revision? A revision is simply an automatically generated Python script in `alembic/versions` with a unique ID and a slug based on the custom message you provided. Crucially, it will contain an `upgrade` and a `downgrade` function, and a variable indicating the ID of the previous revision. This means the revisions can be applied in sequence to change the database schema to any version: you can roll backwards and forwards with ease.

Usually, you're going to want the _latest_ revision. To get it, run:

- `pipenv run alembic-latest`

This script will simply ensure that your database is in the 'head' state. It's equivalent to `pipenv run alembic upgrade head`, so it's saving you from typing a few characters (and is phrased a bit more intuitively).

It is wise to be cautious about the contents of the revision scripts. For example, if you change the name of a column, the automatically generated script will think you've deleted a column and added a new one. If you want to avoid losing the data held in that column, you will need to manually edit the script to execute a `RENAME` operation instead for both the upgrade and downgrade scripts.

So, let's get into the weeds. What exactly needs to happen to get `alembic` to automatically create these revisions? Take a look at `/src/models.py`. What you will see there is a set of `sqlalchemy` objects defined using the ORM 'declarative base' syntax. The file `/alembic/env.py` has been edited after initialisation to import this code, allowing it to determine what the schema ought to look like.

The other side of the coin is that `alembic` also needs to be able to execute the changes. To make this happen, `alembic.ini` was modified to point the `sqlalchemy.url` variable at the `postgres` database we're running.

It's worth saying that this is the only reason our `docker-compose.yml` had to expose the database on localhost - if you look in your `.env` file you'll see that the FastAPI application is connecting to the database over the docker bridge network. That is why the connection string in `alembic.ini` is slightly different to the one in `.env` (and it's also why we have installed two different database driver libraries, `psycopg2` and `asyncpg`).

### New database revisions

If you make changes to the contents of `src/models.py`, then create an alembic revision (possibly modifying the automatically generated scripts), then update the database to the latest version, you will:

- be able to commit the code changes using Git as normal
- be able to also commit the code to bring the SQL database schema up-to-date
- actually bring the SQL database schema up-to-date on your local development database (to check the code works!)

The FastAPI app
---------------

FastAPI is a popular, performant, modern API framework for Python that brings the benefits of concurrency (`async`) to Python web applications.

This is a very simple application, since this project is not a FastAPI demonstration. It is not an example of best practices. The application defines an endpoint `/countries` and contains some demonstration code. You can use the application to interact with the database as follows:

- Visit `http://localhost:8765/country/GB` in the browser - you should get ... nothing
- Execute `curl -X POST http://localhost:8765/country` - this will create a new database record in the country table (the route doesn't allow customisation of this record, but in a real application it would, of course).
- Visit `http://localhost:8765/country/GB` in the browser - this retrieves the record you created in the first step


When you're done
----------------

The command `docker-compose down --volumes` will remove the database and the volumes it uses for persistent storage.

If you instead execute `docker-compose down` then the next time you run `docker-compose up` the database will be in the state in which you left it.
