# Notebook execution record

Date: November 10, 2026. Performed by the AI coding agent during development.

## Outcome
All 10 code cells in the supplied sample executed sequentially with the original assertions enabled. No source changes were needed. Optional experiments stayed disabled, as in the original notebook. The generated classification metrics match the original saved values to their displayed precision; execution timings differ by environment.

| Model | Accuracy | Balanced accuracy | Malignant recall | ROC-AUC |
|---|---|---|---|---|
| RBF, 30 features | 0.9649 | 0.9573 | 0.9286 | 0.9940 |
| RBF, PCA 4 | 0.9298 | 0.9097 | 0.8333 | 0.9940 |
| Quantum ZZ, PCA 4 | 0.6404 | 0.5665 | 0.2857 | 0.7060 |

## Method
Jupyter kernel launch initially failed because this execution environment disallows the required sockets. The first failed attempt is recorded in `evidence/rerun/initial-tcp-attempt.json`. Switching to IPC was also blocked. The successful fallback was `scripts/rerun_inprocess.py`, which executes the sample's code cells in order in one IPython process, clears old outputs first, captures text/rich outputs, and saves an executed notebook. This method uses the Agg plotting backend. Inline plot display is not reproduced, but plots explicitly saved by the notebook were generated. This is sequential code execution, not verification of the normal Jupyter interactive experience.

## Environment
Python 3.12.14; NumPy 2.5.4; scikit-learn 1.9.1; Qiskit 2.6.2; qiskit-machine-learning 0.9.1. The notebook also uses pandas, matplotlib, and IPython. Full package listing is in `evidence/rerun/environment-packages.txt`.

## Evidence
- `evidence/rerun/execution-status.json`: outcome, method, timing, executed cell count.
- `evidence/rerun/quantum_bloom.executed.ipynb`: fresh captured outputs.
- `evidence/rerun/breast_cancer_qml_results/`: generated metrics CSV, plots, configuration, sample IDs, and kernel matrices.
- `evidence/rerun/inspection.json`: verifier inspection of the executed copy.

## Reproduce separately (optional)
For ordinary use of the verifier, no extra packages are required. To repeat the experiment, use a separate virtual environment and install the packages listed below. Review the notebook before executing its code. Run the in-process helper from the project folder:

```sh
python -m pip install 'qiskit>=2,<3' 'qiskit-machine-learning>=0.9,<0.10' numpy pandas matplotlib scikit-learn IPython nbformat
python scripts/rerun_inprocess.py
```

The helper executes the supplied sample only and is not a sandbox for untrusted code. `scripts/rerun_notebook.py` is also included for conventional kernel execution in environments where Jupyter sockets are supported; that execution mode was blocked here.

## Limits
Passing the notebook assertions does not independently establish statistical validity, medical usefulness, learner understanding, or quantum advantage. No quantum hardware was used. This run is separate from the pending external user test.
