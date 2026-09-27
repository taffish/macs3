taf-macs3 3.0.5-r1 — call enrichment peaks and process bedGraph signals.

Usage:
  taf-macs3 macs3 SUBCOMMAND [OPTIONS]
  taf-macs3 --help                Wrapper help
  taf-macs3 -- --help             Upstream help
  taf-macs3 -- --version          Upstream version

Quick start (run from your data directory):
  taf-macs3 macs3 callpeak -t chip.bam -c input.bam -f BAM \
    -g hs -n sample --outdir results
  Read results/sample_peaks.narrowPeak and results/sample_peaks.xls.
  Choose -g for your effective genome size; hs is not suitable for every genome.
  Use a new output directory/name to avoid overwriting earlier results.

Paired-end / single-cell:
  taf-macs3 macs3 callpeak -t fragments.bam -f BAMPE -g hs \
    -n atac --outdir results-atac
  For a 10x fragments.tsv.gz file use -f FRAG; --barcodes can select cells.
  MACS3 BEDPE means three columns: chromosome, fragment start, fragment end,
  not the ten-column BEDTools BEDPE format. BED coordinates are zero-based.
  AnnData export is a Python API: PETrackII.return_anndata(regions).
  Run your API script with: taf-macs3 python analysis.py

BedGraph and model plots:
  taf-macs3 macs3 bdgpeakcall -i signal.bdg -c 5 -l 200 -g 30 -o peaks.bed
  taf-macs3 macs3 SUBCOMMAND --help
  If callpeak/predictd generated a model.R file, render it with:
  taf-macs3 Rscript --vanilla model.R
  The generated PDF is viewed on the host; no display server is needed.

HMMRATAC:
  taf-macs3 macs3 hmmratac -i atac.bam -n pilot --outdir pilot \
    --cutoff-analysis-only
  Review the cutoff report before choosing training/decoding cutoffs.
  taf-macs3 macs3 hmmratac -i atac.bam -n sample --outdir hmm-results
  --jump controls fragment-length EM updates (default 0.5).
  Use --model FILE to reuse your trained model; --modelonly saves training.
  No pretrained model, blacklist or reference database is bundled/downloaded.
  Models are project-specific; verify assay, genome and training provenance.

Backend selection:
  export TAFFISH_CONTAINER_BACKEND=docker
  Or select podman or apptainer. Run the same commands above.
  Both linux/amd64 and linux/arm64 are native platforms.
  HMM floating-point results can differ across architectures.

Optional shared model outside the working directory (administrator-prepared):
  MODEL_ROOT=/opt/taffish/models/macs3/PROJECT/VERSION
  Docker:
    TAFFISH_CONTAINER_BACKEND=docker \
    TAFFISH_DOCKER_RUN_ARGS="-v $MODEL_ROOT:/models:ro" \
      taf-macs3 macs3 hmmratac -i atac.bam --model /models/model.json \
      -n reuse --outdir reuse
  Podman:
    TAFFISH_CONTAINER_BACKEND=podman \
    TAFFISH_PODMAN_RUN_ARGS="-v $MODEL_ROOT:/models:ro" \
      taf-macs3 macs3 hmmratac -i atac.bam --model /models/model.json \
      -n reuse --outdir reuse
  Apptainer (native Linux):
    TAFFISH_CONTAINER_BACKEND=apptainer \
    TAFFISH_APPTAINER_RUN_ARGS="--bind $MODEL_ROOT:/models:ro" \
      taf-macs3 macs3 hmmratac -i atac.bam --model /models/model.json \
      -n reuse --outdir reuse
  Prefer absolute paths without spaces for mount roots; outputs remain in the
  writable working directory. Use resolved physical paths for shared symlinks.
  No automatic model discovery: select the intended model explicitly.
  For spaces in ordinary arguments, retain literal quotes, e.g.:
    taf-macs3 macs3 bdgpeakcall -i '"signal with spaces.bdg"' -o peaks.bed

More help:
  https://github.com/taffish/macs3
  https://macs3-project.github.io/MACS/
