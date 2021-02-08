FROM python:3.7-slim-buster

# Install system level dependencies, including make, gcc, gmp, mpc, and
# postgres libraries, all required to build the pgmp extension.
RUN apt-get update \
        && apt-get install -y build-essential libgmp3-dev libmpc-dev

COPY . /divisor
WORKDIR "/divisor"

RUN pip3 install -r requirements.txt

# these environment variables are used by psycopg2 to initialize the connection
# of the psycopg2 library.  The PGHOST environment variable must be passed from
# the command line --env flag passed to `docker run`, because the host ip
# address is chosen by docker when the divisordb.Dockerfile container is run.
ENV PGUSER=docker
ENV PGPASSWORD=docker
ENV PGDATABASE=divisor

ENTRYPOINT ["python3", "-u", "-m", "timing.ec2_timing_test"]
