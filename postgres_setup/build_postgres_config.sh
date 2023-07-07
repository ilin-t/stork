#!/bin/bash

# navigate to script directory
cd "$(dirname "$0")"
# build the dev image
DOCKER_BUILDKIT=1 docker build -t postgres-test-db-config .
