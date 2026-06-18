macs3 3.0.4-r1

Purpose:
  MACS3 packaged for TAFFISH. MACS3 calls ChIP-seq, ATAC-seq and other
  DNA enrichment peaks, and provides bedGraph and HMMRATAC subcommands.

Usage:
  taf-macs3 -- --help
  taf-macs3 macs3 --help
  taf-macs3 macs3 callpeak -t chip.bam -c control.bam -f BAM -g hs -n chip
  taf-macs3 macs3 bdgpeakcall -i signal.bdg -c 5 -l 200 -g 100 -o peaks.bed
  taf-macs3 macs3 hmmratac -i atac.bam -f BAMPE -n atac_hmm

Common workflows:
  Narrow ChIP-seq:
    taf-macs3 macs3 callpeak -t chip.bam -c control.bam -f BAM -g hs -n chip -B -q 0.01

  Broad histone peaks:
    taf-macs3 macs3 callpeak -t histone.bam -c input.bam --broad -g hs --broad-cutoff 0.1

  Paired-end ATAC-seq:
    taf-macs3 macs3 callpeak -f BAMPE -t atac.bam -g hs -n atac -B -q 0.01

  bedGraph peak calling:
    taf-macs3 macs3 bdgpeakcall -i signal.bdg -c 5 -l 200 -g 100 -o peaks.bed

Included subcommands:
  callpeak       main narrow/broad peak caller
  bdgpeakcall    call peaks from bedGraph
  bdgbroadcall   call broad peaks from bedGraph
  bdgcmp         compare treatment/control bedGraph tracks
  bdgopt         operate on bedGraph score columns
  cmbreps        combine replicate bedGraph tracks
  bdgdiff        differential peak detection from bedGraph tracks
  filterdup      remove duplicate reads
  predictd       estimate fragment size
  pileup         pile up reads/fragments
  randsample     randomly sample reads
  refinepeak     refine peak summits
  callvar        call variants in peak regions
  hmmratac       HMM-based ATAC-seq/scATAC-seq peak calling

Packaged runtime:
  macs3      3.0.4
  python     3.10
  numpy      1.26.4
  scipy      1.13.1
  sklearn    1.5.2
  hmmlearn   0.3.3
  cykhash    2.0.1

Notes:
  This app calls macs3 by default.
  Use taf-macs3 macs3 SUBCOMMAND ... for upstream MACS3 subcommands.
  The taf-macs3 -- form is mainly for option-leading arguments such as --help.
  No reference genome, blacklist, alignment tool, sample sheet, or workflow
  logic is bundled.
  MACS3 normally runs offline once input alignment, fragment or bedGraph files
  are available.
  Upstream warns that hmmratac results on non-x86 Linux architectures may differ
  because of scientific calculation library behavior.

Detailed documentation:
  https://macs3-project.github.io/MACS/
  https://github.com/macs3-project/MACS

Wrapper options:
  taf-macs3 --help       Show this TAFFISH help.
  taf-macs3 --version    Show TAFFISH wrapper version.
  taf-macs3 --compile    Compile the TAFFISH wrapper.
  taf-macs3 -- --help    Pass option-leading arguments to macs3.
