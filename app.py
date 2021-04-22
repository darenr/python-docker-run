from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse

from starlette.routing import Route

import subprocess

import docker
import asyncio
import os
import uuid
import json

from jinja2 import Template

bash_runner_template = """
#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate "{{ conda_environment }}"

{% for e in environment_variables %}
export {{e[0]}}="{{e[1]}}"
{% endfor %}

python - <<'EOF'
{{ script | safe }}
'EOF'

"""


client = docker.from_env()

jobs = {}  # key is ocid, value is job spec


def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2  # copy R bits to X
    os.chmod(path, mode)


def run_script_in_existing_environment(job_ocid, job_spec):

    print(json.dumps(job_spec, indent=2))

    # make bash script
    bash_file = f"{os.getcwd()}/tmp/job-{job_ocid}.sh"
    with open(bash_file, "w") as fp:
        print(
            Template(bash_runner_template).render(
                conda_environment=job_spec["conda_environment"],
                script=job_spec["script"],
                environment_variables=job_spec["environment"].items(),
            ),
            file=fp,
        )

    make_executable(bash_file)

    result = subprocess.run(["/bin/bash", bash_file], stdout=subprocess.PIPE)

    def script_generator(result):
        yield result.stdout

    return StreamingResponse(script_generator(result), media_type="text/plain")


def ocid() -> str:
    return str(uuid.uuid1())


def container_log_output(container):
    for line in container.logs(stream=True):
        yield line.decode("utf-8").strip() + "\n"


def container_job(job_ocid, job_spec):

    print(json.dumps(job_spec, indent=2))

    container = client.containers.run(
        **job_spec,
        volumes={f"{os.getcwd()}/tmp/": {"bind": "/tmp", "mode": "rw"}},
        stdout=True,
        stderr=True,
        detach=True,
    )

    return StreamingResponse(container_log_output(container), media_type="text/plain")


async def create_job(request):
    job_ocid = ocid()

    j = await request.json()

    jobs[job_ocid] = {
        "runtime": j["runtime"],
        "job_spec": json.loads(
            Template(json.dumps(j["job_spec"])).render(
                OCID=job_ocid
            )
        ),
    }

    return JSONResponse({"job_ocid": job_ocid})


async def run_job(request):
    j = await request.json()
    job_ocid = j["job_ocid"]

    if job_ocid in jobs:
        job = jobs[job_ocid]

        runtime = job["runtime"]
        job_spec = job["job_spec"]

        if runtime == "container":
            return container_job(job_ocid, job_spec)
        elif runtime == "script":
            return run_script_in_existing_environment(job_ocid, job_spec)


# fmt: off
app = Starlette(
    debug=True,
    routes=[
        Route('/run_job', run_job),
        Route('/create_job', create_job)
    ]
)
# fmt: on
