ARG POLYGAMES_VERSION
FROM ghcr.io/alignmentresearch/polygames:${POLYGAMES_VERSION}-ci-base
LABEL org.opencontainers.image.source=https://github.com/AlignmentResearch/polygames

# Build with optimizations so the python tests are moderately fast
RUN mkdir "/home/circleci/project/build"
WORKDIR "/home/circleci/project/build"
ENV CC=/usr/bin/clang
ENV CXX=/usr/bin/clang++
RUN cmake .. -DCMAKE_BUILD_TYPE=relwithdebinfo -DPYTORCH15=ON -DWITH_LUDII=OFF -DPOLYGAMES_WITH_CUDA=OFF -DUSE_MOLD=ON \
    && make -j

WORKDIR "/home/circleci/project"
