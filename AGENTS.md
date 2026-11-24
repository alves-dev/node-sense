# AGENTS.md

## Setup Commands

- Install: `python3 -m venv .venv && . .venv/bin/activate && pip install -e '.[test]'`
- Local MQTT: `docker run -d --name nodesense-mqtt -p 1883:1883 -v "$PWD/mosquitto.local.conf:/mosquitto/config/mosquitto.conf:ro" eclipse-mosquitto:2`
- Run: `python main.py` or `docker compose up -d`
- Test: `pytest`
- Docker build: `docker compose build` or `docker build --build-arg TARGETARCH=amd64 -t nodesense:local .`

## Code Style

- Python 3.12+, small modules and standard-library interfaces where practical.
- Keep MQTT topics, entity IDs and agent IDs stable.
- Do not invoke external commands through a shell or interpolate untrusted values.
- Preserve atomic persistence, graceful shutdown and local execution locking.
- Follow patterns from `context/knowledge/patterns/`.

## Context Files to Load

- `context/.context-mesh-framework.md`
- `context/intent/project-intent.md`
- Relevant files under `context/intent/`, `context/decisions/` and `context/knowledge/patterns/`

## After Changes

- Update the relevant Context Mesh feature, decision outcome or changelog entry.
- Run the relevant tests and document validation results.
- Do not commit `.idea/`, local `.env` files or generated caches.

## Definition of Done

- [ ] Relevant decision and pattern context was reviewed.
- [ ] Implementation follows documented conventions.
- [ ] Tests pass or the limitation is documented.
- [ ] Context Mesh reflects the change.
- [ ] Changelog is updated for material behavior changes.
