# python-docker-run
Run a docker container and capture in python the stdout/stderr from a
Starlette asynch app. The server takes in a job spec and runs the
job in a container and streams the container's output to the caller

uses: https://github.com/docker/docker-py

## Development

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

## TODO

  - break up API:
    - job creation (takes in job spec, returns ID)
    - job run (takes in ID, streams output)
  - write client API code
  - demo client API code in Jupyter Lab
