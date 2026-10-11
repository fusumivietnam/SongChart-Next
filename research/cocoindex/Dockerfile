FROM python:3.12-slim-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/huggingface

WORKDIR /workspace
COPY research/cocoindex/requirements.txt /tmp/cocoindex-requirements.txt
RUN python -m pip install --requirement /tmp/cocoindex-requirements.txt
RUN python - <<'PY'
from sentence_transformers import SentenceTransformer
SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
PY

COPY . /workspace
CMD ["python", "research/cocoindex/benchmark.py"]
