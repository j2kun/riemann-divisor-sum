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
sudo apt-get install ssmtp

sudo -E cat > /etc/ssmtp/ssmtp.conf << EOF
root=$GMAIL_APP_USER
mailhub=smtp.gmail.com:465
FromLineOverride=YES
AuthUser=$GMAIL_APP_USER
AuthPass=$GMAIL_APP_PASS
TLS_CA_FILE=/etc/ssl/certs/ca-certificates.crt
UseTLS=Yes
rewriteDomain=gmail.com
hostname=$(hostname).$(dnsdomainname)
EOF
