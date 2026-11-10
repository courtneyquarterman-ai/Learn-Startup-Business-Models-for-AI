"""Execute this trusted sample sequentially without a separate Jupyter kernel.

Do not use this runner for untrusted notebooks: it executes arbitrary Python.
Requires IPython, nbformat, and the dependencies used by the sample notebook.
"""
from datetime import datetime, timezone
import os
from pathlib import Path
import time
import json
import traceback
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
import matplotlib
matplotlib.use('Agg')

root = Path(__file__).resolve().parents[1]
out = root / 'evidence' / 'rerun'
out.mkdir(parents=True, exist_ok=True)
nb = nbformat.read(root / 'samples/quantum_bloom.ipynb', as_version=4)
for cell in nb.cells:
    if cell.cell_type == 'code':
        cell.outputs = []
        cell.execution_count = None
shell = InteractiveShell.instance()
os.chdir(out)
status = {'result': 'PASS', 'date': datetime.now(timezone.utc).isoformat(),
          'execution': 'Sequential code cells in one IPython process; Agg plotting backend; no separate Jupyter kernel',
          'source': 'samples/quantum_bloom.ipynb', 'extensions_enabled': False,
          'executed_code_cells': 0, 'limitations': 'Optional extensions remain disabled. Inline figure display is not reproduced; plot files are saved by the original code.'}
start = time.perf_counter()
for i, cell in enumerate(nb.cells):
    if cell.cell_type != 'code':
        continue
    with capture_output() as cap:
        result = shell.run_cell(cell.source, store_history=False)
    outputs = []
    if cap.stdout:
        outputs.append(nbformat.v4.new_output('stream', name='stdout', text=cap.stdout))
    if cap.stderr:
        outputs.append(nbformat.v4.new_output('stream', name='stderr', text=cap.stderr))
    for item in cap.outputs:
        outputs.append(nbformat.v4.new_output('display_data', data=item.data, metadata=item.metadata))
    status['executed_code_cells'] += 1
    cell.execution_count = status['executed_code_cells']
    error = result.error_before_exec or result.error_in_exec
    if error:
        outputs.append(nbformat.v4.new_output('error', ename=type(error).__name__, evalue=str(error),
                       traceback=traceback.format_exception(type(error), error, error.__traceback__)))
        status.update(result='FAIL', failed_cell=i, error=str(error))
    cell.outputs = outputs
    print(f'Cell {i}: {"FAIL" if error else "PASS"}', flush=True)
    if error:
        break
status['seconds'] = time.perf_counter() - start
nbformat.write(nb, out / 'quantum_bloom.executed.ipynb')
(out / 'execution-status.json').write_text(json.dumps(status, indent=2))
print(json.dumps(status, indent=2))
if status['result'] != 'PASS':
    raise SystemExit(1)
