# macs3

`macs3` packages MACS3, the current MACS command-line suite for ChIP-seq,
ATAC-seq, and other DNA enrichment peak-calling workflows, for TAFFISH.

Package identity:

- name: `macs3`
- command: `taf-macs3`
- kind: `tool`
- version: `3.0.4-r1`
- license: Apache-2.0 for the TAFFISH packaging
- upstream: <https://github.com/macs3-project/MACS>

## What This App Packages

This app installs MACS3 3.0.4 from the official PyPI source distribution, pinned
by SHA256, with the GitHub upstream tag `v3.0.4` recorded for update tracking.
The packaged default command is `macs3`.

MACS3 is a peak-calling and bedGraph analysis toolkit. It can call narrow and
broad peaks, operate on bedGraph tracks, estimate fragment size, pile up reads,
sample reads, refine peaks, call variants in peak regions, and run the HMMRATAC
ATAC-seq mode.

## Scope

This app supports the upstream MACS3 command surface, including:

- `macs3 callpeak`
- `macs3 bdgpeakcall`
- `macs3 bdgbroadcall`
- `macs3 bdgcmp`
- `macs3 bdgopt`
- `macs3 cmbreps`
- `macs3 bdgdiff`
- `macs3 filterdup`
- `macs3 predictd`
- `macs3 pileup`
- `macs3 randsample`
- `macs3 refinepeak`
- `macs3 callvar`
- `macs3 hmmratac`

This app does not align reads, sort or index BAM files, provide reference
genomes, download public datasets, choose an experimental design, or validate
peak-calling parameters for a specific assay.

## Container Contents

- `macs3`: MACS3 3.0.4 command-line suite.
- `python`: Python 3.10 runtime with MACS3 and its scientific Python
  dependencies.
- Python packages: NumPy 1.26.4, SciPy 1.13.1, scikit-learn 1.5.2, hmmlearn
  0.3.3, and cykhash 2.0.1.
- Upstream license, README, ChangeLog, package metadata, and pinned package
  list under `/opt/macs3/share/doc/macs3`.

## Usage

Access upstream help:

```sh
taf-macs3 -- --help
taf-macs3 macs3 --help
taf-macs3 macs3 callpeak --help
```

Narrow peak calling:

```sh
taf-macs3 macs3 callpeak -t chip.bam -c control.bam -f BAM -g hs -n chip -B -q 0.01
```

Broad peak calling:

```sh
taf-macs3 macs3 callpeak -t histone.bam -c input.bam --broad -g hs --broad-cutoff 0.1
```

ATAC-seq paired-end peak calling:

```sh
taf-macs3 macs3 callpeak -f BAMPE -t atac.bam -g hs -n atac -B -q 0.01
```

HMMRATAC mode:

```sh
taf-macs3 macs3 hmmratac -i atac.bam -f BAMPE -n atac_hmm
```

Call peaks from a bedGraph track:

```sh
taf-macs3 macs3 bdgpeakcall -i signal.bdg -c 5 -l 200 -g 100 -o peaks.bed
```

## Command Mode

TAFFISH command mode is enabled. Because MACS3 uses subcommands, normal
subcommand calls should use the explicit upstream command form:

```sh
taf-macs3 macs3 callpeak ...
taf-macs3 macs3 bdgcmp ...
taf-macs3 macs3 hmmratac ...
```

The `taf-macs3 -- --help` form is mainly for option-leading arguments passed to
the default `macs3` command. A call such as `taf-macs3 callpeak ...` would be
interpreted as command mode and try to run an executable named `callpeak`.

## Inputs

| Input | Meaning | Notes |
| --- | --- | --- |
| BAM/SAM/BED/ELAND/Bowtie/BAMPE/BEDPE/FRAG | Read alignment or fragment input | Accepted formats depend on the selected MACS3 subcommand. |
| bedGraph | Signal track input | Used by `bdgpeakcall`, `bdgbroadcall`, `bdgcmp`, `bdgopt`, `cmbreps`, and `bdgdiff`. |
| genome size | Effective genome size or alias | Common aliases such as `hs`, `mm`, and explicit numeric sizes are handled by upstream MACS3. |
| barcode list | Optional scATAC FRAG restriction | Used by MACS3 3.0.4 `hmmratac` with FRAG input. |

## Output Notes

Outputs are subcommand-specific. `callpeak` commonly writes `*_peaks.xls`,
`*.narrowPeak`, `*.broadPeak`, `*_summits.bed`, and optional treatment/control
bedGraph files. bedGraph subcommands write BED-like or bedGraph-like tracks.
`hmmratac` writes ATAC peak and state outputs according to upstream options.

## Resources, Databases, and Platform

No production database or reference bundle is packaged. MACS3 normally runs
offline once the user provides alignment, fragment, bedGraph, genome-size, and
other input files. The container does not need a network connection for normal
analysis.

This app is declared for native `linux/amd64` and `linux/arm64` builds. Upstream
MACS3 documents testing on x86_64 and aarch64, but also warns that `hmmratac`
results on non-x86 Linux architectures can differ because of scientific
calculation library behavior. For strict cross-platform reproducibility of
`hmmratac`, compare results on the same architecture.

## Boundaries

This app packages MACS3 itself. It does not include aligners, read mappers,
workflow logic, genome FASTA files, blacklists, spike-in normalization, sample
metadata handling, replicate consensus logic, QC reporting, or downstream
annotation/visualization tools.

## Testing

The container build and smoke tests cover:

- MACS3 version, top-level help, and representative subcommand help.
- Python runtime imports for MACS3, NumPy, SciPy, scikit-learn, hmmlearn, and
  cykhash.
- Dynamic library completeness for compiled Python extensions.
- A tiny synthetic `callpeak` run that writes MACS3 peak-calling outputs and
  treatment pileup bedGraph.
- A tiny synthetic `bdgpeakcall` run that calls peaks from bedGraph input.

The smoke tests do not benchmark sensitivity, compare biological peak quality,
or validate assay-specific parameter choices on production data.

## License and Citation

TAFFISH app packaging: Apache-2.0.

Upstream MACS3 software: BSD-3-Clause. Bundled Python packages keep their own
license terms.

Please cite MACS according to upstream guidance:

Zhang et al. 2008. Model-based Analysis of ChIP-Seq (MACS). Genome Biology.
DOI: `10.1186/gb-2008-9-9-r137`.

## Upstream Links

- Documentation: <https://macs3-project.github.io/MACS/>
- Source repository: <https://github.com/macs3-project/MACS>
- Release: <https://github.com/macs3-project/MACS/releases/tag/v3.0.4>
- PyPI package: <https://pypi.org/project/MACS3/3.0.4/>
