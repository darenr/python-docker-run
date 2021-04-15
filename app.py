from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse

from starlette.routing import Route

import docker
import asyncio

client = docker.from_env()



async def container_log_output(container):
    for line in container.logs(stream=True):
        yield line.decode('utf-8').strip() + "\n"

async def list_containers(request):
    results = []
    for container in client.containers.list():
        results.append(container.short_id)

    return JSONResponse(results)

async def run_container(request):
    container = client.containers.run(
        "iris-model:latest",
        environment = {
            'SOURCE_DATA_CSV': 'iris.csv',
            'DEST_ARTIFACT': 'out.joblib'
        },
        detach=True)
    return StreamingResponse(container_log_output(container), media_type='text/plain')


app = Starlette(debug=True, routes=[
    Route('/containers', list_containers),
    Route('/job', run_container),

])
