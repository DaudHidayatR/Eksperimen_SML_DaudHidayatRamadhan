FROM python:3.12.7-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/matplotlib HOME=/tmp
# Prefer working IPv4 routes on hosts with unreachable IPv6; container-only setting.
RUN printf 'precedence ::ffff:0:0/96 100\n' >> /etc/gai.conf
WORKDIR /workspace
COPY requirements.txt requirements-notebook.txt ./
RUN pip install --no-cache-dir -r requirements-notebook.txt && pip check
RUN useradd --uid 1000 --create-home learner
COPY --chown=1000:1000 . .
USER 1000:1000
CMD ["python", "tools/execute_notebook.py"]
