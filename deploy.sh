#!/bin/bash

set -euf -o pipefail

docker build -t divisordb -f docker/divisordb.Dockerfile .
docker build -t divisorsearch -f docker/divisorsearch.Dockerfile .

docker run -d --name divisordb -p 5432:5432 --memory="1G" divisordb:latest

export PGHOST=$(docker inspect -f "{{ .NetworkSettings.IPAddress }}" divisordb)

# give time for the divisordb container to start up
sleep 5
docker run -d --name divisorsearch --env PGHOST="$PGHOST" --memory="15G" divisorsearch:latest
