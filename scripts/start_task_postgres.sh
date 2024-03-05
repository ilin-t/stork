#!/bin/bash

DOCKER="postgres-container"

docker run -d -p 5000:22 \
           --ipc=host \
           -h $DOCKER \
           -v $DOCKER-home:/home \
           -v $DOCKER-tmp:/tmp \
           --cpuset-cpus="0-2" \
           --restart always \
           --name $DOCKER \
           $DOCKER
