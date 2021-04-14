#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function


import pandas as pd
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from joblib import dump
import os, logging

#
# requires two options:
#   SOURCE_DATA_CSV: folder on oci storage
#   DEST_ARTIFACT:   path for resulting model


logging.basicConfig(level=logging.DEBUG)

def train_model(source_data_csv: str, dest_artifact: str):
    logging.info(f"Iris::train_model {source_data_csv=}, {dest_artifact=}")

    df = pd.read_csv(source_data_csv)

    y = LabelEncoder().fit_transform(df['variety'])
    X = df.drop(['variety'], axis=1)

    clf = SVC()
    clf.fit(X, y)

    print(clf)

    dump(clf, dest_artifact)


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
