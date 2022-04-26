FROM ubuntu:20.04

RUN apt-get update && apt-get upgrade -y

# Install Python3.8.13
RUN apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
RUN wget https://www.python.org/ftp/python/3.8.13/Python-3.8.13.tgz
RUN tar -xf Python-3.8.13.tgz && cd Python-3.8.13 && ./configure --enable-optimizations && make -j 8 && make altinstall

# install git
RUN apt-get install -y git

# copy app & install packages
RUN mkdir /usr/local/airee-controller
COPY ["requirements.txt", "/usr/local/airee-controller/"]
RUN python3.8 -m pip install -r /usr/local/airee-controller/requirements.txt
COPY ["airee_repos.py", "git_module.py", "util.py", "config.py", "pair_key.py", "entrypoint_init.py", "/usr/local/airee-controller/"]

ENTRYPOINT [ "python3.8", "/usr/local/airee-controller/entrypoint_init.py"]
