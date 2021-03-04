#!/bin/bash

# export secrets as environment variables, then run
# 
#   sudo -E configure_ssmtp.sh
#

cat > /etc/ssmtp/ssmtp.conf << EOF
root=$GMAIL_APP_USER
mailhub=smtp.gmail.com:465
FromLineOverride=YES
AuthUser=$GMAIL_APP_USER
TLS_CA_FILE=/etc/ssl/certs/ca-certificates.crt
UseTLS=Yes
rewriteDomain=gmail.com
hostname=$(hostname).$(dnsdomainname)
EOF
