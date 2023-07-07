#!/bin/bash

DOCKER="postgres-test-db-config"

docker run -d -p 6000:22 -p 6432:5432 \
           --ipc=host \
           -h $DOCKER \
           -v $DOCKER-home:/home \
           -v $DOCKER-tmp:/tmp \
           -v $DOCKER-data:/var/lib/postgresql/data \
           -v /var/run/postgresql:/var/run/postgresql \
           --cpuset-cpus="0-2" \
           --restart always \
           --name $DOCKER \
           --env-file config.ini \
           $DOCKER
