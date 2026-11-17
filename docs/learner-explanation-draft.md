# Learner explanation — draft for student review

This explanation was drafted with AI assistance from the supplied notebook. Review it against the code and rewrite any wording you would not use or cannot explain. It is not evidence that a learner demonstrated understanding in a live assessment.

## What the experiment does
The notebook compares three support vector machine classifiers on the Wisconsin Diagnostic Breast Cancer dataset: an RBF SVM using all 30 features, an RBF SVM using four principal components, and a quantum-kernel SVM using those same four components. The purpose is to study how feature reduction and kernel choice affect performance. The dataset is used as an educational example, not as a basis for a clinical tool.

## How the data is prepared
The notebook reserves 20% of observations for testing using a stratified split and seed 42. It selects 120 training observations from the remaining training pool. All three models use the same training and test observation IDs. Standardization is fitted only on the selected training data. PCA is also fitted on that training data and retains four components. Those components are scaled to angles between zero and pi; test values outside the fitted range are clipped. Keeping the test data out of fitting helps avoid data leakage.

## Where the quantum part enters
A four-qubit ZZ feature map encodes the four PCA coordinates, with two repetitions and linear entanglement. The kernel measures the squared overlap between the states for two observations. The main classifier uses exact statevector simulation through FidelityStatevectorKernel. The SVM itself is trained classically using a precomputed kernel matrix. A separate 2,048-shot example compares a sampled overlap estimate with the exact value. That sampling example does not model device noise.

## Why the classical comparisons matter
The full-feature RBF model provides a reference for the effect of feature reduction. Comparing the two four-component models holds the reduced inputs fixed while changing the kernel. The notebook fixes C at 1 for the initial comparison; this is not a comparison of fully optimized models.

## How I would interpret the supplied saved outputs
The saved table reports accuracy of about 96.5% for the full-feature RBF SVM, 93.0% for the PCA RBF SVM, and 64.0% for the quantum-kernel SVM. The corresponding malignant recall values are about 92.9%, 83.3%, and 28.6%. On this particular split and configuration, the quantum model performs worse. That result does not show that all quantum kernels fail; it shows that this configuration did not improve on these baselines. A developer rerun reproduced these displayed metrics. Its method and limits are recorded in docs/notebook-rerun.md; that rerun does not establish that I personally performed or understood the experiment.

## What still needs checking
One small training subset and one split do not establish general performance. Fixed initial settings are not a fair basis for claiming that one model family can never work better. Looking at the held-out scores and then tuning to them would weaken their value as an independent evaluation. Simulation timings do not establish quantum hardware speedup. The MVP report cannot establish authorship or understanding: a reviewer still needs to ask the learner to explain decisions and respond to follow-up questions.

## How this relates to Hybrid Skills Verifier
The notebook is a sample submission, while the verifier organizes its saved evidence and records a human judgment. The verifier can report saved errors and comparisons, but it does not execute the notebook or certify the learner. The first user test should check whether this evidence record is useful to a reviewer.
