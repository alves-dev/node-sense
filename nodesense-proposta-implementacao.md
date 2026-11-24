# NodeSense — Proposta técnica e especificação de implementação

## 1. Visão geral

**NodeSense** é um agente leve de telemetria para homelab, escrito em Python, executado como **um container Docker por host** e integrado ao **Home Assistant (HA)** via **MQTT Discovery**. Pretende gradualmente concentrar as funcionalidades utilizadas hoje em Glances, Beszel e Net Pulse, sem exigir banco de dados ou backend central. O HA será a interface de visualização, histórico e controle.

**Repositório sugerido:** `alves-dev/nodesense`  
**Imagem sugerida:** `ghcr.io/alves-dev/nodesense`  
**Status:** proposta para implementação; nada nesta especificação deve ser considerado já implementado ou testado.

## 2. Objetivos da V1

1. Executar em hosts Linux `amd64`, Raspberry Pi `arm64` e, **se houver binário oficial compatível**, `arm/v7`.
2. Registrar **um dispositivo MQTT por agente/host** no Home Assistant, com identificadores estáveis.
3. Publicar nome do host, disponibilidade e temperatura de CPU/SoC quando o host fornecer esse sensor.
4. Executar testes de velocidade da Internet com a **CLI oficial da Ookla incluída na imagem Docker**; publicar download, upload, latência, jitter, perda de pacotes quando presente, servidor usado, status e timestamps.
5. Configurar **por entidade do HA, independentemente para cada host**, expressão cron e habilitação dos testes; permitir execução manual por botão.
6. Persistir configuração localmente, sobreviver a reinicializações e indisponibilidade temporária de HA/MQTT.
7. Preparar arquitetura extensível para novos coletores (CPU, RAM, disco, rede, Docker, uptime etc.) sem incluí-los obrigatoriamente na V1.

## 3. Não objetivos da V1

- Não criar frontend próprio, API REST, banco de dados, painel web ou servidor de coordenação.
- Não implementar monitoramento detalhado de containers, disco, RAM e CPU nesta etapa.
- Não exigir instalação da Ookla no host.
- Não prometer ausência de testes simultâneos **entre hosts**: crons desencontrados diminuem a chance, mas não constituem trava distribuída. Implementar trava **local** por agente; coordenação distribuída é evolução futura.

## 4. Arquitetura

```text
server1 [NodeSense container] ─┐
server2 [NodeSense container] ─┼── MQTT Broker (Mosquitto) ⇄ Home Assistant
server3 [NodeSense container] ─┤        ↑                 MQTT Discovery
raspberry [NodeSense] ────────┘        └── comandos/configuração HA → agente
```

Componentes sugeridos:

- `core/config.py`: configuração por variáveis de ambiente, validação e persistência atômica de parâmetros editáveis.
- `core/mqtt.py`: conexão TLS/autenticação, reconexão, publish/subscribe, Last Will, tópicos e disponibilidade.
- `core/discovery.py`: publicação de entidades MQTT Discovery por dispositivo.
- `core/scheduler.py`: agendamento cron, timezone, atualização dinâmica, prevenção de concorrência local.
- `collectors/temperature.py`: leitura de sensores térmicos do host.
- `collectors/speedtest.py`: execução segura da CLI Ookla e parsing JSON.
- `main.py`: ciclo de vida, inicialização, encerramento e supervisão de tarefas.

Preferir Python 3.12+ e dependências pequenas (`paho-mqtt`, `croniter` ou APScheduler, `psutil` somente se necessário, `pydantic` opcional). Não executar comandos via shell interpolado.

## 5. Modelo MQTT

Prefixo configurável, padrão `nodesense`. `agent_id` deve ser estável, explícito ou derivado de hostname persistido; **não** depender do ID efêmero do container. Usar nomes normalizados e não permitir colisões entre hosts.

Tópicos exemplificativos:

```text
nodesense/server1/availability                 online | offline
nodesense/server1/system/state                 JSON de sensores/identidade
nodesense/server1/speedtest/state              JSON do último teste
nodesense/server1/speedtest/status             idle | running | success | error
nodesense/server1/speedtest/cron/state         expressão cron atual
nodesense/server1/speedtest/cron/set           nova expressão
nodesense/server1/speedtest/enabled/state      ON | OFF
nodesense/server1/speedtest/enabled/set        ON | OFF
nodesense/server1/speedtest/run/set            comando de execução manual
nodesense/server1/speedtest/next_run           timestamp ISO 8601
```

