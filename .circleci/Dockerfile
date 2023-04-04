FROM cimg/python:3.10.10
LABEL org.opencontainers.image.source=https://github.com/AlignmentResearch/polygames


# Install binary dependencies
RUN sudo apt-get update -q \
    && sudo apt-get install -y --no-install-recommends \
        wget cmake pkg-config clang lcov libzmq3-dev mold \
    && sudo apt-get clean \
    && sudo rm -rf /var/lib/apt/lists/*

WORKDIR "/home/circleci/project"
# Install Python dependencies
COPY --chown=circleci:circleci .circleci/requirements.txt ./requirements-circleci.txt
RUN pip install --upgrade pip -r requirements-circleci.txt && rm -rf "${HOME}/.cache"

# Copy whole repo
COPY --chown=circleci:circleci . .
# Abort if repo is dirty
RUN mv requirements-circleci.txt .circleci/requirements.txt && \
    if ! { [ -z "$(git status --porcelain --ignored=traditional)" ] \
    && [ -z "$(cd src/third_party/pybind11 && git status --porcelain --ignored=traditional)" ] \
    ; }; then exit 1; fi

# TODO(nhowe): add support for Ludii
RUN mkdir "/home/circleci/project/build"
WORKDIR "/home/circleci/project/build"
ENV CC=/usr/bin/clang
ENV CXX=/usr/bin/clang++
RUN cmake .. -DCMAKE_BUILD_TYPE=debug -DPYTORCH15=ON -DWITH_LUDII=OFF -DPOLYGAMES_WITH_CUDA=OFF -DUSE_MOLD=ON && make -j

# Back to project workdir
ENV PYTHONPATH="/home/circleci/project"
WORKDIR "/home/circleci/project"
CMD ["/bin/sh"]
