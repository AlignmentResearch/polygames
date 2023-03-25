FROM cimg/python:3.11.2

# Install binary dependencies
RUN sudo apt-get update -q \
    && sudo apt-get install -y --no-install-recommends \
        wget cmake pkg-config clang lldb lcov libzmq3-dev \
    && sudo apt-get clean \
    && sudo rm -rf /var/lib/apt/lists/*

ENV MOLD_VERSION="mold-1.11.0-x86_64-linux"
RUN wget "https://github.com/rui314/mold/releases/download/v1.11.0/${MOLD_VERSION}.tar.gz" \
    && tar xf "${MOLD_VERSION}.tar.gz" \
    && sudo mv "${MOLD_VERSION}/bin/mold" /usr/local/bin \
    && rm -rf "${MOLD_VERSION}" "${MOLD_VERSION}.tar.gz"

WORKDIR "/home/circleci/project"
# Copy whole repo
COPY --chown=circleci:circleci . .
# Abort if repo is dirty
RUN if [ ! -z "$(git status --porcelain)" ] ; then exit 1; fi

# Install Python dependencies
RUN pip install --upgrade pip -r .circleci/requirements.txt && rm -rf /home/circleci/.cache

# TODO(nhowe): add support for Ludii
RUN mkdir "/home/circleci/project/build"
WORKDIR "/home/circleci/project/build"
RUN CC=/usr/bin/clang CXX=/usr/bin/clang++ cmake .. -DCMAKE_BUILD_TYPE=debug -DPYTORCH15=ON -DWITH_LUDII=OFF -DPOLYGAMES_WITH_CUDA=OFF -DUSE_MOLD=ON && make -j

# Back to project workdir
ENV PYTHONPATH="/home/circleci/project"
WORKDIR "/home/circleci/project"
CMD ["/bin/sh"]
