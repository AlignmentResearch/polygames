#!/bin/sh

# Git checkout code from CircleCI. Only difference is removing --force at the bottom when checking out.

set -e
# Workaround old docker images with incorrect $HOME
# check https://github.com/docker/docker/issues/2968 for details
if [ "${HOME}" = "/" ]
then
  export HOME=$(getent passwd $(id -un) | cut -d: -f6)
fi

echo "Using SSH Config Dir '$SSH_CONFIG_DIR'"
git --version

mkdir -p "$SSH_CONFIG_DIR"
chmod 0700 "$SSH_CONFIG_DIR"

printf "%s" 'github.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCj7ndNxQowgcQnjshcLrqPEiiphnt+VTTvDP6mHBL9j1aNUkY4Ue1gvwnGLVlOhGeYrnZaMgRK6+PKCUXaDbC7qtbW8gIkhL7aGCsOr/C56SJMy/BCZfxd1nWzAOxSDPgVsmerOBYfNqltV9/hWCqBywINIR+5dIg6JTJ72pcEpEjcYgXkE2YEFXV1JHnsKgbLWNlhScqb2UmyRkQyytRLtL+38TGxkxCflmO+5Z8CSSNY7GidjMIZ7Q4zMjA2n1nGrlTDkzwDCsw+wqFPGQA179cnfGWOWRVruj16z6XyvxvjJwbz0wQZ75XK5tKSb7FNyeIEs4TT4jk+S4dhPeAUC5y+bDYirYgM4GC7uEnztnZyaVWQ7B381AK4Qdrwt51ZqExKbQpTUNn+EjqoTwvqNj4kqx5QUCI0ThS/YkOxJCXmPUWZbhjpCg56i+2aB6CmK2JGhn57K5mj0MNdBXA4/WnwH6XoPWJzK5Nyu2zB3nAZp+S5hpQs+p1vN1/wsjk=
github.com ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEmKSENjQEezOmxkZMy7opKgwFB9nkt5YRrYMjNuG5N87uRgg6CLrbo5wAdT/y6v0mKV0U2w0WZ2YB/++Tpockg=
github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl
bitbucket.org ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAubiN81eDcafrgMeLzaFPsw2kNvEcqTKl/VqLat/MaB33pZy0y3rJZtnqwR2qOOvbwKZYKiEO1O6VqNEBxKvJJelCq0dTXWT5pbO2gDXC6h6QDXCaHo6pOHGPUy+YBaGQRGuSusMEASYiWunYN0vCAI8QaXnWMXNMdFP3jHAJH0eDsoiGnLPBlBp4TNm6rYI74nMzgz3B9IikW4WVK+dc8KZJZWYjAuORU3jc1c/NPskD2ASinf8v3xnfXeukU0sJ5N6m5E8VLjObPEO+mN2t/FZTMZLiFqPWc/ALSqnMnnhwrNi2rbfg/rd/IpL8Le3pSBne8+seeFVBoGqzHM9yXw==
gitlab.com ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBFSMqzJeV9rUzU4kWitGjeR4PWSa29SPqJ1fVkhtj3Hw9xjLVXVYrU9QlYWrOLXBpQ6KWjbjTDTdDkoohFzgbEY=
' >> "$SSH_CONFIG_DIR/known_hosts"
chmod 0600 "$SSH_CONFIG_DIR/known_hosts"

rm -f "$SSH_CONFIG_DIR/id_rsa"
printf "%s" "$CHECKOUT_KEY" > "$SSH_CONFIG_DIR/id_rsa"
chmod 0600 "$SSH_CONFIG_DIR/id_rsa"
if (: "${CHECKOUT_KEY_PUBLIC?}") 2>/dev/null; then
  rm -f "$SSH_CONFIG_DIR/id_rsa.pub"
  printf "%s" "$CHECKOUT_KEY_PUBLIC" > "$SSH_CONFIG_DIR/id_rsa.pub"
fi

export GIT_SSH_COMMAND='ssh -i "$SSH_CONFIG_DIR/id_rsa" -o UserKnownHostsFile="$SSH_CONFIG_DIR/known_hosts"'

# use git+ssh instead of https
git config --global url."ssh://git@github.com".insteadOf "https://github.com" || true
git config --global gc.auto 0 || true

if [ -e '/home/circleci/project/.git' ] ; then
  echo 'Fetching into existing repository'
  existing_repo='true'
  cd '/home/circleci/project'
  git remote set-url origin "$CIRCLE_REPOSITORY_URL" || true
else
  echo 'Cloning git repository'
  existing_repo='false'
  mkdir -p '/home/circleci/project'
  cd '/home/circleci/project'
  git clone --no-checkout "$CIRCLE_REPOSITORY_URL" .
fi

if [ "$existing_repo" = 'true' ] || [ 'false' = 'true' ]; then
  echo 'Fetching from remote repository'
  if [ -n "$CIRCLE_TAG" ]; then
    git fetch --force --tags origin
  else
    git fetch --force origin +refs/heads/circleci-with-docker:refs/remotes/origin/circleci-with-docker
  fi
fi

if [ -n "$CIRCLE_TAG" ]; then
  echo 'Checking out tag'
  git checkout "$CIRCLE_TAG"
  git reset --hard "$CIRCLE_SHA1"
else
  echo 'Checking out branch'
  git checkout -B "$CIRCLE_BRANCH" "$CIRCLE_SHA1"
  git --no-pager log --no-color -n 1 --format='HEAD is now at %h %s'
fi
