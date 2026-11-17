"""Optional full notebook rerun. Requires nbclient, nbformat, ipykernel and sample dependencies."""
import json
from pathlib import Path
import sys
import time
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

root = Path(__file__).resolve().parents[1]
out = root / 'evidence' / 'rerun'
out.mkdir(parents=True, exist_ok=True)
source = root / 'samples' / 'quantum_bloom.ipynb'
notebook = nbformat.read(source, as_version=4)
for cell in notebook.cells:
    if cell.cell_type == 'code':
        cell.outputs = []
        cell.execution_count = None
start = time.perf_counter()
status = {'source': 'samples/quantum_bloom.ipynb', 'execution': 'fresh sequential notebook execution',
          'extensions_enabled': False}
try:
    NotebookClient(notebook, timeout=300, kernel_name='python3',
                   km=KernelManager(kernel_name='python3', transport='ipc', ip=str(out / 'kernel')),
                   resources={'metadata': {'path': str(out)}}).execute()
    status['result'] = 'PASS'
except Exception as exc:
    status.update(result='FAIL', error_type=type(exc).__name__, error=str(exc))
finally:
    status['seconds'] = time.perf_counter() - start
    status['executed_code_cells'] = sum(c.cell_type == 'code' and c.execution_count is not None for c in notebook.cells)
    nbformat.write(notebook, out / 'quantum_bloom.executed.ipynb')
    (out / 'execution-status.json').write_text(json.dumps(status, indent=2))
    print(json.dumps(status, indent=2))
if status['result'] != 'PASS':
    sys.exit(1)
