# NodeSense

![NodeSense](<NodeSense Neon Tech Banner.webp>)

Agente leve de telemetria para hosts Linux, integrado ao Home Assistant por MQTT Discovery. A V1 publica hostname e temperatura disponível, executa a CLI oficial Ookla e expõe download, upload, ping, jitter, perda, servidor, status, cron, switch e botão manual como um único dispositivo no HA.

## Execução local

```bash
cp .env.example .env
docker run -d --name nodesense-mqtt -p 1883:1883 -v "$PWD/mosquitto.local.conf:/mosquitto/config/mosquitto.conf:ro" eclipse-mosquitto:2
docker compose pull
docker compose up -d
```

O Compose usa a imagem publicada em `ghcr.io/alves-dev/nodesense:latest`, `network_mode: host`, monta `/sys` somente leitura e mantém a configuração em um volume Docker. Para um registry privado, execute `docker login ghcr.io` antes do `pull`. Para construir a versão localmente, use `docker compose build` e depois `docker compose up -d`. Para outro host, altere `AGENT_ID`, `AGENT_NAME` e `MQTT_HOST`; o `AGENT_ID` deve ser único e estável.

O workflow lê a versão de `pyproject.toml` e publica automaticamente as imagens `linux/amd64` e `linux/arm64` no GHCR com as tags `latest`, `<versão-do-projeto>` e `sha-<commit>`. O pacote é publicado como `ghcr.io/alves-dev/nodesense`; a visibilidade pública do pacote pode ser ajustada nas configurações de Packages do GitHub.

## MQTT e HA

O discovery é retido em `homeassistant/device/nodesense_<agent_id>/config`. Estados ficam em `nodesense/<agent_id>/system/state` e `speedtest/state`; comandos ficam em `speedtest/cron/set`, `speedtest/enabled/set` e `speedtest/run/set`. Comandos não são retidos. O agente publica Last Will `offline` e `online` após reconexão.

O cron tem cinco campos e, por padrão, é `0 */4 * * *`. A frequência mínima padrão é 30 minutos. A configuração editável é salva atomicamente em `/data/config.json`. Uma execução por host é permitida; um disparo concorrente é ignorado.

As entidades de conectividade usam o prefixo `Internet —` e ícones específicos de rede. A temperatura usa `CPU/SoC — Temperature` e prioriza `coretemp/Package id 0`, `x86_pkg_temp` e zonas explicitamente identificadas como CPU/SoC; zonas ACPI/ambiente e Wi-Fi ficam como fallback inferior.

## Ookla e arquiteturas

A imagem instala a CLI oficial `speedtest` no próprio container, não no host. O Dockerfile valida `speedtest --version` no build e aceita `amd64` e `arm64` conforme os pacotes oficiais disponíveis. `arm/v7` não é rotulado como suportado nesta versão: o pacote encontrado é antigo e não foi validado com a base/flags atuais. O uso da CLI deve obedecer à licença e aos termos da Ookla.

## Desenvolvimento

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[test]'
pytest
```

Testes unitários cobrem parsing/conversão, cron, persistência e seleção de sensor. A validação de HA pode ser feita em `http://localhost:9123` após o container MQTT e o agente estarem ativos.
