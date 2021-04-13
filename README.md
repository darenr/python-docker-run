# python-docker-run
Run a docker container and capture in python the stdout/stderr

## Development

```bash
conda create -y --name dockerrunner python=3.7
conda activate dockerrunner

pip install -r requirements.txt -U
```

# Docker

- build:

  ```bash
  docker build -f Dockerfile -t iris-model:latest .
  ```

- test:

  ```bash
    docker run -e iris.csv iris-model:latest
  ```
