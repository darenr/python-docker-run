# python-docker-run
Run a docker container and capture in python the stdout/stderr from a
Starlette asynch app. The server takes in a job spec and runs the
job in a container and streams the container's output to the caller

uses: https://github.com/docker/docker-py

## Development

You can pick Python 3.7/3.8 or 3.9, this is independent of the jobs runtime

```bash
conda create -y --name dockerrunner python=3.8
conda activate dockerrunner

pip install -r requirements.txt -U
```

## Docker

`cd example_docker_train`

- build:

  ```bash
  make build
  ```

- test:

  ```bash
    make test
  ```

## Run the server

`./run.sh`

or

`uvicorn --reload app:app`

## TESTS

start web app: `./run.sh`

`python -m pytest -v tests`

*OR* to not run the web app and skip remote tests:

`python -m pytest -v tests -k 'not remote'``

## TODO

  - ~~break up API:~~
    - ~~job creation (takes in job spec, returns ID)~~
    - ~~job run (takes in ID, streams output)~~
  - ~~write client API code~~
  - demo client API code in Jupyter Lab
