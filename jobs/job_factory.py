import requests
import os

from typing import List, Set, Dict, Tuple, Optional, Type

__SECRET__ = object()

url_base = "http://localhost:8000"


class Job:

    ENGINE_TYPE_ODSC = "odsc"
    ENGINE_RUNTIME_CONTAINER = "container"
    ENGINE_RUNTIME_PYTHON = "python"
    ENGINE_RUNTIME_DATAFLOW = "dataflow"

    class ContainerRuntime:

        def __init__(self, parent_job):
            self.parent_job = parent_job
            self.runtime_image = None
            self.runtime_config = {}

        def image(self, image: str):
            self.runtime_image = image
            return self.parent_job

        def config(self, runtime_config: Dict):
            self.runtime_config = runtime_config
            return self.parent_job

        def _job_spec(self):

            assert self.runtime_image

            job_spec = {
                "image": self.runtime_image
            }

            return {**job_spec, **self.runtime_config}  # merge dicts

        def __repr__(self) -> str:
            return f"ContainerRuntime:: {self.runtime_image}"

    class PythonRuntime:

        def __init__(self, parent_job):
            self.parent_job = parent_job
            self.script_name = None
            self.conda_name = None
            self.runtime_config = {}

        def script_from_string(self, script_block: str):
            self.script = script_block

        def script_from_file(self, script_filename: str):
            with open(script_filename, "r") as fin:
                self.script = fin.read()

            return self.parent_job

        def conda(self, conda_name: str):
            self.conda_name = conda_name
            return self.parent_job

        def config(self, runtime_config: Dict):
            self.runtime_config = runtime_config
            return self.parent_job

        def _job_spec(self):

            return {"conda_environment": self.conda_name, "script": self.script}

        def __repr__(self) -> str:
            return f"PythonRuntime:: {self.script_name}::{self.conda_name}"

    def __init__(self, engine: str, runtime_type: str, secret):

        if secret != __SECRET__:
            raise ValueError("Use `create_(container|python|dataflow)_job` instead.")
        else:
            self.engine = engine
            self.runtime_type = runtime_type
            self.job_environment = {}

            if runtime_type == Job.ENGINE_RUNTIME_CONTAINER:
                self.job_runtime = Job.ContainerRuntime(self)
            elif runtime_type == Job.ENGINE_RUNTIME_PYTHON:
                self.job_runtime = Job.PythonRuntime(self)
            else:
                raise ValueError(
                    f"Runtime [{runtime_type}] not yet supported"
                )

        self.job_ocid = -1

    def __repr__(self) -> str:
        return f"JOB:: [{self.job_ocid}] {self.engine}::{self.job_runtime}"

    @property
    def runtime(self):
        return self.job_runtime

    def environment(self, env: Dict):
        self.job_environment = env
        return self

    def console(self):
        return JobConsole(self.job_ocid)

    def build(self):

        job_spec = self.runtime._job_spec()
        job_spec["environment"] = self.job_environment

        result = requests.get(
            f"{url_base}/create_job",
            json={"runtime": self.runtime_type, "job_spec": job_spec},
        )

        self.job_ocid = result.json()["job_ocid"]

        return self

    def run(self):

        return JobConsole(
            requests.get(f"{url_base}/run_job", json={"job_ocid": self.job_ocid})
        )

    @classmethod
    def create_container_job(self, engine: str):
        return Job(engine, Job.ENGINE_RUNTIME_CONTAINER, secret=__SECRET__)

    @classmethod
    def create_python_job(self, engine: str):
        return Job(engine, Job.ENGINE_RUNTIME_PYTHON, secret=__SECRET__)

    @classmethod
    def create_dataflow_job(self, engine: str):
        return Job(engine, Job.ENGINE_RUNTIME_DATAFLOW, secret=__SECRET__)


class JobConsole:
    def __init__(self, r):
        self.r = r

    def watch(self):
        if self.r.status_code == requests.codes.ok:
            for line in self.r.content.splitlines():
                print(line.decode("utf-8").strip())
        else:
            self.r.raise_for_status()