Usar MQTT Discovery no formato **device-based**, conforme a documentação atual do Home Assistant, por exemplo `homeassistant/device/nodesense_server1/config`. Verificar o schema oficial antes de implementar. Todas as entidades pertencem ao mesmo dispositivo com `identifiers`, `name`, `manufacturer: NodeSense`, `model`, `sw_version`. Cada entidade tem `unique_id` estável. Publicar Discovery e estado relevante com `retain` quando apropriado. `availability` usa MQTT Last Will `offline` e publicação `online` após conectar. Comandos `*/set` **não** devem ser retained, para evitar reexecução após reconexão.

Entidades esperadas:

| Entidade | Tipo HA | Observação |
|---|---|---|
| Nome do host | sensor | Diagnóstico, estável |
| Temperatura | sensor | `°C`, `device_class: temperature`, `state_class: measurement`; indisponível se sem sensor |
| Download | sensor | `Mbit/s`, `state_class: measurement` |
| Upload | sensor | `Mbit/s`, `state_class: measurement` |
| Ping | sensor | `ms`, medição de latência |
| Jitter | sensor | `ms` |
| Perda de pacotes | sensor | `%`, opcional conforme JSON da CLI |
| Servidor do teste | sensor | Nome/ID da ponta Ookla |
| Último teste | sensor | ISO 8601, `device_class: timestamp` |
| Próximo teste | sensor | ISO 8601, `device_class: timestamp` |
| Status do teste | sensor | idle/running/success/error; opcional `last_error` diagnóstico |
| Cron | text | Editável no HA; validar e confirmar por tópico state |
| Testes habilitados | switch | ON/OFF persistido |
| Executar teste | button | Disparo manual, sem reter comando |

**Observação:** preferir JSON de estado agregado para reduzir publicações, mas manter tópicos de configuração/comandos separados. Definir claramente `value_template`, `availability_topic`, `entity_category` e disponibilidade dos campos. Não publicar zeros artificiais quando o sensor estiver ausente ou o teste falhar. Não reter indefinidamente `running` como status após restart; restaurar `idle` ou `error` de forma consistente.

## 6. Cron e comportamento dos testes

- Expressão cron padrão de **5 campos** (`min hora dia mês dia_semana`) e timezone configurável (`TZ`, por padrão `America/Sao_Paulo` ou definido explicitamente no deployment).
- Valor inicial sugerido por host, evitando horários idênticos:
  - `server1`: `0 */4 * * *`
  - `server2`: `10 */4 * * *`
  - `server3`: `20 */4 * * *`
  - `raspberry`: `30 */4 * * *`
- O usuário altera o cron por entidade `text` do HA. Validar a expressão e impor frequência mínima configurável para evitar testes excessivos (sugestão: 30 minutos). Em caso de erro, manter configuração anterior, publicar erro e republicar valor válido.
- Persistir cron e enabled em JSON no volume `/data`, com escrita atômica; ao reiniciar, restaurar configuração antes de agendar.
- O botão manual pode executar com testes agendados desabilitados, mas respeita trava local e timeout. Documentar essa decisão.
- Uma execução por agente por vez; quando ocupado, rejeitar comando adicional e registrar motivo (não enfileirar indefinidamente).
- Não executar teste automaticamente na inicialização, salvo configuração explícita futura.
- Não tentar recuperar em lote testes perdidos durante downtime.
- Calcular e publicar `next_run` após mudanças, execução e reinicialização.
- A CLI pode consumir banda e afetar outros serviços: limites de frequência e timeout são obrigatórios.

## 7. Ookla CLI e imagem multiarch

**Requisito essencial:** a CLI oficial `speedtest` deve estar **dentro da imagem**, sem bind mount de binário do host.

- Criar Dockerfile multi-stage baseado em imagem Python slim adequada à arquitetura.
- Selecionar artefato por `TARGETARCH`/`TARGETVARIANT` (BuildKit) e validar arquitetura real no build.
- **Antes de fechar a matriz**, confirmar no site/repositório oficial Ookla a disponibilidade, versão, URL, licença e dependências dos pacotes `amd64`, `arm64` e `arm/v7`. Se `arm/v7` não estiver disponível/compatível, não inventar URL nem rotular a imagem como suportada; documentar limitação e permitir fallback futuro.
- Fixar versão e, quando possível, checksum SHA-256 verificável; evitar baixar `latest` não rastreável.
- Validar `speedtest --version` no build (considerar limitações de execução cross-arch no CI).
- Executar com argumentos `--accept-license --accept-gdpr --format=json`, após confirmar flags na versão fixada. Tratar aceitação de termos e obrigações de redistribuição/licenciamento antes de publicar imagem pública.
- Converter corretamente `bandwidth` (bytes/s) em Mbit/s: `bytes_per_second * 8 / 1_000_000`; não confundir com MiB/s.
- Tratar timeout, JSON inválido, código de saída, indisponibilidade de rede e campos ausentes.
- Preferir usuário não-root e permissões mínimas; considerar `network_mode: host` para medições representativas da conectividade do host, sem afirmar equivalência absoluta.

