#
# API to connect to an run a job
#

from jobs import job_factory


if __name__ == '__main__':


    container_job = job_factory \
        .builder
        .create_job(engine="odsc", implementation="container") \
        .config("cpu_percent") \
        .environment({
            'TARGET_VARIABLE': 'variety',
            'TRAINING_KERNEL': 'poly',  # linear/poly/rbf/sigmoid/precomputed
            'SOURCE_DATA_CSV': 'https://raw.githubusercontent.com/darenr/public_datasets/master/iris_dataset.csv',
            'DEST_ARTIFACT':   '/tmp/model-${OCID}.joblib'
        }) \
        .getOrCreate()
