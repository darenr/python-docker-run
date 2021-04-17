from starlette.applications import Starlette
from starlette.responses import (
    JSONResponse,
    StreamingResponse
)

from starlette.routing import Route

import subprocess
import tempfile

import docker
import asyncio
import os
import uuid

from jinja2 import Template

bash_runner_template = '''
#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate "{{ conda_environment }}"

{% for e in environment_variables %}
export {{e[0]}}="{{e[1]}}"
{% endfor %}

python - <<'EOF'
{{ script | safe }}
'EOF'

'''


client = docker.from_env()

def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

async def run_script_in_existing_environment(request):
    job_ocid = ocid()

    job_spec = {
        'conda_environment': "pyk8s",
        'script': open('example_scripts/ex1_script.py').read(),
        'env': {
            'MODULES': 'flask joblib scipy'
        }
    }

    # make bash script
    bash_file = f'{os.getcwd()}/tmp/job-{job_ocid}.sh'
    with open(bash_file, "w") as fp:
        print(Template(bash_runner_template).render(
            conda_environment=job_spec['conda_environment'],
            script=job_spec['script'],
            environment_variables=job_spec['env'].items(),
        ), file=fp)

    make_executable(bash_file)

    result = subprocess.run(
        ['/bin/bash', bash_file],
        stdout=subprocess.PIPE
    )

    def script_generator(result):
        yield result.stdout

    return StreamingResponse(
        script_generator(result),
        media_type='text/plain'
    )

async def run_script_in_new_environment(request):
    job_ocid = ocid()

    # conda create --name environmentName python=3 pandas numpy



def ocid() -> str:
    return str(uuid.uuid1())


async def container_log_output(container):
    yield 'Output:\n'

    for line in container.logs(stream=True):
        yield line.decode('utf-8').strip() + '\n'


async def run_hello_world(request):

    container = client.containers.run(
        image='hello-world',
        detach=True
    )

    return StreamingResponse(
        container_log_output(container),
        media_type='text/plain'
    )

async def container_job(request):
    job_ocid = ocid()

    job_spec = {
        'container': "train-model:latest",
        'env': {
            'TARGET_VARIABLE': f'variety',
            'TRAINING_KERNEL': f'poly',  # linear/poly/rbf/sigmoid/precomputed
            'SOURCE_DATA_CSV': f'https://raw.githubusercontent.com/darenr/public_datasets/master/iris_dataset.csv',
            'DEST_ARTIFACT':   f'/tmp/model-{job_ocid}.joblib'
        }
    }

    container = client.containers.run(
        image=job_spec['container'],
        volumes={
            f'{os.getcwd()}/tmp/': {
                'bind': '/tmp',
                'mode': 'rw'
            }
        },
        environment=job_spec['env'],
        stdout=True,
        stderr=True,
        detach=True
    )

    return StreamingResponse(
        container_log_output(container),
        media_type='text/plain'
    )


app = Starlette(
    debug=True,
    routes=[
        Route('/hello', run_hello_world),
        Route('/container_job', container_job),
        Route('/run_script_in_existing_environment', run_script_in_existing_environment),
        Route('/run_script_in_new_environment', run_script_in_new_environment),
    ]
)
