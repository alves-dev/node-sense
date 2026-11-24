# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS runtime
ARG TARGETARCH
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl gnupg \
    && install -d -m 0755 /etc/apt/keyrings \
    && curl -fsSL https://packagecloud.io/ookla/speedtest-cli/gpgkey | gpg --dearmor -o /etc/apt/keyrings/ookla.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/ookla.gpg] https://packagecloud.io/ookla/speedtest-cli/debian bookworm main" > /etc/apt/sources.list.d/ookla.list \
    && if [ "$TARGETARCH" = "arm" ]; then echo 'arm/v7 is not a validated NodeSense target' >&2; exit 1; fi \
    && apt-get update && apt-get install -y --no-install-recommends speedtest \
    && speedtest --version && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY nodesense ./nodesense
COPY main.py ./
COPY static ./static
RUN useradd --system --uid 10001 nodesense && mkdir /data && chown nodesense:nodesense /data
USER nodesense
VOLUME ["/data"]
ENTRYPOINT ["python", "main.py"]
