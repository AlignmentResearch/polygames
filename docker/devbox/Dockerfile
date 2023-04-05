ARG POLYGAMES_VERSION
FROM ghcr.io/alignmentresearch/polygames:${POLYGAMES_VERSION}-runner
LABEL org.opencontainers.image.source=https://github.com/AlignmentResearch/polygames

# Remote development niceties:
## Alacritty terminal, ssh keys dir
RUN wget https://github.com/alacritty/alacritty/releases/download/v0.11.0/alacritty.info \
    && tic -xe alacritty,alacritty-direct alacritty.info \
    && rm alacritty.info \
    && mkdir /run/sshd

WORKDIR "${HOME}/.ssh"
ARG SSH_KEY
RUN echo "${SSH_KEY}" > "${HOME}/.ssh/authorized_keys"

## Unison synchronizer
RUN wget https://github.com/bcpierce00/unison/releases/download/v2.53.2/unison-v2.53.2+ocaml-4.14.1+x86_64.linux.tar.gz \
    && mkdir unison-work \
    && tar xf unison-v2.53.2+ocaml-4.14.1+x86_64.linux.tar.gz -C unison-work \
    && mv unison-work/bin/unison* /usr/local/bin \
    && rm -rf unison*
