ARG MACS3_VERSION=3.0.4
ARG MACS3_TAG=v3.0.4
ARG MACS3_COMMIT=e8ff0409e11d743d00c12ef44361f19ea5df9161
ARG MACS3_SDIST_URL=https://files.pythonhosted.org/packages/d5/fc/7c5e99b12260372918521d52e3749b14ffc277b092a959bbe04550425e49/macs3-3.0.4.tar.gz
ARG MACS3_SDIST_SHA256=1c2c9cc219d136b026b5e517dcbc518c3f76b9c864b8b52f00c7902f11070aef
ARG PYTHON_VERSION=3.10
ARG PIP_INDEX_URL=https://pypi.org/simple

FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

ARG MACS3_VERSION
ARG MACS3_TAG
ARG MACS3_COMMIT
ARG MACS3_SDIST_URL
ARG MACS3_SDIST_SHA256
ARG PYTHON_VERSION
ARG PIP_INDEX_URL

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DEFAULT_TIMEOUT=120
ENV PIP_RETRIES=5
ENV PIP_INDEX_URL=${PIP_INDEX_URL}
ENV PYTHONNOUSERSITE=1
ENV OPENBLAS_NUM_THREADS=1
ENV OMP_NUM_THREADS=1

RUN set -eux; \
    for attempt in 1 2 3 4 5; do \
      if apt-get -o Acquire::Retries=5 update \
       && apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
            bash \
            build-essential \
            ca-certificates \
            curl \
            gzip \
            libc-bin \
            libgomp1 \
            tar \
            zlib1g-dev; then \
        break; \
      fi; \
      if [ "$attempt" = "5" ]; then exit 1; fi; \
      apt-get clean; \
      rm -rf /var/lib/apt/lists/*; \
      sleep 5; \
    done; \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    python -m venv /opt/macs3/venv

ENV PATH=/opt/macs3/venv/bin:${PATH}
ENV LD_LIBRARY_PATH=/opt/macs3/venv/lib/python3.10/site-packages/numpy.libs:/opt/macs3/venv/lib/python3.10/site-packages/scipy.libs:/opt/macs3/venv/lib/python3.10/site-packages/scikit_learn.libs

WORKDIR /tmp/build

RUN set -eux; \
    python -m pip install --upgrade \
      "pip==26.1.1" \
      "setuptools==82.0.1" \
      "wheel==0.47.0"; \
    python -m pip install \
      "Cython==3.0.12" \
      "numpy==1.26.4" \
      "scipy==1.13.1" \
      "scikit-learn==1.5.2" \
      "hmmlearn==0.3.3" \
      "cykhash==2.0.1"; \
    curl --retry 5 --retry-delay 2 --retry-all-errors -fsSL \
      "${MACS3_SDIST_URL}" \
      -o macs3.tar.gz; \
    echo "${MACS3_SDIST_SHA256}  macs3.tar.gz" | sha256sum -c -; \
    mkdir source; \
    tar -xzf macs3.tar.gz -C source --strip-components=1; \
    python -m pip install --no-build-isolation --no-deps ./source; \
    python -m pip check; \
    mkdir -p /opt/macs3/share/doc/macs3 /opt/macs3/share/licenses/macs3 /opt/macs3/share/testdata; \
    cp -a source/README.md source/ChangeLog source/pyproject.toml source/setup.py /opt/macs3/share/doc/macs3/; \
    cp -a source/LICENSE /opt/macs3/share/licenses/macs3/LICENSE; \
    python -m pip freeze --all | sort > /opt/macs3/share/doc/macs3/python-packages.txt; \
    { \
      printf "name=MACS3\n"; \
      printf "version=%s\n" "${MACS3_VERSION}"; \
      printf "tag=%s\n" "${MACS3_TAG}"; \
      printf "commit=%s\n" "${MACS3_COMMIT}"; \
      printf "source=%s\n" "${MACS3_SDIST_URL}"; \
      printf "source_sha256=%s\n" "${MACS3_SDIST_SHA256}"; \
      printf "repo=https://github.com/macs3-project/MACS\n"; \
      printf "runtime_install=PyPI source distribution installed with pip --no-build-isolation --no-deps after pinned Python dependencies\n"; \
      printf "python=%s\n" "${PYTHON_VERSION}"; \
      printf "numpy=1.26.4\n"; \
      printf "scipy=1.13.1\n"; \
      printf "scikit-learn=1.5.2\n"; \
      printf "hmmlearn=0.3.3\n"; \
      printf "cykhash=2.0.1\n"; \
    } > /opt/macs3/share/doc/macs3/source.txt; \
    macs3 --version 2>&1 | grep -F "${MACS3_VERSION}" >/dev/null; \
    macs3 --help 2>&1 | grep -F "callpeak" >/dev/null; \
    python -c 'import importlib.metadata as md; import MACS3, numpy, scipy, sklearn, hmmlearn, cykhash; assert md.version("MACS3") == "3.0.4"'; \
    find /opt/macs3/venv -type f -name '*.so' -print0 | xargs -0 -r ldd > /tmp/macs3-ldd.txt; \
    if grep -F "not found" /tmp/macs3-ldd.txt; then exit 1; fi; \
    rm -rf /tmp/build

COPY docker/macs3_smoke.py /opt/macs3/share/testdata/macs3_smoke.py

RUN set -eux; \
    chmod 0755 /opt/macs3/share/testdata/macs3_smoke.py; \
    tmp=/tmp/taf-macs3-builder-check; \
    rm -rf "$tmp"; \
    mkdir -p "$tmp"; \
    python /opt/macs3/share/testdata/macs3_smoke.py "$tmp"; \
    cd "$tmp"; \
    macs3 callpeak -t reads.bed -f BED -g 1000 -n smoke --outdir callpeak --nomodel --extsize 50 --shift 0 --keep-dup all -B --nolambda -p 0.99 > callpeak.log 2>&1; \
    test -s callpeak/smoke_peaks.xls; \
    test -s callpeak/smoke_treat_pileup.bdg; \
    grep -F "chr1" callpeak/smoke_treat_pileup.bdg >/dev/null; \
    grep -F "Done!" callpeak.log >/dev/null; \
    macs3 bdgpeakcall -i signal.bdg -c 5 -l 20 -g 10 -o peaks.bed > bdgpeakcall.log 2>&1; \
    test -s peaks.bed; \
    grep -F "chr1" peaks.bed >/dev/null; \
    rm -rf "$tmp"

FROM python:${PYTHON_VERSION}-slim-bookworm

ARG MACS3_VERSION
ARG PYTHON_VERSION

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONNOUSERSITE=1
ENV OPENBLAS_NUM_THREADS=1
ENV OMP_NUM_THREADS=1
ENV PATH=/opt/macs3/venv/bin:${PATH}
ENV LD_LIBRARY_PATH=/opt/macs3/venv/lib/python3.10/site-packages/numpy.libs:/opt/macs3/venv/lib/python3.10/site-packages/scipy.libs:/opt/macs3/venv/lib/python3.10/site-packages/scikit_learn.libs
ENV MACS3_HOME=/opt/macs3
ENV MACS3_TESTDATA=/opt/macs3/share/testdata

RUN set -eux; \
    for attempt in 1 2 3 4 5; do \
      if apt-get -o Acquire::Retries=5 update \
       && apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
            bash \
            ca-certificates \
            gzip \
            libc-bin \
            libgomp1 \
            libstdc++6 \
            zlib1g \
            grep \
            sed; then \
        break; \
      fi; \
      if [ "$attempt" = "5" ]; then exit 1; fi; \
      apt-get clean; \
      rm -rf /var/lib/apt/lists/*; \
      sleep 5; \
    done; \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/macs3 /opt/macs3

WORKDIR /data

RUN set -eux; \
    command -v macs3 >/dev/null; \
    command -v python >/dev/null; \
    command -v python3 >/dev/null; \
    command -v bash >/dev/null; \
    command -v gzip >/dev/null; \
    command -v ldd >/dev/null; \
    macs3 --version 2>&1 | grep -F "${MACS3_VERSION}" >/dev/null; \
    macs3 --help 2>&1 | grep -F "callpeak" >/dev/null; \
    macs3 --help 2>&1 | grep -F "hmmratac" >/dev/null; \
    macs3 callpeak --help 2>&1 | grep -F "callpeak" >/dev/null; \
    macs3 bdgpeakcall --help 2>&1 | grep -F "bdgpeakcall" >/dev/null; \
    macs3 hmmratac --help 2>&1 | grep -F "hmmratac" >/dev/null; \
    python -c 'import importlib.metadata as md; import MACS3, numpy, scipy, sklearn, hmmlearn, cykhash; assert md.version("MACS3") == "3.0.4"; print("macs3-runtime-ok")' | grep -F "macs3-runtime-ok" >/dev/null; \
    test -s /opt/macs3/share/doc/macs3/source.txt; \
    test -s /opt/macs3/share/doc/macs3/python-packages.txt; \
    test -s /opt/macs3/share/licenses/macs3/LICENSE; \
    tmp=/tmp/taf-macs3-runtime-check; \
    rm -rf "$tmp"; \
    mkdir -p "$tmp"; \
    python /opt/macs3/share/testdata/macs3_smoke.py "$tmp"; \
    cd "$tmp"; \
    macs3 callpeak -t reads.bed -f BED -g 1000 -n smoke --outdir callpeak --nomodel --extsize 50 --shift 0 --keep-dup all -B --nolambda -p 0.99 > callpeak.log 2>&1; \
    test -s callpeak/smoke_peaks.xls; \
    test -s callpeak/smoke_treat_pileup.bdg; \
    grep -F "chr1" callpeak/smoke_treat_pileup.bdg >/dev/null; \
    macs3 bdgpeakcall -i signal.bdg -c 5 -l 20 -g 10 -o peaks.bed > bdgpeakcall.log 2>&1; \
    test -s peaks.bed; \
    grep -F "chr1" peaks.bed >/dev/null; \
    cd /data; \
    rm -rf "$tmp"; \
    find /opt/macs3/venv -type f -name '*.so' -print0 | xargs -0 -r ldd > /tmp/macs3-ldd.txt; \
    if grep -F "not found" /tmp/macs3-ldd.txt; then exit 1; fi; \
    rm -f /tmp/macs3-ldd.txt

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=macs3
