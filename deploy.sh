#!/bin/bash

set -euf -o pipefail

docker build -t divisordb -f divisordb.Dockerfile .
docker build -t divisorsearch -f divisorsearch.Dockerfile .

docker run -d --name divisordb -p 5432:5432 --memory="1G" divisordb:latest

# The host address for the divisordb container is nested inside a json
# `jq` is a CLI for stream processing json data.
export PGHOST=$(docker network inspect bridge | jq -r '.[0].Containers[] | select(.Name=="divisordb") | .IPv4Address' | sed 's|/.*$||g')

# give time for the divisordb container to start up
sleep 5
docker run -d --name divisorsearch --env PGHOST="$PGHOST" --memory="15G" divisorsearch:latest
