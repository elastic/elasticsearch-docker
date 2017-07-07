import os
from subprocess import run, PIPE

try:
    version = os.environ['ELASTIC_VERSION']
except KeyError:
    version = run('./bin/elastic-version', stdout=PIPE).stdout.decode().strip()
