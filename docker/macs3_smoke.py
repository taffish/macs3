#!/usr/bin/env python3
from pathlib import Path
import sys


def write_lines(path, lines):
    path.write_text("".join(lines))


outdir = Path(sys.argv[1])
outdir.mkdir(parents=True, exist_ok=True)

reads = []
for i in range(80):
    start = 100 + (i % 20)
    reads.append(f"chr1\t{start}\t{start + 36}\tpeak_plus_{i}\t255\t+\n")
    reads.append(f"chr1\t{start + 8}\t{start + 44}\tpeak_minus_{i}\t255\t-\n")
for i in range(8):
    start = 650 + i * 20
    reads.append(f"chr1\t{start}\t{start + 36}\tbackground_{i}\t255\t+\n")

write_lines(outdir / "reads.bed", reads)

write_lines(
    outdir / "signal.bdg",
    [
        "chr1\t0\t80\t0\n",
        "chr1\t80\t180\t12\n",
        "chr1\t180\t260\t11\n",
        "chr1\t260\t360\t0\n",
        "chr1\t360\t430\t7\n",
        "chr1\t430\t520\t0\n",
    ],
)
