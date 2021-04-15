#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function


import pandas as pd
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from joblib import dump
import os, logging, time

#
# requires two options:
#   SOURCE_DATA_CSV: folder on oci storage
#   DEST_ARTIFACT:   path for resulting model


logging.basicConfig(level=logging.DEBUG)

def train_model(source_data_csv: str, dest_artifact: str):
    logging.info(f"Iris::train_model {source_data_csv}, {dest_artifact}")

    df = pd.read_csv(source_data_csv)

    y = LabelEncoder().fit_transform(df['variety'])
    X = df.drop(['variety'], axis=1)

    clf = SVC()
    clf.fit(X, y)

    for param, value in clf.get_params(deep=True).items():
        logging.info(f"{param} -> {value}")

    dump_file = dump(clf, dest_artifact)
    logging.info(f"Iris::train_model created {dump_file}")

    for i, row in enumerate(X.values):
        yhat = clf.predict(row.reshape(1, -1))[0]
        logging.info(f"Predicted: {yhat}, Actual: {y[i]}")
        time.sleep(0.05)

    logging.info("training complete")

if __name__ == '__main__':

    logging.info(f" Iris::main")

    if 'SOURCE_DATA_CSV' in os.environ and 'DEST_ARTIFACT' in os.environ:

        source_data_csv = os.environ['SOURCE_DATA_CSV']
        dest_artifact = os.environ['DEST_ARTIFACT']

        train_model(source_data_csv, dest_artifact)

    else:

        logging.error("requires SOURCE_DATA_CSV and DEST_ARTIFACT env vars")
        for key in os.environ:
            logging.info(f"{key}={os.environ.get(key)}")
