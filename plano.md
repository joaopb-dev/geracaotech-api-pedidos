# API de pedidos — plano do Projeto B

- **Projeto:** API de pedidos que demonstra o fluxo completo de uma aplicação até sua operação e teste de carga.
- **Nível:** Projeto B.
- **Repositório:** https://github.com/joaopb-dev/geracaotech-api-pedidos
- **Stack:** Python padrão e SQLite; aplicação em contêiner com Docker Compose, com CI.
- **Responsável:** João Pedro Batista Barbosa.
- **Última atualização:** 2026-11-18.

**Convenções das tarefas:** `[ ]` pendente; `[~]` em andamento; `[X]` concluído e verificado.

## 1. O que é o projeto

Uma API para criar e consultar pedidos. O consumidor envia itens, quantidades e preços; a aplicação valida os dados, calcula o total e persiste o pedido. Em seguida, é possível consultá-lo pelo identificador, inclusive após reiniciar a aplicação.

**Fluxo de demonstração:** iniciar a aplicação → criar pedido → receber identificador e total → consultar pedido → executar testes e consultar métricas → apresentar o resultado do smoke test.

**Regras:** pedido com ao menos um item; nome não vazio; quantidade inteira positiva; preço unitário não negativo; total calculado no servidor. Valores monetários em centavos inteiros para evitar erros de ponto flutuante.

## 2. Objetivos e limites

### Objetivos

- Fluxo principal funcional, persistente e fácil de demonstrar.
- Atender aos requisitos de Compose, SOLID e um padrão de projeto justificado.
- Testes unitários e de integração, cobertura mínima e CI verde.
- Configuração segura, logs estruturados, uma métrica e um SLO.
- Documentar operação, decisão técnica, contrato, desempenho, autoria e uso de IA.

### Fora do escopo

- Marketplace com múltiplos módulos, pagamentos reais, autenticação, interface gráfica e integrações externas.
- Os 100 mil pedidos, os diagramas C4 e o teste em três estágios do Projeto A.
- Funcionalidades extras antes de concluir e validar os requisitos do Projeto B.

## 3. Regras de trabalho

- **Escopo primeiro:** fluxo mínimo e itens obrigatórios antes de melhorias opcionais.
- **Evidência:** executar testes e registrar resultados reais; não inventar cobertura, desempenho ou CI verde.
- **Regressões:** ao corrigir um erro, adicionar teste relevante ou registrar reprodução e verificação manual.
- **Segredos:** configuração no ambiente, somente exemplos sem credenciais; revisar arquivos antes de publicar.
- **Dados:** usar dados sintéticos em testes e demonstração; respeitar licenças e autoria de materiais reutilizados.
- **Simplicidade:** separar responsabilidades sem arquitetura excessiva para um domínio único; dependências com justificativa.
- **Autoria:** registrar contribuições reais e uso de IA; quem apresentar deve explicar as decisões e o código.

## 4. Arquitetura

```text
Cliente HTTP / k6
        │
        ▼
API: rotas, validação e respostas ──► logs estruturados / métrica
        │
        ▼
Caso de uso e regras de pedido
        │
        ▼
Interface de persistência ──► SQLite
```

- **API:** recebe requisições, valida o formato e traduz resultados em respostas HTTP.
- **Domínio e caso de uso:** aplicam regras, calculam total e coordenam criação e consulta.
- **Persistência:** armazena e recupera pedidos.
- **Operação:** configuração externa, logs estruturados e métrica verificável.
- **Padrão:** Repository, para separar as regras do mecanismo de persistência; justificado na ADR 0001.

### Estrutura

```text
README.md                         # Projeto B na primeira linha
CONTRIBUTORS.md
plano.md
docker-compose.yml
Dockerfile
.env.example                      # sem segredos reais
docs/
  adr/0001-decisao.md
  openapi.yaml
  desempenho.md
  ia.md
src/                              # aplicação e regras de domínio
tests/                            # testes unitários e de integração
k6/                               # smoke test
.github/workflows/ci.yml
```

## 5. Decisões

- **Repositório:** `geracaotech-api-pedidos`, publicado na branch `main`.
- **Domínio:** pedidos.
- **Persistência e stack:** Python padrão e SQLite.
- **Padrão:** Repository.
- **Cobertura:** mínimo de 80% no domínio.
- **SLO:** 99% sem erro 5xx nas rotas de pedidos em 30 dias.
- **Responsável:** João Pedro Batista Barbosa; assistência de IA registrada em `CONTRIBUTORS.md` e `docs/ia.md`.

## 6. Fases e tarefas

### Fase 0 — Fundação

- [X] Ler o enunciado e criar o plano inicial.
- [X] Adaptar o plano ao documento de referência.
- [X] Verificar ferramentas disponíveis e evidências existentes no repositório e no CI.
- [X] Definir stack, persistência, padrão de projeto e limiar de cobertura.
- [X] Preparar estrutura básica, gestão de dependências e `.gitignore`.
- [X] Criar ADR com contexto, decisão, alternativa descartada e consequências.

### Fase 1 — Fluxo principal

