ARG PYTHON_IMAGE=python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e
FROM ${PYTHON_IMAGE} AS builder

ARG MACS3_VERSION=3.1.0
ARG MACS3_COMMIT=81761ed60a985cd817aca862f8b0402fafaeb11f
ARG MACS3_SDIST_URL=https://files.pythonhosted.org/packages/d6/eb/3b32d38f8cbc8044043e4cdb53c1df26f627d483cb04642645dc65b8aa7e/macs3-3.1.0.tar.gz
ARG MACS3_SDIST_SHA256=aae548b86ab652717dca281fa2e33645fc1dc8091264ccbf7ce09cf8a13532e0
ENV DEBIAN_FRONTEND=noninteractive PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=120 PIP_RETRIES=5 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
# The base digest does not freeze Debian's active APT repositories. Diagnose
# network/index errors versus removed packages; any changed package closure
# needs a new verified build and all runtime gates, not relaxed checks.
RUN apt-get -o Acquire::Retries=5 update \
 && apt-get -o Acquire::Retries=5 install -y --no-install-recommends build-essential zlib1g-dev curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/macs3/venv
ENV PATH=/opt/macs3/venv/bin:${PATH}
COPY docker/requirements.txt /tmp/requirements.txt
# requirements.txt pins versions, not wheel bytes or perpetual availability.
# python-packages.txt is a post-install inventory, not an input lock. Check
# official versions/architecture/licenses before changing pins and revalidate.
RUN python -m pip install pip==26.1.1 setuptools==82.0.1 wheel==0.47.0 \
 && python -m pip install -r /tmp/requirements.txt
WORKDIR /tmp/build
# The fixed PyPI sdist can disappear. Restore only trusted bytes matching the
# recorded SHA256; a new source/hash is an update requiring full validation.
# Never bypass checksum/TLS checks or blindly recalculate a mismatched hash.
RUN set -eu; \
    curl --retry 5 --retry-all-errors -fsSL "${MACS3_SDIST_URL}" -o macs3.tar.gz; \
    echo "${MACS3_SDIST_SHA256}  macs3.tar.gz" | sha256sum -c -; \
    mkdir source; tar -xzf macs3.tar.gz -C source --strip-components=1; \
    python -m pip install --no-build-isolation --no-deps ./source; \
    python -m pip check; \
    mkdir -p /opt/macs3/share/doc/macs3 /opt/macs3/share/licenses/macs3; \
    cp source/README.md source/ChangeLog source/pyproject.toml source/setup.py /opt/macs3/share/doc/macs3/; \
    cp source/LICENSE /opt/macs3/share/licenses/macs3/; \
    cp source/MACS3/IO/libdeflate/COPYING /opt/macs3/share/licenses/macs3/libdeflate-COPYING; \
    cp source/MACS3/Signal/NUMPY_LICENSE.txt /opt/macs3/share/licenses/macs3/; \
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
# Runtime APT packages follow active Bookworm; the pinned base alone is not a
# complete offline rebuild guarantee (see builder notes above).
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
