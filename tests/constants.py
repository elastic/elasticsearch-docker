import os
from subprocess import run, PIPE

try:
    version = os.environ['ELASTIC_VERSION']
    # When building the image using local builds of es + xpack,
    # `-SNAPSHOT` is not reported by ES.
    version = version.rstrip('-SNAPSHOT')
except KeyError:
    version = run('./bin/elastic-version', stdout=PIPE).stdout.decode().strip()
