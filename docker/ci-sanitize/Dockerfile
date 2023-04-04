ARG POLYGAMES_VERSION
FROM ghcr.io/alignmentresearch/polygames:${POLYGAMES_VERSION}-ci-base
LABEL org.opencontainers.image.source=https://github.com/AlignmentResearch/polygames

# Build with sanitizers to detect out-of-bounds memory access, memory leaks, etc.
WORKDIR "/home/circleci/project/build"
ENV CC=/usr/bin/clang
ENV CXX=/usr/bin/clang++
ENV ASAN_OPTIONS="detect_odr_violation=0"
RUN cmake .. -DCMAKE_BUILD_TYPE=debug -DPYTORCH15=ON -DWITH_LUDII=OFF -DPOLYGAMES_WITH_CUDA=OFF -DUSE_MOLD=ON \
    && make -j

WORKDIR "/home/circleci/project"
