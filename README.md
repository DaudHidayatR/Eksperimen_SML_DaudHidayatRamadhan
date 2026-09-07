# Eksperimen SML — DaudHidayatRamadhan

A passive four-class text classifier for Normal, SQLInjection, XSS and CommandInjection benchmark payloads. Payloads are read as text, never executed.

The publisher-declared Apache-2.0 raw dataset and attribution are under sqli_xss_raw/. The original CSV is losslessly gzip-compressed. The notebook retains all five sections of the supplied Dicoding template.

The preprocessing policy removes null/empty payloads, invalid one-hot labels, all contradictory-label payload groups, and exact duplicates. It then takes a deterministic stratified 24,000-row resource-bounded subset and splits 80/20. This sample size was fixed before evaluating model performance. All exclusions and hashes are reported. Text stays as text; the learned TF-IDF vocabulary is fitted within each training/CV fold in the model stage. No lowercasing, punctuation stripping, or payload execution is performed.

Remaining limitations include near-duplicate leakage and the publisher's label-quality warning; the dataset is not representative evidence of production security effectiveness.

## Environment

Use Python 3.12.7 and install requirements-notebook.txt for the notebook, or requirements.txt for automation. Execute preprocessing/Eksperimen_DaudHidayatRamadhan.ipynb from a clean kernel. Automation and workflow usage will be documented after verification.
