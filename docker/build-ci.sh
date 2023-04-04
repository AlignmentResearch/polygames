#!/usr/bin/env sh
set -eo pipefail

VERSION="$1"

if [ -z "$VERSION" ]; then
    echo "Must specify a version to build"
    exit 1;
fi

echo "Building version $VERSION"
docker build -t "ghcr.io/alignmentresearch/polygames:${VERSION}-ci-base" -f docker/ci-base/Dockerfile .
docker build -t "ghcr.io/alignmentresearch/polygames:${VERSION}-ci-sanitize" -f docker/ci-sanitize/Dockerfile .
docker build -t "ghcr.io/alignmentresearch/polygames:${VERSION}-ci-relwithdebinfo" -f docker/ci-relwithdebinfo/Dockerfile .
