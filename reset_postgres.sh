#!/bin/bash
# run this for local development

rm -rf /usr/local/var/postgres
initdb --locale=C -E UTF-8 /usr/local/var/postgres
pg_ctl -D /usr/local/var/postgres -l /tmp/logfile start

psql postgres <<EOF
CREATE DATABASE divisor
    WITH OWNER = $USER;
\connect divisor;
CREATE EXTENSION pgmp;
EOF
