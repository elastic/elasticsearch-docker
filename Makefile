SHELL = /bin/bash
ELASTIC_VERSION := $(shell ./bin/elastic-version)

TEDI_DEBUG ?= false
TEDI_VERSION ?= 0.10
TEDI ?= docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(PWD):/mnt \
  -v $(PWD)/../..:/release-manager \
  -e TEDI_DEBUG=$(TEDI_DEBUG) \
  docker.elastic.co/tedi/tedi:$(TEDI_VERSION)

export PATH := ./bin:./venv/bin:$(PATH)

IMAGE_FLAVORS ?= oss full

default: from-release

# Test specified versions without building
test: lint
	docker run --rm -v "$(PWD):/mnt" bash rm -rf /mnt/tests/datadir1 /mnt/tests/datadir2
	$(foreach FLAVOR, $(IMAGE_FLAVORS), \
	  pyfiglet -w 160 -f puffy "test: $(FLAVOR) single"; \
	  ./bin/pytest --image-flavor=$(FLAVOR) --single-node tests; \
	  pyfiglet -w 160 -f puffy "test: $(FLAVOR) multi"; \
	  ./bin/pytest --image-flavor=$(FLAVOR) tests; \
	)

# Test a snapshot image, which requires modifying the ELASTIC_VERSION to find the right images.
test-snapshot:
	ELASTIC_VERSION=$(ELASTIC_VERSION)-SNAPSHOT make test

# Build and test
test-build: lint build docker-compose

lint: venv
	flake8 tests

clean:
	$(foreach FLAVOR, $(IMAGE_FLAVORS), \
	  COMPOSE_FILE=".tedi/build/elasticsearch-$(FLAVOR)/docker-compose.yml"; \
	  if [[ -f $$COMPOSE_FILE ]]; then \
	    docker-compose -f $$COMPOSE_FILE down && docker-compose -f $$COMPOSE_FILE rm -f -v; \
	  fi; \
	)
	$(TEDI) clean --clean-assets

# Build images from releases on www.elastic.co
# The ELASTIC_VERSION specified in this file might not have been released yet,
# so you may need to override it.
from-release:
	$(TEDI) build --fact=elastic_version:$(ELASTIC_VERSION) \
	              --fact=image_tag:$(ELASTIC_VERSION) \
	              --asset-set=default

# Build images from snapshots on snapshots.elastic.co
from-snapshot:
	$(TEDI) build --fact=elastic_version:$(ELASTIC_VERSION) \
	              --fact=image_tag:$(ELASTIC_VERSION)-SNAPSHOT \
	              --asset-set=snapshot

# Build release images from within the Release Manager.
release-manager-release: clean
	$(TEDI) build --fact=elastic_version:$(ELASTIC_VERSION) \
	              --fact=image_tag:$(ELASTIC_VERSION) \
	              --asset-set=local_release

# Build snapshot images from within the Release Manager.
release-manager-snapshot: clean
	$(TEDI) build --fact=elastic_version:$(ELASTIC_VERSION) \
	              --fact=image_tag:$(ELASTIC_VERSION)-SNAPSHOT \
	              --asset-set=local_snapshot

# The tests are written in Python. Make a virtualenv to handle the dependencies.
venv: requirements.txt
	@if [ -z $$PYTHON3 ]; then\
	    PY3_MINOR_VER=`python3 --version 2>&1 | cut -d " " -f 2 | cut -d "." -f 2`;\
	    if (( $$PY3_MINOR_VER < 5 )); then\
		echo "Couldn't find python3 in \$PATH that is >=3.5";\
		echo "Please install python3.5 or later or explicity define the python3 executable name with \$PYTHON3";\
	        echo "Exiting here";\
	        exit 1;\
	    else\
		export PYTHON3="python3.$$PY3_MINOR_VER";\
	    fi;\
	fi;\
	test -d venv || virtualenv --python=$$PYTHON3 venv;\
	pip install -r requirements.txt;\
	touch venv;\
