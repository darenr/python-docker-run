from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from autosklearn.classification import AutoSklearnClassifier

X, y = make_classification(
    n_samples=100, n_features=10, n_informative=5, n_redundant=5, random_state=1
)

# split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33, random_state=1
)

# define search
automl = AutoSklearnClassifier(
    time_left_for_this_task=1 * 60, per_run_time_limit=30, n_jobs=-1
)

# perform the search
automl.fit(X_train, y_train)

# summarize
print(automl.sprint_statistics())

# all models

print(automl.show_models())


# evaluate best model
y_hat = automl.predict(X_test)
acc = accuracy_score(y_test, y_hat)

print("Accuracy: %.3f" % acc)
