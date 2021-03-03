#!/bin/bash

set -euf -o pipefail

docker build -t divisordb -f docker/divisordb.Dockerfile .
docker build -t generate -f docker/generate_search_blocks.Dockerfile .
docker build -t process -f docker/process_search_blocks.Dockerfile .

docker run -d --name divisordb -p 5432:5432 --memory="1G" divisordb:latest

export PGHOST=$(docker inspect -f "{{ .NetworkSettings.IPAddress }}" divisordb)

# give time for the divisordb container to start up
sleep 5
docker run -d --name generate --env PGHOST="$PGHOST" --memory="1G" generate:latest
sleep 5
docker run -d --name process --env PGHOST="$PGHOST" --memory="1G" process:latest


# monitoring

# need pip to install requirements to run alerting script
# need smtp to send alert emails
sudo apt install -y python3-pip ssmtp
pip3 install -r alerts/requirements.txt
sudo -E alerts/configure_ssmtp.sh
nohup python3 -m alerts.monitor_docker &
