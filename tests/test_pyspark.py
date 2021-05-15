#
# API to connect to an run a pyspark job
#

from jobs.job_factory import Job
import sys
import pytest

sys.path.append(".")


def test_inproc_pyspark_script():

    script = """
import os, random

from pyspark.sql import SparkSession

NUM_SAMPLES = int(os.environ.get("NUM_SAMPLES"))

spark = SparkSession \
    .builder \
    .appName("PySparkTestApp") \
    .getOrCreate()

sc = spark.sparkContext

def inside(p):
    x, y = random.random(), random.random()
    return x*x + y*y < 1

count = sc.parallelize(range(0, NUM_SAMPLES)) \
             .filter(inside).count()

print("*********************************************************")
print("Pi is roughly %f" % (4.0 * count / NUM_SAMPLES))
print("*********************************************************")

    """

    job = (
        Job.create_dataflow_job(Job.ENGINE_TYPE_INPROC)
        .runtime.script_from_string(script)
        .environment({"NUM_SAMPLES": 10000000})
        .build()
    )

    job.run().watch()
