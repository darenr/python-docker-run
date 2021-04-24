
import subprocess

import docker
import asyncio
import os
import uuid
import json

from jinja2 import Template

from .__version__ import __version__, __cakes__

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

def generate_ocid() -> str:
    return str(uuid.uuid1())


def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2  # copy R bits to X
    os.chmod(path, mode)


def container_log_output(container):
    for line in container.logs(stream=True):
        yield line.decode("utf-8").strip() + "\n"


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
                version=__version__,
            ),
            file=fp,
        )

    make_executable(bash_file)

    result = subprocess.run(["/bin/bash", bash_file], stdout=subprocess.PIPE)

    def script_generator(result):
        yield result.stdout

    return script_generator(result)


def run_container_job(job_ocid, job_spec):

    print(json.dumps(job_spec, indent=2))

    container = client.containers.run(
        **job_spec,
        volumes={f"{os.getcwd()}/tmp/": {"bind": "/tmp", "mode": "rw"}},
        stdout=True,
        stderr=True,
        detach=True,
    )

    return container_log_output(container)


def create_job(runtime, job_spec):
    job_ocid = generate_ocid()

    jobs[job_ocid] = {
        "runtime": runtime,
        "job_spec": json.loads(
            Template(json.dumps(job_spec)).render(
                OCID=job_ocid,
                job_spec=job_spec,
                version=__version__,
            )
        ),
    }

    return job_ocid, 'ACCEPTED'

def run_job(job_ocid: str):

    if not job_ocid in jobs:
        raise ValueError(f"Job {job_ocid} not found")

    job = jobs[job_ocid]

    if job['runtime'] == "container":
        return run_container_job(job_ocid, job['job_spec'])
    elif job['runtime'] == "python":
        return run_script_in_existing_environment(job_ocid, job['job_spec'])
    else:
        raise ValueError(f"Job {job_ocid} found, but not driver for \"{job['runtime']}\" runtime")
