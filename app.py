from starlette.applications import Starlette
from starlette.responses import (
    JSONResponse,
    StreamingResponse
)

from starlette.routing import Route

import docker
import asyncio
import os
import uuid

client = docker.from_env()


def ocid() -> str:
    return str(uuid.uuid1())


async def container_log_output(container):
    yield 'Output:\n'

    for line in container.logs(stream=True):
        yield line.decode('utf-8').strip() + '\n'


async def list_containers(request):
    results = []
    for container in client.containers.list():
        results.append(container.short_id)

    return JSONResponse(results)


async def run_hello_world(request):

    container = client.containers.run(
        image='hello-world',
        detach=True
    )

    return StreamingResponse(
        container_log_output(container),
        media_type='text/plain'
    )


async def run_container(request):
    job_ocid = ocid()

    job_spec = {
        'container': "train-model:latest",
        'env': {
            'TARGET_VARIABLE': f'variety',
            'TRAINING_KERNEL': f'poly',  # linear/poly/rbf/sigmoid/precomputed
            'SOURCE_DATA_CSV': f'https://raw.githubusercontent.com/darenr/public_datasets/master/iris_dataset.csv',
            'DEST_ARTIFACT':   f'/mnt/tmp/model-{job_ocid}.joblib'
        }
    }

    container = client.containers.run(
        image=job_spec['container'],
        volumes={
            f'{os.getcwd()}/tmp/': {
                'bind': '/mnt/tmp',
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
        Route('/containers', list_containers),
        Route('/job', run_container),
        Route('/hello', run_hello_world),
    ]
)
