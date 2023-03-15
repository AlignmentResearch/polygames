FROM nvidia/cuda:11.7.1-cudnn8-devel-ubuntu22.04
ENV DEBIAN_FRONTEND noninteractive
ENV LANG=C.UTF-8

# Install binary dependencies
RUN apt-get update -q \
    && apt-get install -y --no-install-recommends \
    wget \
    git \
    python3 python3-dev python3-pip python3-setuptools python-is-python3 \
    cmake \
    libmkl-core libmkl-intel-thread libmkl-intel-ilp64 \
    vim \
    tmux \
    less \
    ssh \
    openssh-server \
    sudo \
    curl \
    jq \
    libzmq3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Remote development niceties:
## Alacritty terminal, ssh keys dir
RUN wget https://github.com/alacritty/alacritty/releases/download/v0.11.0/alacritty.info \
    && tic -xe alacritty,alacritty-direct alacritty.info \
    && rm alacritty.info \
    && mkdir /run/sshd && mkdir /root/.ssh

## Unison synchronizer
RUN wget https://github.com/bcpierce00/unison/releases/download/v2.52.1/unison-v2.52.1+ocaml-4.14.0+x86_64.linux.tar.gz \
    && mkdir unison-work \
    && tar xf unison-v2.52.1+ocaml-4.14.0+x86_64.linux.tar.gz -C unison-work \
    && mv unison-work/bin/unison* /usr/local/bin \
    && rm -rf unison*

# Following https://stackoverflow.com/questions/35134713/disable-cache-for-specific-run-commands, build with
# docker build --build-arg CACHEBUST="$(git ls-remote origin refs/heads/dockerfile)"
ARG CACHEBUST=0
# Copy code
RUN git clone --recursive --branch dockerfile https://github.com/AlignmentResearch/polygames /polygames
WORKDIR /polygames
RUN pip install -r docker-dev/requirements.txt

# Copy SSH keys to the right place
RUN mv docker-dev/authorized_keys /root/.ssh/authorized_keys

RUN mkdir /polygames/build
WORKDIR /polygames/build

# TODO(nhowe): add support for Ludii
RUN cmake .. -DCMAKE_BUILD_TYPE=relwithdebinfo -DPYTORCH15=ON -DWITH_LUDII=OFF && make -j

WORKDIR /polygames
ENV PYTHONPATH=/polygames
