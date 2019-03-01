FROM debian:stretch AS builder

RUN apt-get -y update && apt-get -y install curl zip virtualenv make

# install proto3
RUN curl -Lfs https://github.com/google/protobuf/releases/download/v3.1.0/protoc-3.1.0-linux-x86_64.zip -o protoc3.zip && \
  unzip protoc3.zip -d protoc3 && \
  mv protoc3/bin/protoc /usr/bin/protoc && \
  chmod a+rx /usr/bin/protoc && \
  cp -r protoc3/include/google /usr/include/ && \
  chmod -R a+Xr /usr/include/google && \
  rm -rf protoc3.zip protoc3

COPY orc8r /magma/orc8r
COPY protos /magma/protos

ENV MAGMA_ROOT /magma
ENV PYTHON_BUILD /build/python
ENV PIP_CACHE_HOME ~/.pipcache

WORKDIR /magma/orc8r/gateway/python
RUN make protos

FROM debian:stretch AS magmapi

RUN apt-get -y update && apt-get -y install \
  python3-pip \
  python-babel \
  python-dev \
  pkg-config \
  python-protobuf \
  libsystemd-dev \ 
  libffi-dev \
  python3-cffi \
  systemd \
  libssl-dev

# Install python module dependencies.
COPY orc8r/gateway/python /tmp/orc8r
RUN pip3 install /tmp/orc8r

#COPY orc8r/gateway/python/magma /usr/local/lib/python3.5/dist-packages/
COPY --from=builder /build/python/gen /usr/local/lib/python3.5/dist-packages/
COPY example/gateway/configs/ /etc/magma

# Install supervisord
RUN apt-get install -y supervisor
COPY orc8r/gateway/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]
