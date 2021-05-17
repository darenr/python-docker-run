#
# API to connect to an run a job
#

from jobs.job_factory import Job
import sys
import pytest

sys.path.append(".")


def test_inproc_container():

    job = (
        Job.create_container_job(Job.ENGINE_TYPE_INPROC)
        .runtime.image("train-model:latest")
        .runtime.config({"kernel_memory": "8m", "name": "iris-{{id}}"})
        .environment(
            {
                "TARGET_VARIABLE": "variety",
                "TRAINING_KERNEL": "poly",  # linear/poly/rbf/sigmoid/precomputed
                "SOURCE_DATA_CSV": "https://raw.githubusercontent.com/darenr/public_datasets/master/iris_dataset.csv",
                "DEST_ARTIFACT": "/tmp/model-{{id}}.joblib",
            }
        )
        .build()
    )

    job.run().watch()


def test_remote_container():

    job = (
        Job.create_container_job(Job.ENGINE_TYPE_REMOTE)
        .runtime.image("train-model:latest")
        .runtime.config({"kernel_memory": "16m", "name": "iris-{{id}}"})
        .environment(
            {
                "TARGET_VARIABLE": "variety",
                "TRAINING_KERNEL": "poly",  # linear/poly/rbf/sigmoid/precomputed
                "SOURCE_DATA_CSV": "https://raw.githubusercontent.com/darenr/public_datasets/master/iris_dataset.csv",
                "DEST_ARTIFACT": "/tmp/model-{{id}}.joblib",
            }
        )
        .build()
    )

    job.run().watch()
