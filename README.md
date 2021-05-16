# python-docker-run
Run a docker container and capture in python the stdout/stderr from a
Starlette asynch app. The server takes in a job spec and runs the
job in a container and streams the container's output to the caller

uses: https://github.com/docker/docker-py

## Development



You can pick Python 3.7/3.8 or 3.9, this is independent of the jobs runtime

```bash
conda env create -f  environment.yml
conda activate dockerrunner
pre-commit install

```

## Pre-commit hooks

By running `pre-commit install` this will install a hook to run a series of hooks
on the changed files. To refresh the tool chain use `pre-commit autoupdate` and
to force run on all files use `pre-commit run --all-files`


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

`python -m pytest -v tests -k 'not remote'`

## To use the PySparkRuntime you need to create a conda env, using

```bash
conda create -y --name pyspark2.4 python=3.7
conda activate pyspark2.4
conda install -y -c conda-forge/label/cf202003 pyspark # Pyspark 2.4.5
```

## TODO

  - ~~break up API:~~
    - ~~job creation (takes in job spec, returns ID)~~
    - ~~job run (takes in ID, streams output)~~
  - ~~write client API code~~
  - demo client API code in Jupyter Lab
