FROM alpine:3.9
COPY id_rsa id_rsa
RUN chmod 400 id_rsa
RUN apk add --no-cache \
  openssh-client \
  ca-certificates \
  bash