# macs3

`macs3` packages MACS3 **3.1.0-r1** for TAFFISH, retaining the upstream CLI
and Python API. MACS identifies enrichment peaks in ChIP-seq/ATAC-seq and other
DNA-enrichment assays; it is not an aligner or a complete analysis workflow.

## What This App Packages

- Command: `taf-macs3`; thin two-line tool wrapper with automatic command mode.
- Official [v3.1.0](https://github.com/macs3-project/MACS/releases/tag/v3.1.0),
  commit `81761ed60a985cd817aca862f8b0402fafaeb11f`.
- Verified [PyPI source distribution](https://pypi.org/project/MACS3/3.1.0/):
  SHA256 `aae548b86ab652717dca281fa2e33645fc1dc8091264ccbf7ce09cf8a13532e0`.
- Image: `ghcr.io/taffish/macs3:3.1.0-r1`; runtime: `macs3 3.1.0`.
- Native `linux/amd64` and `linux/arm64`; no emulation flags or upstream patches.
- Python 3.12.14 from a digest-pinned multi-platform official image, compiled
  MACS3 extensions (including bundled fermi-lite/SIMDe), NumPy 2.2.6, SciPy
  1.15.3, pandas 2.2.3, AnnData 0.11.4, scikit-learn 1.6.1 and hmmlearn 0.3.3.
  Full pins: [requirements.txt](docker/requirements.txt).
- Base R/Rscript for upstream-generated peak-model PDF scripts; gzip and zlib
  for compressed data. No external samtools is needed by MACS3's internal BAM reader.
- Stable dependency inventory and source record in `/opt/macs3/share/doc/macs3`;
  licenses in `/opt/macs3/share/licenses/macs3`, Python package metadata and
  Debian `/usr/share/doc`. Embedded third-party source archive preserves its notices.

## Scope

The complete upstream command set is retained: callpeak, bdgpeakcall, bdgbroadcall,
bdgcmp, bdgopt, bdgdiff, cmbreps, filterdup, predictd, pileup, randsample,
refinepeak, callvar and hmmratac. New sparse barcode-by-peak AnnData export is
available through `PETrackII.return_anndata(regions)`; h5ad writing/reading is included.

Not bundled: aligners, production inputs, genome references/blacklists,
pretrained HMMs, a Jupyter/Scanpy analysis environment or genome browsers.
No normal analysis command downloads these implicitly.

GUI discovery checked v3.1.0 pyproject/setup, official installation and the
[notebook examples](https://github.com/macs3-project/MACS/tree/v3.1.0/notebooks).
There are no MACS3 GUI/server entry points, package extras or linked dedicated
viewer. The PBMC notebooks are tutorials executing the same Python API inside
a general Jupyter environment; their Scanpy/matplotlib downstream exploration
is not a MACS3 service. This app preserves the CLI/API contract, not an
interactive notebook distribution. Use your separate notebook/Scanpy environment
to explore exported h5ad files. The packaged R path produces static PDFs,
viewed on the host; no browser service, ports or noVNC lifecycle is involved.

## Installation and Usage

Install the published version via `taf install macs3`. From a directory containing inputs:

```sh
taf-macs3 --help
taf-macs3 -- --help
taf-macs3 -- --version
taf-macs3 macs3 callpeak -t chip.bam -c input.bam -f BAM -g hs -n sample --outdir results
taf-macs3 macs3 callpeak -t fragments.bam -f BAMPE -g hs -n atac --outdir results-atac
taf-macs3 macs3 bdgpeakcall -i signal.bdg -c 5 -l 200 -g 30 -o peaks.bed
taf-macs3 python analysis.py
taf-macs3 Rscript --vanilla model.R
```

Select your effective genome size; `hs` is an example, not a universal default.
For upstream subcommands always include `macs3`: `taf-macs3 callpeak ...`
would instead request an executable called callpeak. Wrapper `--help` and
`--version` differ from upstream `-- --help` and `-- --version`.
Current TAFFISH command mode constructs a shell line: paths with spaces require
literal quotes, for example `taf-macs3 macs3 bdgpeakcall -i '"signal with spaces.bdg"' -o peaks.bed`.
Use simple names for sample labels embedded by upstream in generated R code.

### CPU Budget (3.1.0)

Use `--threads N` on callpeak, predictd, pileup, filterdup, randsample,
refinepeak, hmmratac or callvar. The upstream `MACS3_NUM_THREADS` environment
variable provides a default; for a single container invocation use command mode:

    taf-macs3 env MACS3_NUM_THREADS=2 macs3 callpeak -t reads.bed -f BED -g 1000 --nomodel --outdir peaks

An explicit `--threads` overrides that default. callpeak and callvar also accept
`--process-backend auto` (default) or `serial`. These CPU controls have the
same CLI on all three backends. The packaged BLAS/OpenMP limits prevent
library oversubscription; MACS3's own execution policy remains explicit.
Upstream speedups are workload-specific; more workers can increase memory use.

## Inputs and Outputs

- BED is zero-based; BAM is parsed internally. Use BAMPE for paired-end fragments.
- MACS3 BEDPE is **three columns**, not BEDTools' ten-column BEDPE.
- FRAG is the five-column 10x fragment format (chromosome, start, end, barcode,
  count); gzip input is supported and `--barcodes` selects a subset.
- Control alignments are optional; `-g`, model/shift settings, duplicates and
  thresholds are scientific choices. MACS2-era defaults should not be assumed.
- callpeak writes peaks.xls, narrowPeak/summits or broadPeak/gappedPeak;
  `-B` requests pileup/control bedGraphs. Genome tracks are not browser sessions.
- predictd/model-enabled callpeak may write an R script; execute Rscript in a
  writable output directory. `--nomodel` does not generate a model plot.
- hmmratac's `--cutoff-analysis-only` writes a TSV and now exits successfully;
  assess it before selecting `-l/-u/-c`. `--jump` defaults to 0.5.
  `--modelonly` writes a trained JSON; `--model` reuses it.
- Output filenames may be overwritten by upstream. Use a new output name/directory.
  Scratch and Python/R temporary files belong in /tmp, not the installed prefix.

## Resources, Databases, and Platform

Resource classification: alignments, cell lists, genome sizes, blacklist BEDs,
training regions and trained HMM JSONs are **project-specific inputs**, not members
of a downloadable MACS3 pretrained-model catalog. v3.1.0 has no official model/
database downloader or catalog. There is consequently no automatic installer,
root-once download, auto-discovery, override or disable helper: choosing a model
automatically could silently select a scientifically inappropriate assay/genome.

A team can nevertheless prepare a model once and reuse it read-only.
Recommended layouts are `~/.local/share/taffish/models/macs3/PROJECT/VERSION/`,
`/usr/local/share/taffish/models/macs3/PROJECT/VERSION/` or
`/opt/taffish/models/macs3/PROJECT/VERSION/`. The administrator copies an already
trained, approved model (not a generic model obtained from this app), records
its SHA256, MACS3/dependency versions, assay/genome, training parameters and
input provenance. Use administrator ownership, traversable 0755 directories
and readable 0644 files; ordinary users need read, not write, access.
Never change shared system permissions as part of an analysis run.
Resource sharing/redistribution follows the source data/model's own terms:
the software's BSD license does not grant rights to third-party references
or 10x tutorial data. Download/project license validation is the data owner's responsibility.

Each invocation explicitly selects its JSON. Resolve symlinks to a physical
root; a read-only bind exposes only that root, while outputs remain in the
working-directory bind. For example set
`MODEL_ROOT=/opt/taffish/models/macs3/PROJECT/VERSION`, then use:

| Backend | Optional site policy for this invocation |
| --- | --- |
| Docker | `TAFFISH_CONTAINER_BACKEND=docker TAFFISH_DOCKER_RUN_ARGS="-v $MODEL_ROOT:/models:ro" taf-macs3 macs3 hmmratac -i atac.bam --model /models/model.json -n reuse --outdir reuse` |
| Podman | `TAFFISH_CONTAINER_BACKEND=podman TAFFISH_PODMAN_RUN_ARGS="-v $MODEL_ROOT:/models:ro" taf-macs3 macs3 hmmratac -i atac.bam --model /models/model.json -n reuse --outdir reuse` |
| Apptainer | `TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_APPTAINER_RUN_ARGS="--bind $MODEL_ROOT:/models:ro" taf-macs3 macs3 hmmratac -i atac.bam --model /models/model.json -n reuse --outdir reuse` |

No model root is required for ordinary peak calling. Missing/bad explicit input
fails rather than downloading a replacement. Local project paths inside the
working directory are the simplest alternative to the optional bind.

## Backend Capability and Validation

The 3.1.0-r1 candidate passed fresh native builds from the repository-root
context. The following results are from this candidate, not inherited receipts.

| Native platform | Docker | Podman | Apptainer |
| --- | --- | --- | --- |
| linux/amd64 (xjp) | PASS: exact + wrapper | PASS: exact + wrapper | PASS: actual read-only SIF from the same candidate OCI + wrapper |
| linux/arm64 | PASS: exact + wrapper | PASS: exact + wrapper | Not separately validated |

All 221 independent exact probes passed: combined/individual existence probes,
every manifest test, Docker/Podman normal/read-only/non-root roots, and actual SIF.
The five completed wrapper combinations each passed 29 calls plus four supplementary
checks: project-model read-only binds, denied writes, spaces, ownership, HMM reuse,
BAMPE/callvar, gzip, PDFs, CPU policy, recovery/repeat reuse and truncated BAM.
Five native upstream PDFs (two pages each) rendered to identical page pixels;
both pages were visually checked. No upstream plot template was modified.

The initial ARM64 Docker wrapper run stopped when Docker Desktop reported
"unable to start". After a maintainer-authorized Docker Desktop restart, the
same image and byte-identical wrapper passed all 29 calls and four supplementary
checks. The original failure evidence is retained; it is not counted as a PASS.
No app code, version, Action or other container engine was changed for this retest.

Native platform and backend evidence are tracked separately. The untested
arm64/Apptainer combination is not a PASS claim; there is no backend-specific
architecture/device/service path in this app requiring that combination.
HMM training must be checked on both native architectures. HMM floating-point
training/decoding can differ across CPU/library platforms; no bit-identical
scientific output promise is made. Apptainer requires native Linux; a Mac is
not an Apptainer runner. The app has no GPU/device/service options.

## Troubleshooting

- Empty peaks: check input format, effective genome size and cutoffs rather than
  assuming container failure. Sparse data may not support peak-model fitting.
- R script absent: `--nomodel` or insufficient symmetric peaks can explain this.
- Model reuse fails: verify JSON identity and assay compatibility, path visibility
  and read permission; do not grant model directories write permission.
- Read-only output error: put outputs in the working directory, not /opt or /models.
- Missing zarr/Scanpy/Jupyter: those independent analysis frontends/formats are not
  this app's contract; export h5ad and use a dedicated downstream environment.
- Host stdin is not forwarded to a Python command by the tested TAFFISH 0.11.0
  container heredoc. Use mounted input files for such scripts. This is a core
  command-transport boundary, not a MACS3 parser patch; ordinary stdout capture
  and file-based MACS3 workflows are tested.

## Testing and Packaging Boundary

[smoke] tests run independently without network: identity/all command help,
compiled extension imports, tiny summit/bedGraph calls, AnnData count preservation
and h5ad roundtrip, HMM save/load/decode and cutoff-only, upstream R exporter
to PDF, and serial/auto calling of a two-chromosome FRAG with no trailing newline.
Dockerfile executes only identity/import/tiny peak gates; no numerical
HMM golden matrix or graphics stack is tested at build time.

Python compiler headers/static archives/bytecode are removed before copying the
runtime prefix into the final stage. Non-runtime pandas/SciPy/scikit-learn test
suites are removed, while NumPy's test tree is retained because its testing API
imports it at runtime. Runtime modules/data, package metadata and notices are
retained. Final image sizes: amd64 502.79 MiB (527,208,424 bytes), arm64
517.95 MiB (543,105,205 bytes). Runtime /opt/macs3 occupies 284 MiB/276 MiB
respectively; base R is 34 MiB. Installed package inventories and pip check
passed, and final imports/function tests ran after pruning.

Source drift: the base digest and sdist SHA256 identify inputs but do not
guarantee permanent download availability. APT follows active Bookworm, and
requirements.txt pins package versions rather than wheel bytes. The installed
inventory is not an input lock. Recover old material only with matching trusted
identities; adopting new material requires a new validated candidate. Never
bypass checksums/TLS or blindly recalculate a mismatched source hash.

Tests are packaging checks, not a full benchmark, production PBMC/ChIP-seq
scientific acceptance or a claim of bitwise HMM reproducibility across architectures.

## License and Citation

Packaging: Apache-2.0. MACS3: BSD-3-Clause. Embedded fermi-lite/SIMDe and Python/R
components retain their own licenses and notices.
MACS3's current citation is [MACS3: A Peak-calling Platform for Bulk and Single-cell
Regulatory Genomics (2026)](https://doi.org/10.1093/gpbjnl/qzag097).
The 2008 MACS1 paper is not the sole citation recommended for MACS3.
