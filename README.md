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

- build:

  ```bash
  docker build -f Dockerfile -t iris-model:latest .
  ```

- test:

  ```bash
    docker run -e iris.csv iris-model:latest
  ```

## Run the runner

python runner.py
