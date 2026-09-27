ARG PYTHON_IMAGE=python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e
FROM ${PYTHON_IMAGE} AS builder

ARG MACS3_VERSION=3.0.5
ARG MACS3_COMMIT=c5443190e3edfeb301cc94acf450e2b2c026a223
ARG MACS3_SDIST_URL=https://files.pythonhosted.org/packages/b2/4b/d228c770577e48a11bdad778130590f0f68e7659e3d5bafa1bdef7ce25ad/macs3-3.0.5.tar.gz
ARG MACS3_SDIST_SHA256=22cb5e22903ef0598e8078cc19d4593cb43be43870808335c98e0f7298597224
ENV DEBIAN_FRONTEND=noninteractive PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=120 PIP_RETRIES=5 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
RUN apt-get -o Acquire::Retries=5 update \
 && apt-get -o Acquire::Retries=5 install -y --no-install-recommends build-essential zlib1g-dev curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/macs3/venv
ENV PATH=/opt/macs3/venv/bin:${PATH}
COPY docker/requirements.txt /tmp/requirements.txt
RUN python -m pip install pip==26.1.1 setuptools==82.0.1 wheel==0.47.0 \
 && python -m pip install -r /tmp/requirements.txt
WORKDIR /tmp/build
RUN set -eu; \
    curl --retry 5 --retry-all-errors -fsSL "${MACS3_SDIST_URL}" -o macs3.tar.gz; \
    echo "${MACS3_SDIST_SHA256}  macs3.tar.gz" | sha256sum -c -; \
    mkdir source; tar -xzf macs3.tar.gz -C source --strip-components=1; \
    python -m pip install --no-build-isolation --no-deps ./source; \
    python -m pip check; \
    mkdir -p /opt/macs3/share/doc/macs3 /opt/macs3/share/licenses/macs3; \
    cp source/README.md source/ChangeLog source/pyproject.toml source/setup.py /opt/macs3/share/doc/macs3/; \
    cp source/LICENSE /opt/macs3/share/licenses/macs3/; \
    tar -czf /opt/macs3/share/licenses/macs3/fermi-lite-source.tar.gz -C source/MACS3 fermi-lite; \
    printf 'version=%s\ncommit=%s\nsource=%s\nsource_sha256=%s\n' \
      "${MACS3_VERSION}" "${MACS3_COMMIT}" "${MACS3_SDIST_URL}" "${MACS3_SDIST_SHA256}" \
      > /opt/macs3/share/doc/macs3/source.txt; \
    rm -rf /tmp/build
COPY docker/prune.py /tmp/prune.py
RUN python /tmp/prune.py \
 && python -m pip check

FROM ${PYTHON_IMAGE}
ENV DEBIAN_FRONTEND=noninteractive PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
    PATH=/opt/macs3/venv/bin:${PATH} \
    MACS3_HOME=/opt/macs3 MACS3_TESTDATA=/opt/macs3/share/testdata
RUN apt-get -o Acquire::Retries=5 update \
 && apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
      bash ca-certificates gzip libgomp1 libstdc++6 zlib1g r-base-core \
 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/macs3 /opt/macs3
COPY docker/macs3_smoke.py docker/smoke.py /opt/macs3/share/testdata/
WORKDIR /tmp
# Build gates deliberately exclude HMM fitting, R rendering and large-data accuracy checks.
RUN python /opt/macs3/share/testdata/smoke.py identity \
 && python /opt/macs3/share/testdata/smoke.py imports \
 && python /opt/macs3/share/testdata/smoke.py peaks
ENV TAFFISH_ENV=TAFFISH TAFFISH_NAME=macs3
