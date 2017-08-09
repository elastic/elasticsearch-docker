from subprocess import run, PIPE

version = run('./bin/elastic-version', stdout=PIPE).stdout.decode().strip()
