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

# Remote development niceties: Alacritty terminal and sshd
RUN wget https://github.com/alacritty/alacritty/releases/download/v0.11.0/alacritty.info \
    && tic -xe alacritty,alacritty-direct alacritty.info \
    && rm alacritty.info \
    && mkdir /run/sshd && mkdir /root/.ssh

# Copy code
RUN git clone --recursive --branch dockerfile https://github.com/AlignmentResearch/polygames /polygames
WORKDIR /polygames
RUN mv docker-dev/authorized_keys /root/authorized_keys
RUN pip install -r docker-dev/requirements.txt

RUN mkdir /polygames/build
WORKDIR /polygames/build

# TODO(nhowe): add support for Ludii
RUN cmake .. -DCMAKE_BUILD_TYPE=relwithdebinfo -DPYTORCH15=ON -DWITH_LUDII=OFF
RUN make -j

WORKDIR /polygames
ENV PYTHONPATH=/polygames
