ARG POLYGAMES_VERSION
FROM ghcr.io/alignmentresearch/polygames:${POLYGAMES_VERSION}-ci-base
LABEL org.opencontainers.image.source=https://github.com/AlignmentResearch/polygames

# Need to mkdir so the user is circleci and the dir is writable
RUN mkdir "/home/circleci/project/build"
WORKDIR "/home/circleci/project/build"
ENV CC=/usr/bin/clang
ENV CXX=/usr/bin/clang++
# Build with sanitizers to detect out-of-bounds memory access, memory leaks, etc.
ENV CXXFLAGS="-fsanitize=address -fsanitize=undefined -fsanitize=leak"
ENV ASAN_OPTIONS="detect_odr_violation=0"

RUN cmake .. -DCMAKE_BUILD_TYPE=debug -DPYTORCH15=ON -DWITH_LUDII=OFF -DPOLYGAMES_WITH_CUDA=OFF -DUSE_MOLD=ON \
    && make -j \
    && cd .. \
    && python setup.py develop \
    && pip install -e src/tube

WORKDIR "/home/circleci/project"
