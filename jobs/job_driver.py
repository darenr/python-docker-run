from .__version__ import __version__, __cakes__
from jinja2 import Template
import subprocess

import docker
import asyncio
import os
import uuid
import json
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(processName)s::%(relativeCreated)6d %(threadName)s %(message)s",
)


bash_python_runner_template = """
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

bash_pyspark_runner_template = """
#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate "{{ conda_environment }}"

{% for e in environment_variables %}
export {{e[0]}}="{{e[1]}}"
{% endfor %}

spark-submit "{{script_file | safe}}"

"""

logging.info(f"initializing docker connection...")
client = docker.from_env()


logging.info(f"initializing jobs database...")

jobs = {}  # key is id, value is job spec


def generate_id() -> str:
    return str(uuid.uuid1())


def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2  # copy R bits to X
    os.chmod(path, mode)


def container_log_output(container):
    for line in container.logs(stream=True):
        yield line.decode("utf-8").strip()


def run_script_in_existing_environment(job_id, job_spec):

    # make bash script
    bash_file = f"{os.getcwd()}/tmp/job-{job_id}.sh"
    with open(bash_file, "w") as fp:
        print(
            Template(bash_python_runner_template).render(
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
        yield result.stdout.decode("utf-8").strip()

    return script_generator(result)


def run_pyspark(job_id, job_spec):

    # write script to a file for submitting...
    script_file = f"{os.getcwd()}/tmp/job-{job_id}.py"
    with open(script_file, "w") as fp:
        print(job_spec["script"], file=fp)

    # make bash script
    bash_file = f"{os.getcwd()}/tmp/job-{job_id}.sh"
    with open(bash_file, "w") as fp:
        print(
            Template(bash_pyspark_runner_template).render(
                conda_environment=job_spec["conda_environment"],
                environment_variables=job_spec["environment"].items(),
                version=__version__,
                script_file=script_file,
                job_id=job_id,
            ),
            file=fp,
        )

    make_executable(bash_file)

    result = subprocess.run(["/bin/bash", bash_file], stdout=subprocess.PIPE)

    def script_generator(result):
        yield result.stdout.decode("utf-8").strip()

    return script_generator(result)


def run_container_job(job_id, job_spec):

    container = client.containers.run(
        **job_spec,
        volumes={f"{os.getcwd()}/tmp/": {"bind": "/tmp", "mode": "rw"}},
        stdout=True,
        stderr=True,
        detach=True,
    )

    return container_log_output(container)


def create_job(runtime, job_spec):
    job_id = generate_id()

    logging.info(f"create_job: [{runtime}, id: {job_id}]")

    jobs[job_id] = {
        "runtime": runtime,
        "job_spec": json.loads(
            Template(json.dumps(job_spec)).render(
                id=job_id,
                job_spec=job_spec,
                version=__version__,
            )
        ),
    }

    return job_id


def run_job(job_id: str):

    logging.info(f"run_job: [{job_id}]: {job_id in jobs}")

    if not job_id in jobs:
        raise ValueError(f"Job {job_id} not found")

    job = jobs[job_id]

    if job["runtime"] == "container":
        return run_container_job(job_id, job["job_spec"])
    elif job["runtime"] == "python":
        return run_script_in_existing_environment(job_id, job["job_spec"])
    elif job["runtime"] == "pyspark":
        return run_pyspark(job_id, job["job_spec"])
    else:
        raise ValueError(
            f"Job {job_id} found, but not driver for \"{job['runtime']}\" runtime"
        )
