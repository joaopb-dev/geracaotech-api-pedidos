# Desempenho e smoke test

## Cenário

`k6/smoke.js` envia pedidos sintéticos para `POST /orders` durante 10 segundos com um usuário virtual. Verifica o status 201 e o total calculado; os limiares exigem sucesso de todas as verificações e ausência de falhas HTTP. O relatório do k6 contém o p95 de `http_req_duration`.

## Execução

1. Inicie a API com `docker compose up --build -d`.
2. Execute `k6 run k6/smoke.js` (ou `BASE_URL=http://host:porta k6 run k6/smoke.js`).
3. Também é possível consultar o job `smoke-compose` do GitHub Actions e baixar o artefato `resultado-k6`.
4. O teste cria registros persistentes; não o execute em dados de produção.

## Resultado

Medição real de 2026-11-18, executada localmente antes da publicação:

- **Comando:** `k6 run k6/smoke.js`
- **Ambiente:** API em contêiner (`python:3.13-alpine`) com SQLite em volume, executada via Podman em Linux x86_64; k6 v0.54.0 na mesma máquina.
- **Cenário:** 1 VU, duração de 10 s, 295 requisições, 29,4 req/s.
- **Falhas:** `http_req_failed` 0,00% (0 de 295); `checks` 100% (590 de 590).
- **`http_req_duration`:** média 33,59 ms, mediana 27,99 ms, **p95 52,74 ms**, p90 42,49 ms, máximo 341,09 ms.
- **`http_req_waiting`:** média 33,42 ms, p95 52,52 ms.

Interpretação: nesta execução com um único usuário virtual, o p95 ficou abaixo de 60 ms e não houve falha HTTP. O teste não identifica, por si só, a causa da latência. Ele valida o endpoint principal sob carga leve e não representa cenário de produção nem sustenta sozinho o SLO de 30 dias.

### Execução no CI

O job `smoke-compose` do GitHub Actions repete o mesmo cenário a cada push. Nesta medição (run `44422096083`, 2026-11-18):

- **Comando:** `grafana/k6:0.54.0 run /scripts/smoke.js` dentro do workflow.
- **Ambiente:** runner `ubuntu-latest`, API em contêiner Docker com SQLite em volume.
- **Resultado:** 3341 requisições em 10 s (334,1 req/s), `checks` 100% (6682 de 6682), `http_req_failed` 0,00% (0 de 3341).
- **`http_req_duration`:** média 2,75 ms, mediana 1,63 ms, **p95 2,37 ms**, p90 1,87 ms, máximo 407,02 ms.

Comparação: o p95 no CI foi cerca de 22x menor que na execução local (2,37 ms contra 52,74 ms). Os ambientes são diferentes e o teste não isola a causa dessa diferença; para avaliar alterações, compare execuções nas mesmas condições.

Limitações: execução única, sem isolamento de hardware, com outros processos na máquina e sem repetição para intervalo de confiança. Para comparar alterações, repetir o mesmo cenário no mesmo ambiente e guardar o artefato do CI.

## SLO

O objetivo de disponibilidade e sua janela estão descritos no README. O smoke test avalia um cenário curto e não demonstra, sozinho, o cumprimento do SLO de 30 dias.
