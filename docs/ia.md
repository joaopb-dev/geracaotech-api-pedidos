# Uso de inteligência artificial

## Resumo

Este projeto foi desenvolvido com assistência da IA **MiMo-V2.6-Flash Free** (provedor OpenCode), usada como par de programação ao longo de toda a execução: leitura do enunciado, planejamento, implementação, verificação e revisão do material entregue.

A identificação da contribuição está em [`CONTRIBUTORS.md`](../CONTRIBUTORS.md). A responsabilidade pelas decisões, pela revisão do código e pela entrega é humana: nada foi publicado sem verificação, e todo número apresentado neste repositório foi medido no ambiente, não inferido pela IA.

## O que a IA fez

| Área | Contribuição |
|---|---|
| Enunciado | Extração e leitura do PDF do projeto final para identificar os requisitos do nível escolhido. |
| Planejamento | Criação e refinamento do `plano.md`, com escopo, fases, critérios de conclusão e riscos. |
| Implementação | Regras de domínio, persistência em SQLite, API HTTP, tratamento de erros, logs e métrica. |
| Qualidade | Testes unitários e de integração, configuração de lint e de cobertura com limiar. |
| Operação | `Dockerfile`, `docker-compose.yml`, workflow de CI e smoke test com k6. |
| Documentação | README, ADR, contrato OpenAPI, página de desempenho e este registro. |

## Prompts relevantes

Registrados na ordem em que orientaram o trabalho:

- “analise as opções que temos pra fazer e ajudar a implementar”;
- “crie um plano.md com o que devemos fazer, será o projeto b”;
- “se baseie nesse arquivo e deixe nosso plano.md mais completo”;
- “Implemente o plano.md até sua totalidade, o projeto B no caso”;
- “quero que você adicione seus créditos nos contribuitors no caso MiMo-V2.6-Flash Free”;
- “vamos pra implementação agora ... pode verificar o .pdf também pra tirar duvidas, nosso trabalho é o trabalho B”;

## Ferramentas e verificações executadas

- `pdftotext` para converter o enunciado em texto;
- `ruff` para lint (limpo);
- `coverage` com limiar de 80% no domínio (resultado medido: 100%);
- `unittest` para testes unitários e de integração (7 testes, todos aprovados);
- build e execução do contêiner, com teste de persistência após reinício;
- `k6` para o smoke test, com p95 medido e registrado em [`desempenho.md`](desempenho.md);
- varredura do repositório confirmando ausência de credenciais commitadas.

## Limites

A IA sugere alternativas e produz código; as decisões de arquitetura e a validação final são do responsável. Resultados de teste e de desempenho foram executados e observados no ambiente — não foram gerados como afirmações sem evidência.
