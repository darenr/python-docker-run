import os

from typing import List, Set, Dict, Tuple, Optional, Type

from .job_driver import create_job as inproc_create_job
from .job_driver import run_job as inproc_run_job

from .client_job import create_job as remote_create_job
from .client_job import run_job as remote_run_job

__SECRET__ = object()


class Job:

    ENGINE_TYPE_INPROC = "inproc"
    ENGINE_TYPE_REMOTE = "remote"
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

        def conda_environment(self, conda_name: str):
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

        if self.engine == Job.ENGINE_TYPE_INPROC:
            self.job_ocid = inproc_create_job(self.runtime_type, job_spec)

        elif self.engine == Job.ENGINE_TYPE_REMOTE:
            self.job_ocid = remote_create_job(self.runtime_type, job_spec)

        else:
            raise ValueError(f"\"{self.engine}\" not supported, use one of: [{ENGINE_TYPE_INPROC}, {ENGINE_TYPE_REMOTE}]")

        return self

    def run(self):

        if self.engine == Job.ENGINE_TYPE_INPROC:
            return InProcJobConsole(
                inproc_run_job(self.job_ocid)
            )

        elif self.engine == Job.ENGINE_TYPE_REMOTE:
            return RemoteJobConsole(
                remote_run_job(self.job_ocid)
            )
        else:
            raise ValueError(f"\"{self.engine}\" not supported, use one of: [{ENGINE_TYPE_INPROC}, {ENGINE_TYPE_REMOTE}]")

    @classmethod
    def create_container_job(self, engine: str):
        return Job(engine, Job.ENGINE_RUNTIME_CONTAINER, secret=__SECRET__)

    @classmethod
    def create_python_job(self, engine: str):
        return Job(engine, Job.ENGINE_RUNTIME_PYTHON, secret=__SECRET__)

    @classmethod
    def create_dataflow_job(self, engine: str):
        return Job(engine, Job.ENGINE_RUNTIME_DATAFLOW, secret=__SECRET__)


class InProcJobConsole:
    def __init__(self, g):
        self.g = g

    def watch(self):
        for line in self.g:
            print(line)


class RemoteJobConsole:
    def __init__(self, r):
        self.r = r

    def watch(self):
        for line in self.r.content.splitlines():
            print(line)
