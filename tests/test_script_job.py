#
# API to connect to an run a job
#

from jobs.job_factory import Job
import sys
import pytest

sys.path.append('.')


def test_in_proc_script():

    job = Job.create_python_job(Job.ENGINE_TYPE_INPROC) \
        .runtime.script_from_file("example_scripts/ex1_script.py") \
        .runtime.conda_environment("base") \
        .environment({
            "MODULES": "decorator conda"
        }) \
        .build()

    job.run().watch()
