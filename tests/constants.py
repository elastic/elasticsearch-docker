import os

try:
    version = os.environ['ELASTIC_VERSION']
except KeyError:
    version = open('version.txt').read().strip()
