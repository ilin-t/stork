FROM postgres:16

WORKDIR /app

# SSH setup
RUN apt update && apt install -y \
    software-properties-common \
    libssl-dev openssh-server

# General packages
RUN apt update && apt install -y \
    less nano vim emacs htop tree git rsync

# Postgres default setup
RUN apt-mark hold postgresql-16 postgresql-client-16 \
    postgresql-common postgresql-client-common
    
# Postgres PLPython execution environment    
RUN apt-get update -qq && apt-get install postgresql-plpython3-16 -qq -y

# Default python setup
RUN apt-get -y install python3 python3-pip python3-venv -qq

# Clear caches
RUN apt-get clean && rm -rf /var/cache/apt/* /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt requirements.txt

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

# Default Postgres environment variables
ENV POSTGRES_DB=postgres-default-db
ENV POSTGRES_PASSWORD=postgres-default-password
ENV POSTGRES_USER=postgres-default-admin

# Debugging info
#RUN echo "The POSTGRES_DB variable value is $POSTGRES_DB, the POSTGRES_PASSWORD variable value is $POSTGRES_PASSWORD, the POSTGRES_USER variable is $POSTGRES_USER."

EXPOSE 22 5432
