FROM nvidia/cuda:12.0.1-cudnn8-devel-ubuntu22.04
LABEL org.opencontainers.image.source=https://github.com/AlignmentResearch/polygames
ENV DEBIAN_FRONTEND noninteractive

# Install binary dependencies
RUN apt-get update -q \
    && apt-get install -y --no-install-recommends \
    wget \
    git \
    python3 python3-dev python3-pip python3-setuptools python-is-python3 \
    cmake pkg-config clang lldb \
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

# Install CUDA Python dependencies
WORKDIR "/polygames"
COPY --chown=circleci:circleci requirements-cuda.txt requirements.txt ./
RUN pip install -r requirements.txt -r requirements-cuda.txt && rm -rf "${HOME}/.cache"

# Copy whole repo
COPY --chown=circleci:circleci . .
# Abort if repo is dirty
RUN if ! { [ -z "$(git status --porcelain --ignored=traditional)" ] \
    && [ -z "$(cd src/third_party/pybind11 && git status --porcelain --ignored=traditional)" ] \
    ; }; then exit 1; fi

# Build in RelWithDebInfo
WORKDIR "/polygames/build"
ENV CC=/usr/bin/clang
ENV CXX=/usr/bin/clang++
RUN cmake .. -DCMAKE_BUILD_TYPE=relwithdebinfo -DPYTORCH15=ON -DWITH_LUDII=OFF -DPOLYGAMES_WITH_CUDA=OFF -DUSE_MOLD=ON \
    && make -j

ENV PYTHONPATH="/home/circleci/project"
CMD ["/bin/sh"]
