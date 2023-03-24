FROM cimg/python:3.10.6

# Install binary dependencies
RUN sudo apt-get update -q \
    && sudo apt-get install -y --no-install-recommends \
        wget cmake pkg-config clang lldb lcov \
    && sudo apt-get clean \
    && sudo rm -rf /var/lib/apt/lists/*

WORKDIR "/home/circleci/project"
# Copy whole repo
COPY --chown=circleci:circleci . .
# Abort if repo is dirty
RUN if [ ! -z "$(git status --porcelain)" ] ; then exit 1; fi

# Install Python dependencies
RUN pip install --upgrade pip -r .circleci/requirements.txt

# TODO(nhowe): add support for Ludii
RUN mkdir "/home/circleci/project/build"
WORKDIR "/home/circleci/project/build"
RUN CC=/usr/bin/clang CXX=/usr/bin/clang++ cmake .. -DCMAKE_BUILD_TYPE=debug -DPYTORCH15=ON -DWITH_LUDII=OFF && make -j

# Back to project workdir
ENV PYTHONPATH="/home/circleci/project"
WORKDIR "/home/circleci/project"
CMD ["/bin/sh"]
