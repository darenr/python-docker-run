# python-docker-run
Run a docker container and capture in python the stdout/stderr

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
