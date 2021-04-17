import os

for module in os.environ.get('MODULES').split():
    m = __import__(module)
    print(module, m.__version__)
