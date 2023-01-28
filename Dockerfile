# See
# Document docker poetry best practices
# https://github.com/python-poetry/poetry/discussions/1879


# `python-base` sets up all our shared environment variables
FROM python:3.11.1-slim as python-base
# slim => sh and no bash

#
# python
#

# python output is sent straight to terminal without being first buffered
ENV PYTHONUNBUFFERED=1

# prevents python creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

#
# pip
#

# keep docker image as small as possible
ENV PIP_NO_CACHE_DIR=off

# suppress pip upgrade warning
ENV PIP_DISABLE_PIP_VERSION_CHECK=on

# mitigate ReadTimeoutError
ENV PIP_DEFAULT_TIMEOUT=100

#
# poetry
# see:
# https://python-poetry.org/docs/configuration/
#

ENV POETRY_VERSION=1.3.0

ENV POETRY_HOME="/opt/poetry"

# the virtualenv will be created and expected in a folder named .venv
# within the root directory of the project.
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# do not ask any interactive question
ENV POETRY_NO_INTERACTION=1

#
# bespoke
#

# this is where our requirements + virtual environment will live
ENV PYSETUP_PATH="/opt/pysetup"
ENV VENV_PATH="/opt/pysetup/.venv"


ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

################################################################################
################################################################################

# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base as builder-base

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install  --no-root --no-dev


################################################################################
################################################################################

# docker build --target development --tag image:tag .

# `development` image is used during test
FROM python-base as test

ENV FASTAPI_ENV=development

WORKDIR $PYSETUP_PATH

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # vi for dev editing
        vim \
        tree

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN poetry install --no-root

COPY . /opt/src
WORKDIR /opt/src
ENV PYTHONPATH="/opt/src"

RUN echo 'alias ls="ls -aFC --color"' >> ~/.bashrc

CMD sleep 86400

################################################################################
################################################################################

# `development` image is used during development
FROM python-base as development

ENV FASTAPI_ENV=development

WORKDIR $PYSETUP_PATH

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # vi for dev editing
        vim \
        tree \
        # ping, nc, ifconfig for network sleuthing
        iputils-ping \
        netcat \
        net-tools

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN poetry install --no-root

COPY . /opt/src
WORKDIR /opt/src
ENV PYTHONPATH="/opt/src"

RUN echo 'alias ls="ls -aFC --color"' >> ~/.bashrc

EXPOSE 8000
# CMD sleep 86400
CMD uvicorn --host 0.0.0.0 --reload --log-level debug main:app