## 8. Temperatura no container

- Preferir leitura de `/sys/class/thermal/thermal_zone*/temp` e/ou sensores de `hwmon`, com identificação explícita do sensor relevante.
- Montar `/sys` do host **somente leitura** se necessário; não usar `privileged: true` por padrão.
- Em Raspberry Pi, identificar zona térmica do SoC; em servidores x86, validar disponibilidade e nomenclatura real (nem toda zona representa CPU).
- Normalizar miligraus para Celsius e tratar leituras ausentes, sem publicar 0 °C como substituto.
- Configurar intervalo de coleta (ex.: 30 s) e opcionalmente caminho do sensor.

## 9. Docker Compose e configuração

Fornecer `compose.yaml` e `.env.example` sem segredos reais:

```yaml
services:
  nodesense:
    image: ghcr.io/alves-dev/nodesense:VERSION
    container_name: nodesense
    restart: unless-stopped
    network_mode: host
    environment:
      AGENT_ID: ${AGENT_ID}
      AGENT_NAME: ${AGENT_NAME}
      MQTT_HOST: ${MQTT_HOST}
      MQTT_PORT: ${MQTT_PORT:-1883}
      MQTT_USERNAME: ${MQTT_USERNAME}
      MQTT_PASSWORD: ${MQTT_PASSWORD}
      MQTT_BASE_TOPIC: nodesense
      TZ: America/Sao_Paulo
      DATA_DIR: /data
    volumes:
      - nodesense-data:/data
      - /sys:/host/sys:ro
volumes:
  nodesense-data:
```

A aplicação deve usar `/host/sys` como base quando configurado. `network_mode: host` é escolha inicial para Linux, mas testar acesso MQTT, isolamento e segurança. Oferecer opção TLS para broker remoto e documentar credenciais via secret/file quando aplicável.

## 10. Qualidade e observabilidade

- Logs estruturados legíveis em `docker logs`; nunca registrar senha MQTT ou tokens.
- Graceful shutdown, reconexão MQTT com backoff, publicações QoS apropriadas, Last Will e idempotência do Discovery.
- Testes unitários para parsing da Ookla, conversão de unidades, validação cron, persistência e seleção de sensores térmicos.
- Testes de integração com Mosquitto e, quando viável, HA de teste; não exigir HA real para unit tests.
- CI: lint (`ruff`), testes (`pytest`), build Docker; publicação multiarch somente para arquiteturas validadas.
- README com instalação, configuração por host, permissões, segurança, troubleshooting, tópicos MQTT e exemplos de entidades no HA.

## 11. Critérios de aceite

1. Subir com `docker compose up -d` em Linux `amd64`, sem Ookla instalada no host.
2. Um dispositivo NodeSense aparece no HA com entidades corretas e IDs estáveis após restart.
3. Temperatura aparece quando disponível e fica indisponível quando não suportada.
4. Teste manual gera métricas reais com unidades corretas e timestamp; falhas não sobrescrevem métricas com zero.
5. Editar cron e switch no HA altera execução e persiste após reiniciar container.
6. Agendamento funciona sem HA online, desde que o processo esteja ativo; reconexão MQTT restaura estados/Discovery.
7. Dois comandos simultâneos não produzem dois processos Ookla no mesmo host.
8. Comandos antigos não são reexecutados ao reconectar.
9. Testes documentados e pipeline de build multiarch; `arm64` validado em Raspberry Pi e `arm/v7` somente se oficialmente suportado.
10. Nenhum `privileged: true` obrigatório; segredos não aparecem nos logs nem no repositório.

## 12. Sequência de implementação sugerida

1. Criar esqueleto, configuração e Compose; validar conectividade MQTT.
2. Implementar MQTT Discovery e disponibilidade.
3. Implementar temperatura e identificação de host.
4. Incorporar Ookla na imagem e criar parser JSON testável.
5. Implementar sensores de resultado e botão manual.
6. Implementar cron, switch, persistência, validação e exclusão mútua local.
7. Adicionar testes, documentação e CI multiarch.
8. Validar primeiro no `server1`, depois no Raspberry Pi e finalmente nos demais hosts.

## 13. Instruções ao agente implementador

Implementar código funcional, não apenas pseudocódigo. Se uma dependência externa (especialmente distribuição/licença da Ookla para ARM) impedir uma funcionalidade, relatar claramente a limitação e entregar o restante operante; **não inventar compatibilidade**. Não criar funcionalidades fora do escopo sem consultar. Entregar árvore de arquivos, instruções de build/deploy, testes executados e pendências reais. Priorizar código simples, extensível e robusto.
