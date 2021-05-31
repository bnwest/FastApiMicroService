# FastApiMicroService
Small FastAPi Micro Service

A slightly modified version of a small FastAPI service found here: 
[FastAPI](https://fastapi.tiangolo.com).

## Single Docker Image

### Bootstrapping Poetry

[poetry](https://python-poetry.org) is used to manage python package dependencies.
[poetry](https://python-poetry.org) will be called within the Dockerfile to add python packages to the built Docker image.
[Docker Poetry Best Practice](https://github.com/python-poetry/poetry/discussions/1879) describes a Dockerfile layout which is the basis for the Dockerfile here. 

The base image for the Docker build is `python:3.9.2-slim` which I first pull to get locally:
```bash
$ docker pull python:3.9.2-slim
```

Next, I bash into that pulled image and execute a serious a commands to build the two [poetry](https://python-poetry.org) files needed to manage python packages: `pyproject.toml` and `poetry.lock`.
These commands are exactly the same commands that Dockerfile has and that will be executed each Docker build.
These commands could be run on the host (versus within a running Docker image) but one would need to guarantee the correct python version. 
I find it easier to work within the running Docker image, since in the end poetry must properly work there.
```bash
% export PYTHONUNBUFFERED=1
% export PYTHONDONTWRITEBYTECODE=1
% export PIP_NO_CACHE_DIR=off
% export PIP_DISABLE_PIP_VERSION_CHECK=on
% export PIP_DEFAULT_TIMEOUT=100
% export POETRY_VERSION=1.1.4
% export POETRY_HOME="/opt/poetry"
% export POETRY_VIRTUALENVS_IN_PROJECT=true
% export POETRY_NO_INTERACTION=1
% export PYSETUP_PATH="/opt/pysetup"
% export ENV_PATH="/opt/pysetup/.venv"
% apt-get update
% apt-get install --no-install-recommends -y curl
% apt-get install --no-install-recommends -y  build-essential
% curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
% mkdir $PYSETUP_PATH
% cd $PYSETUP_PATH
% $POETRY_HOME/bin/poetry init
% cat pyproject.toml 
% $POETRY_HOME/bin/poetry install
% cat poetry.lock 
```
The outut of the two `cat` commands can be cut-and-pasted back to the host.

### Building the Development Docker Image

At the repo root, run this command to build a Docker image with proper poetry support:
```bash
$ docker build --target development --tag fastapi:dev .
```
To bash into this image:
```bash
$ docker run -it --entrypoint /bin/bash fastapi:dev
```
Within the running, start `uvicorn` via
```bash
root@92012bb99cc4:/opt/src# uvicorn main:app --host 0.0.0.0 --reload  --log-level debug
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [13] using statreload
INFO:     Started server process [15]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```
For the reason that I used `0.0.0.0` as the host IP, see (Connection refused? Docker networking and how it impacts your image)[https://pythonspeed.com/articles/docker-connection-refused/].
The takeaways from that article are:
1. By default, containers run in their own network namespaces, with their own IP addresses.
2. docker run -p 5000:5000 will forward from all interfaces in the main network namespace 
(or more accurately, the one where the Docker daemon is running) to the external IP in the container.
3. You therefore need to listen on the external IP inside the container, and the easiest way to do that 
is by listening on all interfaces: 0.0.0.0.

### Check the Network Plumbing

While inside the running Docker image, run the a set of commands as a networking sanity check.
First you must bash into the running image from another xterm:
```bash
$ docker ps
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS         PORTS      NAMES
4b626d048f95   fastapi:dev   "/bin/sh -c 'uvicorn…"   6 seconds ago   Up 5 seconds   8000/tcp   intelligent_almeida

# use the NAME of the running image
$ docker exec -it intelligent_almeida bash
```
Once with the running Docker image, run the following commands:
```bash
root@92012bb99cc4:/opt/src# ping 127.0.0.1
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.097 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.047 ms
64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.043 ms
64 bytes from 127.0.0.1: icmp_seq=4 ttl=64 time=0.053 ms
64 bytes from 127.0.0.1: icmp_seq=5 ttl=64 time=0.065 ms
64 bytes from 127.0.0.1: icmp_seq=6 ttl=64 time=0.233 ms
^C
--- 127.0.0.1 ping statistics ---
6 packets transmitted, 6 received, 0% packet loss, time 151ms
rtt min/avg/max/mdev = 0.043/0.089/0.233/0.067 ms

# netcat utility
root@92012bb99cc4:/opt/src# nc -vz 127.0.0.1 8000
localhost [127.0.0.1] 8000 (?) open

root@4b626d048f95:/opt/src# nc -vz 0.0.0.0 8000
0.0.0.0: inverse host lookup failed: Unknown host
(UNKNOWN) [0.0.0.0] 8000 (?) open
```
The `open` status implies that someone (i.e. uvicorn) is listening to the 8000 port, a very good and necessary thing.

### Testing a FastAPI endpoint
After the netwrok santity check and sill at the bash prompt within the running Docker image, run a set of python statements within `ipython` to programmatically tests an endpoint:
```bash
root@4b626d048f95:/opt/src# ipython
Python 3.9.2 (default, Mar 12 2021, 19:04:51) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.21.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import requests
   ...: FASTAPI_ROOT = u"http://127.0.0.1:8000"
   ...: endpoint_url = f"{FASTAPI_ROOT}/"
   ...: response = requests.get(endpoint_url, timeout=15)
   ...: response.json()
   ...: 
Out[1]: {'Hello': 'World'}
```

### Testing a FastAPI Endpoint in the Host's Browser

If needed, exiting out of any running Dcoker images.

Start the Docker image with a port forwarded via
```bash
# Map the internal port tot he external port via convention <host port>:<docker image port>
$ docker run -it  --publish 8000:8000 fastapi:dev
```

Open a host browser and type in the following URLs:
```bash
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
http://127.0.0.1:8000/items/42
http://127.0.0.1:8000/items/42?q=5a920c4c-03d2-422e-b863-ce8126d35ff2
```
The `/docs` endpoint displays the OpenAPI documentation.
Each endpoint, once selected, can be tested by clicking the "Try it out" button.

### Manually run the System Tests

With the service running, bash into the running docker image:
```bash
$ docker ps
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS         PORTS      NAMES
4b626d048f95   fastapi:dev   "/bin/sh -c 'uvicorn…"   6 seconds ago   Up 5 seconds   8000/tcp   pensive_swanson

$ docker exec -it pensive_swanson bash
```
Run `pytest from the command line:
```bash
$ export FASTAPI_ROOT="http://127.0.0.1:8000"

$ pytest -vv tests/system/test_hello.py
================================================== test session starts ==================================================
platform linux -- Python 3.9.2, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /opt/pysetup/.venv/bin/python
cachedir: .pytest_cache
rootdir: /opt/src
plugins: asyncio-0.14.0
collected 1 item                                                                                                        

tests/system/test_hello.py::test_hello_world PASSED                                                               [100%]

=================================================== 1 passed in 0.16s ===================================================
```

## Docker-Compose

After doing the above work, the Docker build and image should be in good shape.

Docker compose simplifies running and testing, since the `docker-compose` file takes care of port mapping, setting up enviroment variable and running multiple images at once.

To build the necessary Docker images, run the following commands which the service image and the system test image:
```bash
$ docker-compose build fastapi-micro-service
$ docker-compose build system-test
```
To start the FastAPI service run:
```bash
$ docker-compose up fastapi-micro-service
fastapi-micro-service_1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
fastapi-micro-service_1  | INFO:     Started reloader process [1] using statreload
fastapi-micro-service_1  | INFO:     Started server process [8]
fastapi-micro-service_1  | INFO:     Waiting for application startup.
fastapi-micro-service_1  | INFO:     Application startup complete.
```
In a second xterm, you check the status of the above via:
```bash
$ docker-compose ps
                   Name                                  Command               State            Ports          
---------------------------------------------------------------------------------------------------------------
fastapimicroservice_fastapi-micro-service_1   uvicorn --host 0.0.0.0 --r ...   Up      127.0.0.1:8000->8000/tcp
```
In a second xterm, you can run the systems test(s) via:
```bash
$ docker-compose up system-test
Docker Compose is now in the Docker CLI, try `docker compose up`

fastapimicroservice_fastapi-micro-service_1 is up-to-date
Creating fastapimicroservice_system-test_1 ... done
Attaching to fastapimicroservice_system-test_1
system-test_1            | ============================= test session starts ==============================
system-test_1            | platform linux -- Python 3.9.2, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /opt/pysetup/.venv/bin/python
system-test_1            | cachedir: .pytest_cache
system-test_1            | rootdir: /opt/src
system-test_1            | plugins: asyncio-0.14.0
system-test_1            | collecting ... collected 1 item
system-test_1            | 
system-test_1            | tests/system/test_hello.py::test_hello_world PASSED                      [100%]
system-test_1            | 
system-test_1            | ============================== 1 passed in 0.25s ===============================
fastapimicroservice_system-test_1 exited with code 0
```

In a second xterm, you can manually run the systems test(s) via:

```bash
$ docker-compose exec system-test bash

$ docker-compose run system-test bash
Creating fastapimicroservice_system-test_run ... done
root@d1f861e0e5f1:/opt/src# pytest -vv tests/system/
================================================== test session starts ==================================================
platform linux -- Python 3.9.2, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /opt/pysetup/.venv/bin/python
cachedir: .pytest_cache
rootdir: /opt/src
plugins: asyncio-0.14.0
collected 1 item                                                                                                        

tests/system/test_hello.py::test_hello_world PASSED                                                               [100%]

=================================================== 1 passed in 0.17s ===================================================
```

To tear it all down, run:
```bash
$ docker-compose down
```

## Kubernetes + Helm

