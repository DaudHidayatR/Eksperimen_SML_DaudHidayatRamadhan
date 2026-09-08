# Eksperimen SML — DaudHidayatRamadhan

A passive four-class text classifier for Normal, SQLInjection, XSS and CommandInjection benchmark payloads. Payloads are read as text, never executed.

The publisher-declared Apache-2.0 raw dataset and attribution are under sqli_xss_raw/. The original CSV is losslessly gzip-compressed. The notebook retains all five sections of the supplied Dicoding template.

The preprocessing policy removes null/empty payloads, invalid one-hot labels, all contradictory-label payload groups, and exact duplicates. It then takes a deterministic stratified 24,000-row resource-bounded subset and splits 80/20. This sample size was fixed before evaluating model performance. All exclusions and hashes are reported. Text stays as text; the learned TF-IDF vocabulary is fitted within each training/CV fold in the model stage. No lowercasing, punctuation stripping, or payload execution is performed.

Remaining limitations include near-duplicate leakage and the publisher's label-quality warning; the dataset is not representative evidence of production security effectiveness.

## Environment

Use Python 3.12.7 and install requirements-notebook.txt for the notebook, or requirements.txt for automation. Execute preprocessing/Eksperimen_DaudHidayatRamadhan.ipynb from a clean kernel. Automation and workflow usage will be documented after verification.


## Docker-first execution

Build with `docker compose build`. Run the manual notebook with `docker compose run --rm notebook`.
The Compose defaults run as UID/GID 1000. On standard Docker, set LOCAL_UID and LOCAL_GID to your host user IDs if different. On this workstation's rootless Podman compatibility runtime, use `LOCAL_UID=0 LOCAL_GID=0 docker compose run --rm notebook`; container root maps to the unprivileged host user.

The Dockerfile prefers IPv4 for package downloads because this workstation has unreachable IPv6 paths. The change is inside the container only. Runtime data and notebook outputs are persisted via the project bind mount. Container images are not the raw-data evidence; the original gzip remains in Git.

Run automation with `docker compose run --rm preprocess`. Run verification with `docker compose run --rm notebook python -m unittest discover -s tests` (apply the rootless user override described above when needed).

GitHub Actions builds the same Dockerfile, regenerates the processed data, checks parity against the saved manual manifest, and uploads train/test/manifest files as a run artifact. It commits only changed outputs. Output-only commits are excluded from trigger paths, so they cannot recurse. A changed raw snapshot must be reviewed and its expected checksum/manual parity fixture updated together; automation fails closed on unreviewed source changes.

The artifact is retained for 30 days; the same verified data is also stored in the repository. Re-run the workflow near submission if fresh downloadable run evidence is needed.
