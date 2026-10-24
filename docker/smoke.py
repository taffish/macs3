"""Independent, offline packaging probes. No production resources or scientific claims."""
import importlib
import importlib.metadata as md
from pathlib import Path
import subprocess
import sys
import tempfile
import os
import json

DATA = Path(__file__).resolve().parent

def run(*args):
    result = subprocess.run(list(map(str, args)), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode:
        print(result.stdout[-16000:], file=sys.stderr)
        raise RuntimeError(f'command failed ({result.returncode}): {args}')
    return result.stdout

def identity():
    assert run('macs3', '--version').strip() == 'macs3 3.1.0'
    for cmd in ('callpeak', 'bdgpeakcall', 'bdgbroadcall', 'bdgcmp', 'bdgopt', 'cmbreps', 'bdgdiff', 'filterdup', 'predictd', 'pileup', 'randsample', 'refinepeak', 'callvar', 'hmmratac'):
        assert cmd in run('macs3', cmd, '--help')
    assert '--jump' in run('macs3', 'hmmratac', '--help')
    assert '--threads' in run('macs3', 'callpeak', '--help')
    assert '--process-backend' in run('macs3', 'callpeak', '--help')
    assert 'source_sha256=aae548b86ab652717dca281fa2e33645fc1dc8091264ccbf7ce09cf8a13532e0' in Path('/opt/macs3/share/doc/macs3/source.txt').read_text()

def imports():
    assert md.version('MACS3') == '3.1.0'
    for name in ('numpy', 'scipy', 'pandas', 'anndata', 'sklearn', 'hmmlearn', 'h5py'):
        importlib.import_module(name)
    import MACS3
    for so in Path(MACS3.__file__).parent.rglob('*.so'):
        name = '.'.join(so.relative_to(Path(MACS3.__file__).parent.parent).parts).split('.cpython-')[0]
        importlib.import_module(name)
        assert 'not found' not in run('ldd', so), so

def peaks():
    with tempfile.TemporaryDirectory(prefix='macs3-peaks-') as directory:
        d = Path(directory)
        run(sys.executable, DATA / 'macs3_smoke.py', d)
        run('macs3', 'callpeak', '-t', d/'reads.bed', '-f', 'BED', '-g', '1000', '-n', 'smoke', '--outdir', d/'peaks', '--nomodel', '--extsize', '50', '--keep-dup', 'all', '-B', '--nolambda', '-p', '0.99', '--call-summits')
        assert 'chr1' in (d/'peaks/smoke_peaks.narrowPeak').read_text()
        assert 'chr1' in (d/'peaks/smoke_treat_pileup.bdg').read_text()
        run('macs3', 'bdgpeakcall', '-i', d/'signal.bdg', '-c', '5', '-l', '20', '-g', '10', '-o', d/'peaks.bed')
        assert 'chr1' in (d/'peaks.bed').read_text()

def anndata_export():
    import anndata
    from MACS3.Signal.PairedEndTrack import PETrackII
    from MACS3.Signal.Region import Regions
    track = PETrackII(buffer_size=100)
    track.add_loc(b'chr1', 0, 80, b'A', 2)
    track.add_loc(b'chr1', 210, 280, b'A', 1)
    track.add_loc(b'chr1', 20, 70, b'B', 3)
    track.finalize()
    regions = Regions()
    regions.add_loc(b'chr1', 0, 100)
    regions.add_loc(b'chr1', 50, 120)  # Must merge; do not duplicate a peak column.
    regions.add_loc(b'chr1', 200, 300)
    matrix = track.return_anndata(regions)
    assert matrix.shape == (2, 2)
    assert matrix.X.toarray().tolist() == [[2, 1], [3, 0]]
    with tempfile.TemporaryDirectory(prefix='macs3-anndata-') as directory:
        path = Path(directory) / 'counts.h5ad'
        matrix.write_h5ad(path)
        restored = anndata.read_h5ad(path)
        assert restored.X.toarray().tolist() == [[2, 1], [3, 0]]
        assert list(restored.obs_names) == ['A', 'B']

def hmm_model(destination):
    import numpy as np
    from MACS3.Signal.HMMR_HMM import hmm_training, hmm_model_save, hmm_model_init, hmm_predict
    rng = np.random.default_rng(7305)
    data = np.concatenate([rng.normal(mean, .1, (80, 4)) for mean in (1., 5., 15.)]).tolist()
    model = hmm_training(data, [240], covar='diag', random_seed=17)
    order = np.argsort(model.means_.sum(axis=1))
    hmm_model_save(str(destination), model, 10, int(order[2]), int(order[1]), int(order[0]), 'gaussian')
    restored = hmm_model_init(str(destination))[0]
    result = hmm_predict(data, [240], restored)
    assert result.shape == (240, 3) and np.isfinite(result).all()
    assert np.allclose(result.sum(axis=1), 1)

def fragments(destination):
    import random
    rng = random.Random(7305)
    rows = []
    for cluster in range(8):
        for length in (50, 200, 400, 600):
            for i in range(150):
                start = 1000 + cluster * 3000 + rng.randrange(900)
                end = start + length + rng.randrange(20)
                rows.append((start, end))
    Path(destination).write_text(''.join(f'chr1\t{start}\t{end}\n' for start,end in sorted(rows)))

def hmm():
    with tempfile.TemporaryDirectory(prefix='macs3-hmm-') as directory:
        d = Path(directory)
        hmm_model(d/'model.json')
        fragments(d/'fragments.bedpe')
        common = ['macs3', 'hmmratac', '-i', d/'fragments.bedpe', '-f', 'BEDPE', '--outdir', d, '--no-fragem', '--jump', '0.5']
        run(*common, '-n', 'cutoff', '--cutoff-analysis-only')
        assert (d/'cutoff_cutoff_analysis.tsv').stat().st_size > 0
        text = run(*common, '-n', 'reuse', '--model', d/'model.json', '--prescan-cutoff', '1.1')
        assert 'Load Hidden Markov Model' in text
        assert (d/'reuse_accessible_regions.narrowPeak').exists()

def plots():
    # Exercise upstream's actual exporter and base-R PDF device, without imposing
    # data-sensitive peak-model fitting or a graphics stack at image build time.
    from types import SimpleNamespace
    from MACS3.IO.OutputWriter import model2r_script
    with tempfile.TemporaryDirectory(prefix='macs3-plot-') as directory:
        d = Path(directory)
        model = SimpleNamespace(plus_line=[1,2,4,2,1], minus_line=[1,1,2,4,2], ycorr=[0,.5,1,.5,0], xcorr=[-2,-1,0,1,2], alternative_d=[1], d=1)
        model2r_script(model, str(d/'model.R'), str(d/'smoke'))
        run('Rscript', '--vanilla', d/'model.R')
        assert (d/'smoke_model.pdf').read_bytes().startswith(b'%PDF-')

def bedgraph():
    with tempfile.TemporaryDirectory(prefix='macs3-bedgraph-') as directory:
        d = Path(directory)
        (d/'a.bdg').write_text('chr1\t0\t100\t10.5\nchr1\t100\t200\t1.5\n')
        (d/'b.bdg').write_text('chr1\t0\t100\t1.5\nchr1\t100\t200\t10.5\n')
        run('macs3', 'bdgcmp', '-t', d/'a.bdg', '-c', d/'b.bdg', '-m', 'FE', '-o', d/'fe.bdg')
        assert 'chr1' in (d/'fe.bdg').read_text()
        run('macs3', 'bdgdiff', '--t1', d/'a.bdg', '--c1', d/'b.bdg', '--t2', d/'b.bdg', '--c2', d/'a.bdg', '--cutoff', '0.1', '-l', '20', '-g', '0', '--outdir', d, '--o-prefix', 'diff')
        scores = [float(line.split()[4]) for p in d.glob('diff*bed') for line in p.read_text().splitlines() if line.startswith('chr1\t')]
        assert scores and any(not x.is_integer() for x in scores), scores
        run('macs3', 'bdgopt', '-i', d/'a.bdg', '-m', 'multiply', '-p', '2', '-o', d/'scaled.bdg')
        assert '21.00000' in (d/'scaled.bdg').read_text()
        run('macs3', 'cmbreps', '-i', d/'a.bdg', d/'b.bdg', '-m', 'mean', '-o', d/'mean.bdg')
        assert 'chr1' in (d/'mean.bdg').read_text()

def parallel():
    # Runtime-only coverage of the new execution policy; no performance claim.
    with tempfile.TemporaryDirectory(prefix='macs3-parallel-') as directory:
        d = Path(directory)
        rows = [f'{chrom}\t{100+i%30}\t{180+i%30}\tcellA\t2'
                for chrom in ('chr1', 'chr2') for i in range(100)]
        (d/'fragments.tsv').write_text('\n'.join(rows))  # No terminal newline.
        outputs = []
        for backend in ('serial', 'auto'):
            run('macs3', 'callpeak', '-t', d/'fragments.tsv', '-f', 'FRAG',
                '-g', '2000', '-n', 'test', '--outdir', d/backend, '--nomodel',
                '--keep-dup', 'all', '--nolambda', '-p', '0.99', '--threads', '2',
                '--process-backend', backend)
            output = (d/backend/'test_peaks.narrowPeak').read_text()
            assert 'chr1' in output and 'chr2' in output
            outputs.append(output)
        assert outputs[0] == outputs[1], 'serial/auto disagree on tiny fixed input'

if __name__ == '__main__':
    modes = dict(identity=identity, imports=imports, peaks=peaks, anndata=anndata_export, hmm=hmm, plots=plots, bedgraph=bedgraph, parallel=parallel)
    if sys.argv[1] == 'prepare-hmm':
        destination = Path(sys.argv[2]); destination.mkdir(parents=True, exist_ok=True)
        hmm_model(destination/'model.json'); fragments(destination/'fragments.bedpe')
    else:
        modes[sys.argv[1]]()
    print('PASS', sys.argv[1])