- [X] Implementar modelo e regras de pedidos, incluindo cálculo monetário seguro.
- [X] Implementar armazenamento persistente e inicialização necessária.
- [X] Implementar criação e consulta por identificador, com validação e respostas de erro.
- [X] Criar configuração externa e exemplo seguro de variáveis.
- [X] Criar Dockerfile e Compose; validar inicialização e persistência após reinício no CI.

### Fase 2 — Qualidade e CI

- [X] Testar regras de domínio com casos válidos e inválidos e totais esperados.
- [X] Testar integração do fluxo de criação e consulta, incluindo tratamento de erro.
- [X] Configurar e executar lint, testes e cobertura com limiar declarado no CI.
- [X] Configurar CI para instalar dependências e executar lint, testes e cobertura.
- [X] Verificar execução verde do CI no repositório para o commit `94cf865`.

### Fase 3 — Operação e desempenho

- [X] Produzir logs estruturados para requisições e erros, sem dados sensíveis.
- [X] Disponibilizar uma métrica útil e verificar seu comportamento.
- [X] Declarar SLO com indicador, alvo e janela de avaliação.
- [X] Criar smoke test k6 para o endpoint principal, com verificações de resposta.
- [X] Executar o teste e registrar comando, cenário, ambiente, p95 real e interpretação em `docs/desempenho.md`.

### Fase 4 — Documentação e revisão

- [X] Finalizar README com nível na primeira linha, pré-requisitos, configuração, execução, exemplos e testes.
- [X] Criar OpenAPI do endpoint principal, incluindo corpo, respostas e erros; validar o arquivo.
- [X] Documentar contribuições e uso de IA em `CONTRIBUTORS.md` e `docs/ia.md`; a confirmação da autoria e das decisões cabe ao responsável.
- [~] Conferir o fluxo, testes, métrica e documentação seguindo o README: lint, cobertura, testes e fluxo HTTP com reinício foram verificados; Docker Compose foi verificado no CI.
- [~] Revisar segredos, autoria e estado do repositório: busca textual não identificou credenciais óbvias; a coleção do Postman ainda está fora do Git; confirmação final de autoria cabe ao responsável.
- [X] Corrigir e executar a coleção do Postman; as pastas 1 a 5 e a persistência após reinício foram verificadas com Newman.
- [X] Alinhar o contrato OpenAPI e a validação de números inteiros, aceitando valores inteiros em notação decimal e científica sem arredondar frações.

## 7. Estado atual

**Atualizado em 2026-11-18.**

- **Aplicação:** API Python com criação, consulta, validação, SQLite, logs, métrica e Compose implementados.
- **Testes:** 9 testes passaram; lint aprovado e cobertura de linhas e desvios no domínio de 100%, medidos em ambiente Python temporário. Integração automatizada usa HTTP em memória e SQLite real.
- **Git:** `main` publicada no commit `94cf865`; `docs/postman_collection.json` está fora do Git.
- **CI:** [execução verde 44422594420](https://github.com/joaopb-dev/geracaotech-api-pedidos/actions/runs/44422594420) para o commit publicado, incluindo lint, testes, cobertura, Compose, persistência e k6; as alterações locais posteriores ainda não têm execução remota.
- **Desempenho:** medições de p95 e condições de execução registradas em `docs/desempenho.md`.
- **Revisão:** o OpenAPI passou no `openapi-spec-validator` e a API trata `1.0` como inteiro, mantendo precisão nas validações. Com Newman, passaram 30 requisições e 70 verificações nas pastas automáticas, além de 3 verificações de persistência após reiniciar a instância de teste. O fluxo Compose foi exercitado no CI.
- **Pendências:** incluir a coleção e as alterações locais no Git quando forem publicadas; confirmar autoria.

## 8. Critérios de conclusão

| Marco | Evidência necessária |
|---|---|
| Fundação | Ferramentas e Git verificados; stack e decisões registradas. |
| Fluxo | Compose inicia com um comando; pedido criado e consultado; erros tratados; dados sobrevivem ao reinício. |
| Qualidade | Testes unitários e de integração passam; cobertura atende o mínimo; lint passa; CI verde. |
| Operação | Logs estruturados e métrica observados; SLO definido; smoke test executado e p95 documentado. |
| Documentação | README reproduzível, ADR, OpenAPI, desempenho, contribuições e IA completos; repositório e CI acessíveis. |

## 9. Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Escopo excessivo | Projeto incompleto | Limitar ao fluxo de pedidos e adiar funcionalidades opcionais. |
| Docker ou k6 indisponíveis | Validação ou execução bloqueada | Verificar ferramentas no início e usar o ambiente disponível. |
| CI sem execução verde | Falta evidência de qualidade | Acompanhar a execução remota e validar localmente. |
| Falta de medição real | Evidências incompletas | Verificar persistência após reinício e registrar resultados reais. |
| Segredo ou dado pessoal publicado | Exposição de dados | Usar exemplos sintéticos e revisar antes de publicar. |
| Dependência externa ou material de terceiros | Bloqueio ou autoria incorreta | Identificar participantes e documentar contribuições efetivas. |
