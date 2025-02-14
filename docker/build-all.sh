#!/usr/bin/env bash
set -eo pipefail

echo "This script should be run from the repository root"

VERSION="1.4.3"
echo "Building version $VERSION. If you update it, remember to also update docker_img_version in .circleci/config.yml"

if [ -n "${CIRCLECI_DOCKER_IMG_VERSION}" ]; then
    if [ "${CIRCLECI_DOCKER_IMG_VERSION}" = "${VERSION}" ]; then
        echo "CircleCI docker image version is up to date"
        exit 0
    else
        echo "CircleCI docker image version is NOT up to date!"
        exit 1
    fi
fi

CI_BASE="ghcr.io/alignmentresearch/polygames:${VERSION}-ci-base"
CI_SANITIZE="ghcr.io/alignmentresearch/polygames:${VERSION}-ci-sanitize"
CI_RELWITHDEBINFO="ghcr.io/alignmentresearch/polygames:${VERSION}-ci-relwithdebinfo"
RUNNER="ghcr.io/alignmentresearch/polygames:${VERSION}-runner"
DEVBOX="ghcr.io/alignmentresearch/polygames:${VERSION}-devbox-$(whoami)"

docker pull "$CI_BASE" \
    || { docker build \
    -t "$CI_BASE" -f docker/ci-base/Dockerfile . \
    && docker push "$CI_BASE"; }

docker pull "$CI_SANITIZE" \
    || { docker build \
    --build-arg "POLYGAMES_VERSION=${VERSION}" \
    -t "$CI_SANITIZE" -f docker/ci-sanitize/Dockerfile . \
    && docker push "$CI_SANITIZE"; }

docker pull "$CI_RELWITHDEBINFO" \
    || { docker build \
    --build-arg "POLYGAMES_VERSION=${VERSION}" \
    -t "$CI_RELWITHDEBINFO" -f docker/ci-relwithdebinfo/Dockerfile . \
    && docker push "$CI_RELWITHDEBINFO"; }

echo "Building or pulling version $VERSION for the experiment runner"
docker pull "$RUNNER" \
    || { docker build  \
    -t "$RUNNER" -f docker/runner/Dockerfile . \
    && docker push "$RUNNER"; }

if [ "${CI}" = "true" ]; then
    echo "Running in CI, not building devbox"
else
    # Get the SSH agent's current keys
    SSH_KEY="$(ssh-add -L)"
    echo "Building the devbox for version $VERSION and SSH key $SSH_KEY"
    docker build \
        --build-arg "SSH_KEY=${SSH_KEY}" \
        --build-arg "POLYGAMES_VERSION=${VERSION}" \
        -t "$DEVBOX" -f docker/devbox/Dockerfile .
    docker push "$DEVBOX"
fi
