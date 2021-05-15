import requests

url_base = "http://localhost:8000"


def create_job(runtime, job_spec):
    result = requests.get(
        f"{url_base}/create_job",
        json={"runtime": runtime, "job_spec": job_spec},
    )

    return result.json()["job_ocid"]


def run_job(job_ocid: str):

    return requests.get(f"{url_base}/run_job", json={"job_ocid": job_ocid})
