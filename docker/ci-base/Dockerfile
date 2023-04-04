FROM cimg/python:3.10.10
LABEL org.opencontainers.image.source=https://github.com/AlignmentResearch/polygames

# Install binary dependencies
RUN sudo apt-get update -q \
    && sudo apt-get install -y --no-install-recommends \
        wget cmake pkg-config clang lcov libzmq3-dev mold \
    && sudo apt-get clean \
    && sudo rm -rf /var/lib/apt/lists/*

# Install CPU Python dependencies
WORKDIR "/home/circleci/project"
COPY --chown=circleci:circleci requirements-cpu.txt requirements.txt .
RUN pip install -r requirements.txt -r requirements-cpu.txt && rm -rf "${HOME}/.cache"

# Copy whole repo
COPY --chown=circleci:circleci . .
# Abort if repo is dirty
RUN if ! { [ -z "$(git status --porcelain --ignored=traditional)" ] \
    && [ -z "$(cd src/third_party/pybind11 && git status --porcelain --ignored=traditional)" ] \
    ; }; then exit 1; fi

ENV PYTHONPATH="/home/circleci/project"
CMD ["/bin/sh"]
