#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function


import pandas as pd
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from joblib import dump
import os
import logging
import time

#
# requires two options:
#   SOURCE_DATA_CSV: folder on oci storage
#   DEST_ARTIFACT:   path for resulting model


logging.basicConfig(
    level=logging.DEBUG,
    format='%(processName)s::%(relativeCreated)6d %(threadName)s %(message)s')


def train_model(
    target_variable: str,
    training_kernel: str,
    source_data_csv: str,
    dest_artifact: str
):

    logging.info(f"TrainModelOperatortrain_model reading dataset [{source_data_csv}]")

    df = pd.read_csv(source_data_csv)

    logging.info(f"TrainModelOperatortrain_model dataset, rows: [{len(df)}]")

    le = LabelEncoder()
    y = le.fit_transform(df[target_variable])
    X = df.drop([target_variable], axis=1)

    logging.info(f"TrainModelOperatortrain_model begin training...")

    clf = SVC(
        kernel=training_kernel,
        verbose=True,
        probability=True,
        random_state=42
    )

    clf.fit(X, y)

    for param, value in clf.get_params(deep=True).items():
        logging.info(f"model parameter: {param}={value}")

    dump_file = dump(clf, dest_artifact)
    logging.info(f"TrainModelOperatortrain_model created {dump_file}")

    for i, row in enumerate(X.values):
        yhat = clf.predict(row.reshape(1, -1))[0]
        actual = y[i]
        logging.info(f"Actual: {actual}, Predicted: {yhat}, Correct: {yhat==actual}")


    accuracy = accuracy_score(y, clf.predict(X))
    logging.info(f"accuracy_score: {accuracy}")

    logging.info("training complete!")


if __name__ == '__main__':

    logging.info(f"TrainModelOperatormain")

    required_env_vars = [
        'TARGET_VARIABLE',
        'SOURCE_DATA_CSV',
        'DEST_ARTIFACT',
        'TRAINING_KERNEL'
    ]

    if all([elem in os.environ for elem in required_env_vars]):

        target_variable = os.environ['TARGET_VARIABLE']
        source_data_csv = os.environ['SOURCE_DATA_CSV']
        dest_artifact = os.environ['DEST_ARTIFACT']
        training_kernel = os.environ['TRAINING_KERNEL']

        train_model(
            target_variable,
            training_kernel,
            source_data_csv,
            dest_artifact
        )

    else:

        logging.error(f"usage: required environment variables: {', '.join(required_env_vars)}")
        for key in os.environ:
            logging.info(f"Env: {key}={os.environ.get(key)}")

    print("ALL DONE")
