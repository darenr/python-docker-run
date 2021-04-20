#
# API to connect to an run a job
#

from jobs import job_factory

import requests

example_script_job_spec = {
    'conda_environment': "pyk8s",
    'script': open('example_scripts/ex1_script.py').read(),
    'env': {
        'MODULES': 'flask joblib scipy'
    }
}

example_container_job_spec = {
    'container': "train-model:latest",
    'env': {
        'TARGET_VARIABLE': 'variety',
        'TRAINING_KERNEL': 'poly',
        'SOURCE_DATA_CSV': 'https://raw.githubusercontent.com/darenr/public_datasets/master/iris_dataset.csv',
        'DEST_ARTIFACT':   '/tmp/model-{{job_ocid}}.joblib'
    }
}

if __name__ == '__main__':

    result = requests.get('http://localhost:8000/create_job', json={
        'runtime': 'container',
        'job_spec': example_container_job_spec
    })

    job_ocid = result.json()['job_ocid']

    print(f'job_ocid: {job_ocid}')

    result = requests.get('http://localhost:8000/run_job',
        json={
            'job_ocid': job_ocid
        }
    )

    for line in result.content.splitlines():
        print(line.decode('utf-8').strip())

    #
    # container_job = job_factory \
    #     .builder
    #     .create_job(engine="odsc", implementation="container") \
    #     .config("cpu_percent") \
    #     .environment({
    #         'TARGET_VARIABLE': 'variety',
    #         'TRAINING_KERNEL': 'poly',  # linear/poly/rbf/sigmoid/precomputed
    #         'SOURCE_DATA_CSV': 'https://raw.githubusercontent.com/darenr/public_datasets/master/iris_dataset.csv',
    #         'DEST_ARTIFACT':   '/tmp/model-${OCID}.joblib'
    #     }) \
    #     .getOrCreate()