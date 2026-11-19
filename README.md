Projeto B — API de pedidos

API de domínio único que cria e consulta pedidos, calcula o total em centavos e persiste os dados em SQLite. O servidor usa apenas a biblioteca padrão do Python. A documentação do contrato está em [docs/openapi.yaml](docs/openapi.yaml).

## Requisitos e inicialização

É necessário Docker com o plugin Compose. Na raiz do projeto:

```sh
docker compose up --build -d
```

A API fica em `http://localhost:8080`. Opcionalmente, copie `.env.example` para `.env` e ajuste `PORT` e `LOG_LEVEL`. O volume nomeado `orders_data` conserva os pedidos após reiniciar os contêineres. Para parar: `docker compose down`. Não acrescente `-v` se quiser preservar os dados.

Também é possível executar diretamente com Python 3.13 ou posterior: `python -m src.app`. As variáveis `PORT` e `DATABASE_PATH` são opcionais; por padrão a aplicação usa a porta 8080 e `data/orders.db`.

## Uso

```sh
curl -sS -X POST http://localhost:8080/orders \
  -H 'Content-Type: application/json' \
  -d '{"items":[{"name":"Livro","quantity":2,"unit_price_cents":1299}]}'
```

A resposta é `201`, com `id`, itens e `total_cents` (2598). Consulte usando o `id` devolvido:

```sh
curl -sS http://localhost:8080/orders/COLE_O_ID
curl -sS http://localhost:8080/health
curl -sS http://localhost:8080/metrics
```

Os preços são inteiros em centavos. Itens exigem nome, quantidade inteira positiva e preço inteiro não negativo. Números de valor inteiro, como `2.0` ou `2e0`, também são aceitos e retornados como inteiros; valores fracionários são rejeitados. Entradas inválidas recebem 400; pedido inexistente, 404; tipo de conteúdo inadequado, 415.

Para testar no Postman, importe [a coleção](docs/postman_collection.json), use `http://localhost:8080` como `base_url` e execute as pastas 1 a 5 na ordem. A pasta 6 é manual: reinicie a API antes de executá-la para verificar a persistência.

## Testes e CI

```sh
python -m pip install -r requirements-dev.txt
python -m ruff check src tests
python -m coverage run -m unittest discover -s tests -v
python -m coverage report
```

O mínimo configurado é **80% de cobertura de linhas e desvios combinados** para as regras de domínio em `src/domain.py`. Os testes unitários e de integração também podem ser executados sem instalar dependências com `python -m unittest discover -s tests -v`. A integração utiliza requisições HTTP em memória e SQLite real, cobrindo criação, consulta e reabertura do banco. O GitHub Actions executa lint, testes e cobertura em cada push e pull request. Um segundo job sobe o Compose, verifica persistência após reiniciar e executa k6 em um contêiner; a saída fica disponível no artefato `resultado-k6` da execução.

## Operação e desempenho

As requisições e erros geram logs estruturados em JSON sem corpo da requisição. `/metrics` expõe o contador Prometheus `orders_http_requests_total`, com método, rota normalizada e status. **SLO proposto:** pelo menos 99% das requisições a `/orders` e `/orders/{id}` devem responder sem erro 5xx em uma janela móvel de 30 dias; erros 4xx são excluídos do numerador de falhas. Para avaliar em operação, um coletor precisa amostrar o contador ao longo da janela, considerando reinícios. O SLO é um objetivo, não uma alegação de resultado observado.

Com k6 instalado e API ativa, execute `k6 run k6/smoke.js`. O teste cria pedidos sintéticos durante 10 segundos; use um banco de teste. O resultado inclui `http_req_duration` e seu p95. Consulte [desempenho](docs/desempenho.md) para cenário, limitações e resultados medidos.

Decisão de arquitetura: [ADR 0001](docs/adr/0001-decisao.md). Contribuições: [CONTRIBUTORS.md](CONTRIBUTORS.md). Uso de IA: [docs/ia.md](docs/ia.md).
