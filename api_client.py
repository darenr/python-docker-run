#
# API to connect to an run a job
#

from jobs.job_factory import Job

if __name__ == "__main__":

    job = Job.create_job(Job.ENGINE_TYPE_ODSC, Job.ENGINE_RUNTIME_CONTAINER) \
           .runtime.image("train-model:latest") \
           .runtime.config({
               "kernel_memory": "16m",
               "name": "iris-{{OCID}}"
           }) \
           .environment({
                "TARGET_VARIABLE": "variety",
                "TRAINING_KERNEL": "poly",  # linear/poly/rbf/sigmoid/precomputed
                "SOURCE_DATA_CSV": "https://raw.githubusercontent.com/darenr/public_datasets/master/iris_dataset.csv",
                "DEST_ARTIFACT": "/tmp/model-{{OCID}}.joblib",
            }) \
            .build()

    print(job)

    job.run().watch()
