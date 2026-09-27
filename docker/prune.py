"""Remove compiler-only payload before copying the runtime prefix into the final image."""
import importlib.metadata as md
import json
from pathlib import Path
import shutil

root = Path('/opt/macs3/venv')
removed = []
for p in list(root.rglob('__pycache__')) + [root / 'include']:
    if p.is_dir():
        removed.append(str(p.relative_to(root)))
        shutil.rmtree(p)
# Headers/static archives are development-only; keep Python modules, runtime data,
# package metadata, upstream examples and license files (including wheel notices).
for p in list(root.rglob('*.a')) + list(root.rglob('*.h')) + list(root.rglob('*.pxd')):
    if p.is_file():
        removed.append(str(p.relative_to(root)))
        p.unlink()
# NumPy's testing API imports numpy._core.tests._natype at runtime, so retain
# its entire test tree. Other removed suites are not MACS3 runtime interfaces.
# Keep sklearn datasets, examples, notices and MACS3's own validation fixture.
site = root/'lib/python3.12/site-packages'
for package in ('pandas', 'scipy', 'sklearn'):
    for p in sorted((site/package).rglob('tests'), key=lambda x: len(x.parts)):
        if p.is_dir():
            removed.append(str(p.relative_to(root)))
            shutil.rmtree(p)
doc = Path('/opt/macs3/share/doc/macs3')
(doc / 'python-packages.txt').write_text('\n'.join(sorted(f'{d.metadata["Name"]}=={d.version}' for d in md.distributions()))+'\n')
(doc / 'pruned-development-files.json').write_text(json.dumps(removed, indent=2)+'\n')
