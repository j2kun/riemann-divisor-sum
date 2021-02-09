FROM postgres:12

# these environment variables are used by postgres to create a user and a
# database and set up initial permissions.
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD docker
ENV POSTGRES_DB divisor

# Install system level dependencies, including make, gcc, gmp, mpc, and
# postgres libraries, all required to build the pgmp extension.
RUN apt-get update \
        && apt-get install -y pgxnclient build-essential libgmp3-dev postgresql-server-dev-12 libmpc-dev

# Install python dependencies.  Because the pgmp installation has a setup step
# that runs a python2 script that depends on six, we have to pip2-install six.
RUN apt-get install -y python3.7 python3-setuptools python3-pip python-pip python3.7-dev \
        && pip3 install wheel \
        && pip install six

RUN pgxn install pgmp 

COPY . /divisor
WORKDIR "/divisor"

# A recent version of pip is required to deal with an issue in numba whereby it
# cannot find the correct llvmlite platform binary on PyPI, and then it falls
# back to trying to build from source, in which case we fail because we don't
# have llvm installed. The llvmlite docs suggest not to compile llvm from
# source.
# 
# Note: this installation step could be made more lightweight.  This container
# only exists to run the postgres database, and it uses our
# riemann/postgres_database.py's __main__ to initialize the schema. However,
# requirements.txt contains dependencies for all parts of the application,
# including the heavyweight numba library. To fix this, we might find a subset
# of the python requirements that are required to initialize the schema, and
# maintain a separate requirements_db.txt just for that.
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

# these environment variables are used by psycopg2 to initialize the connection
# of the psycopg2 library.
ENV PGUSER=docker
ENV PGPASSWORD=docker
ENV PGDATABASE=divisor

# Connects to the database and creates the initial schema if needed.  this
# directory contains scripts that are run automatically by the container at
# startup.
COPY setup_schema.sh /docker-entrypoint-initdb.d/
