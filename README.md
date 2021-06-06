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
# will be given a chance to add python packages, one at a time.
# packages can later be add via "poetry add <package>".
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
For the reason that I used `0.0.0.0` as the host IP, see [Connection refused Docker networking and how it impacts your image](https://pythonspeed.com/articles/docker-connection-refused/).
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
Once within the running Docker image, run the following commands:
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
The netcat `open` status implies that someone (i.e. uvicorn) is listening to the 8000 port, a very good and necessary thing.

### Testing a FastAPI endpoint
After the network santity check and sill at the bash prompt within the running Docker image, run a set of python statements within `ipython` to programmatically tests an endpoint:
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

If needed, exit out of any running Dcoker images.

Start the Docker image with a port forwarded via
```bash
# Map the internal port to the external port via convention <host port>:<docker image port>
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
Each endpoint therein, once selected, can be tested by clicking the "Try it out" button.

### Manually run the System Tests

With the service running, bash into the running docker image:
```bash
$ docker ps
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS         PORTS      NAMES
4b626d048f95   fastapi:dev   "/bin/sh -c 'uvicorn…"   6 seconds ago   Up 5 seconds   8000/tcp   pensive_swanson

$ docker exec -it pensive_swanson bash
```
Run `pytest` from the command line:
```bash
root@9acfbfcaf811:/opt/src# export FASTAPI_ROOT="http://127.0.0.1:8000"

root@9acfbfcaf811:/opt/src# pytest -vv tests/system/test_hello.py
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

Docker compose simplifies running and testing, since the `docker-compose.yaml` file takes care of port mapping, setting up enviroment variable and running multiple images at once.

To build the necessary Docker images, run the following commands which builds the service image and the system test image:
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

In a second xterm, you can bash into the running image and manually run the systems test(s) via:

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

This was my initial attempt to get this FastAPI service running in Kubernetes via helm.

I used the Kubernetes packaged with [Docker Desktop for Mac
](https://hub.docker.com/editions/community/docker-ce-desktop-mac).
Kubernetes will need to enable in the Settings.
If your Kubernetes is configured elsewhere on the host, you will need to select `docker-desktop` from the Kubernetes menu.
The following commands will verify that you have the right Kubernetes node:
```bash
$ kubectl config get-contexts

$ kubectl config current-context
docker-desktop

$ kubectl get nodes
NAME             STATUS   ROLES    AGE     VERSION
docker-desktop   Ready    master   7m50s   v1.19.7
```
The following link may assist in getting Kubernetes to work on the Mac: [Using Kubernetes with Docker for Mac](https://logz.io/blog/kubernetes-docker-mac/). 

The following link may assist in getting Kubernetes and helm working with a FastAPI service: [Simple chart with helm](https://bartek-blog.github.io/kubernetes/helm/python/fastapi/2020/12/13/helm.html).

The work below may also work with the host's [minikube](https://minikube.sigs.k8s.io/docs/) Kubernetes.  I did not try it.

To setup the initial helm charts, I did the following commands from the repo root:
```bash
$ mkdir charts

$ cd charts

$ helm create fastapi-service

$ tree
.
└── fastapi-service
    ├── Chart.yaml
    ├── charts
    ├── templates
    │   ├── NOTES.txt
    │   ├── _helpers.tpl
    │   ├── deployment.yaml
    │   ├── hpa.yaml
    │   ├── ingress.yaml
    │   ├── service.yaml
    │   ├── serviceaccount.yaml
    │   └── tests
    │       └── test-connection.yaml
    └── values.yaml

$ helm lint
==> Linting .
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```
The above yaml files are parameterized manifest files which when filled in are used as the input that Kubernetes (via `kubectl`) requires.

The above helm chart files need to be modified. 
In particular, I needed to switch the executable Docker image to the one we built with Docker.
The pull policy also needed to be changed.
Helm/Kubernetes by default wants to find/pull its images non-locally in the docker register.
To force Helm/Kubernetes to find the image locally, the `pullPolicy` needs to be set to `Never`.  See [Kubernetes Documentation: Configuration Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/):
```bash
imagePullPolicy: Never: the image is assumed to exist locally. No attempt is made to pull the image.
```

To see how the helm paramaterized yaml files will expanded. do the following:
```bash
$ cd charts  # if needed

$ helm install --debug --dry-run my-release fastapi-service
```
The image and pull policy can then be manually verified, if you like.

To start the FastAPI service in Kubernetes, do the following:
```bash
$ cd charts  # if needed

$ helm install my-release fastapi-service
NAME: my-release
LAST DEPLOYED: Mon May 31 15:13:54 2021
NAMESPACE: default
STATUS: deployed
REVISION: 1
NOTES:
1. Get the application URL by running these commands:
  export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=fastapi-service,app.kubernetes.io/instance=my-release" -o jsonpath="{.items[0].metadata.name}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace default port-forward $POD_NAME 8080:80

$ helm list
NAME      	NAMESPACE	REVISION	UPDATED                             	STATUS  	CHART                	APP VERSION
my-release	default  	1       	2021-05-31 15:13:54.677062 -0400 EDT	deployed	fastapi-service-0.1.0	1.16.0     

# to see what Kubernetes has got going:
$ kubectl get all
NAME                                              READY   STATUS    RESTARTS   AGE
pod/my-release-fastapi-service-7f778f65f4-jhb27   1/1     Running   0          2m6s

NAME                                 TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
service/kubernetes                   ClusterIP   10.96.0.1        <none>        443/TCP    24h
service/my-release-fastapi-service   ClusterIP   10.102.117.206   <none>        8000/TCP   2m6s

NAME                                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/my-release-fastapi-service   1/1     1            1           2m6s

NAME                                                    DESIRED   CURRENT   READY   AGE
replicaset.apps/my-release-fastapi-service-7f778f65f4   1         1         1       2m6s

# to see the uvigorn logs (the GETs you see in the logs is a health check that Kubernetes is periodically calling):
$ kubectl logs pod/my-release-fastapi-service-7f778f65f4-jhb27
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [7] using statreload
INFO:     Started server process [9]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     10.1.0.1:60850 - "GET / HTTP/1.1" 200 OK
INFO:     10.1.0.1:60858 - "GET / HTTP/1.1" 200 OK
...

# to port forward so that the host browser can hit the FastAPI endpoints:
$ kubectl port-forward service/my-release-fastapi-service 8000:8000
Forwarding from 127.0.0.1:8000 -> 8000
Forwarding from [::1]:8000 -> 8000
Handling connection for 8000
...
```

To exercise the FastAPI service endpoint go to the host browser and enter the following URLs:
```bash
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
http://127.0.0.1:8000/items/42
http://127.0.0.1:8000/items/42?q=5a920c4c-03d2-422e-b863-ce8126d35ff2
```

To tear it all down:
```bash
$ helm list
NAME      	NAMESPACE	REVISION	UPDATED                             	STATUS  	CHART                	APP VERSION
my-release	default  	1       	2021-05-31 15:13:54.677062 -0400 EDT	deployed	fastapi-service-0.1.0	1.16.0     

$ helm delete my-release
release "my-release" uninstalled
```

### Running Helm Tests

`helm create` creates one test, test-connection, found here:
```bash
charts/fastapi-service/templates/tests/test-connection.yaml
```
This test can be run via
```bash
$ helm install my-release fastapi-service

$ helm test my-release
```
I added an additional tests to the same directory, `test-system.yaml`, which ran the pytest system tests that I created.
Internally, the job defnition for the test needs to contain one of the helm test hook annotations, like 
```bash
  annotations:
    "helm.sh/hook": test-success
```
For more on running test within helm, see [Chart Tests](https://helm.sh/docs/topics/chart_tests/).

Running all of tests:
```bash
$ helm test my-release
Pod my-release-fastapi-service-test-connection pending
Pod my-release-fastapi-service-test-connection pending
Pod my-release-fastapi-service-test-connection pending
Pod my-release-fastapi-service-test-connection succeeded
Pod my-release-fastapi-service-test-system pending
Pod my-release-fastapi-service-test-system pending
Pod my-release-fastapi-service-test-system pending
Pod my-release-fastapi-service-test-system running
Pod my-release-fastapi-service-test-system succeeded
NAME: my-release
LAST DEPLOYED: Sat Jun  5 12:07:32 2021
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE:     my-release-fastapi-service-test-connection
Last Started:   Sat Jun  5 12:08:32 2021
Last Completed: Sat Jun  5 12:08:36 2021
Phase:          Succeeded
TEST SUITE:     my-release-fastapi-service-test-system
Last Started:   Sat Jun  5 12:08:36 2021
Last Completed: Sat Jun  5 12:08:41 2021
Phase:          Succeeded
```
The test output can be manually be checked via `kubectl logs <test pod>`.

## Load Test

I implemented a small load test via [k6](https://k6.io/).
None of the endpoints actually have much of a load, so this is just an example of how to write a simple load test with [k6](https://k6.io/).

To build the load test docker image:
```bash
docker-compose build load-test
```

To run the load test:
```bash
$ docker-compose up load-test
```
which is equivalent to running:
```bash
$ docker-compose run load-test --verbose run /opt/load/load.js --vus 4 --iterations 1000
```
The load test will manage four processes (`--vus 4`) and will hit the root endpoint 1000 times (`--iterations 20`), giving each process 250 endpoint accesses.

[k6](https://k6.io/) will produce the following output:
```bash
DEBU[0000] Logger format: TEXT                          
DEBU[0000] k6 version: v0.30.0 (2021-01-20T13:14:28+0000/2193de0, go1.15.7, linux/amd64) 

          /\      |‾‾| /‾‾/   /‾‾/   
     /\  /  \     |  |/  /   /  /    
    /  \/    \    |     (   /   ‾‾\  
   /          \   |  |\  \ |  (‾)  | 
  / __________ \  |__| \__\ \_____/ .io

DEBU[0000] Initializing the runner...                   
DEBU[0000] Loading...                                    moduleSpecifier="file:///opt/load/load.js" originalModuleSpecifier=/opt/load/load.js
DEBU[0000] Babel: Transformed                            t=144.778313ms
DEBU[0000] Loading...                                    moduleSpecifier="https://jslib.k6.io/k6-utils/1.0.0/index.js" originalModuleSpecifier="https://jslib.k6.io/k6-utils/1.0.0/index.js"
DEBU[0000] Fetching source...                            url="https://jslib.k6.io/k6-utils/1.0.0/index.js?_k6=1"
DEBU[0001] Fetched!                                      len=653 t=411.225578ms url="https://jslib.k6.io/k6-utils/1.0.0/index.js?_k6=1"
DEBU[0001] Babel: Transformed                            t=143.174648ms
DEBU[0001] Getting the script options...                
DEBU[0001] Initializing the execution scheduler...      
  execution: local
     script: /opt/load/load.js
     output: -

  scenarios: (100.00%) 1 scenario, 4 max VUs, 10m30s max duration (incl. graceful stop):
           * default: 1000 iterations shared among 4 VUs (maxDuration: 10m0s, gracefulStop: 30s)

DEBU[0001] Starting the REST API server on localhost:6565 
DEBU[0001] Initialization starting...                    component=engine
DEBU[0001] Start of initialization                       executorsCount=1 neededVUs=4 phase=local-execution-scheduler-init
DEBU[0001] Initialized VU #2                             phase=local-execution-scheduler-init
DEBU[0001] Initialized VU #1                             phase=local-execution-scheduler-init
DEBU[0001] Initialized VU #4                             phase=local-execution-scheduler-init
DEBU[0001] Initialized VU #3                             phase=local-execution-scheduler-init
DEBU[0001] Finished initializing needed VUs, start initializing executors...  phase=local-execution-scheduler-init
DEBU[0001] Initialized executor default                  phase=local-execution-scheduler-init
DEBU[0001] Initialization completed                      phase=local-execution-scheduler-init
DEBU[0001] Execution scheduler starting...               component=engine
DEBU[0001] Start of test run                             executorsCount=1 phase=local-execution-scheduler-run
DEBU[0001] Running setup()                               phase=local-execution-scheduler-run
DEBU[0001] Starting emission of VU metrics...            component=engine
DEBU[0001] Metrics processing started...                 component=engine
DEBU[0001] Start all executors...                        phase=local-execution-scheduler-run
DEBU[0001] Starting executor                             executor=default startTime=0s type=shared-iterations
DEBU[0001] Starting executor run...                      executor=shared-iterations iterations=1000 maxDuration=10m0s scenario=default type=shared-iterations vus=4
DEBU[0005] Executor finished successfully                executor=default startTime=0s type=shared-iterations
DEBU[0005] Running teardown()                            phase=local-execution-scheduler-run
DEBU[0005] Regular duration is done, waiting for iterations to gracefully finish  executor=shared-iterations gracefulStop=30s scenario=default
DEBU[0005] Execution scheduler terminated                component=engine error="<nil>"
DEBU[0005] Processing metrics and thresholds after the test run has ended...  component=engine
DEBU[0005] Engine run terminated cleanly                

running (00m03.9s), 0/4 VUs, 1000 complete and 0 interrupted iterations
default ✓ [======================================] 4 VUs  00m03.8s/10m0s  1000/1000 shared iters
DEBU[0005] Engine: Thresholds terminated                 component=engine
DEBU[0005] run: execution scheduler terminated           component=engine
DEBU[0005] Metrics emission terminated                   component=engine

     █ GET

       ✓ status is 200

     checks.....................: 100.00% ✓ 1000 ✗ 0  
     data_received..............: 200 kB  52 kB/s
     data_sent..................: 100 kB  26 kB/s
     group_duration.............: avg=15.23ms min=985.43µs med=1.91ms   max=47.97ms  p(90)=42.81ms p(95)=43.3ms 
     http_req_blocked...........: avg=18.35µs min=1.46µs   med=2.75µs   max=3.92ms   p(90)=4.29µs  p(95)=5.45µs 
     http_req_connecting........: avg=681ns   min=0s       med=0s       max=229.23µs p(90)=0s      p(95)=0s     
     http_req_duration..........: avg=15.04ms min=885.25µs med=1.73ms   max=47.83ms  p(90)=42.64ms p(95)=43.13ms
     http_req_receiving.........: avg=13.56ms min=25.55µs  med=182.81µs max=45.3ms   p(90)=41.06ms p(95)=41.37ms
     http_req_sending...........: avg=22.36µs min=7.31µs   med=13.94µs  max=1.65ms   p(90)=41.44µs p(95)=54.27µs
     http_req_tls_handshaking...: avg=0s      min=0s       med=0s       max=0s       p(90)=0s      p(95)=0s     
     http_req_waiting...........: avg=1.45ms  min=712.88µs med=1.17ms   max=7.26ms   p(90)=2.48ms  p(95)=3.06ms 
     http_reqs..................: 1000    259.182468/s
     iteration_duration.........: avg=15.25ms min=995.85µs med=1.94ms   max=48.05ms  p(90)=42.83ms p(95)=43.32ms
     iterations.................: 1000    259.182468/s
     vus........................: 4       min=4  max=4
     vus_max....................: 4       min=4  max=4

DEBU[0005] Waiting for engine processes to finish...    
DEBU[0005] Metrics processing winding down...            component=engine
DEBU[0005] Everything has finished, exiting k6!         
```
