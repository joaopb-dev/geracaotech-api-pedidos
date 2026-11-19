# ADR 0001 — Python e SQLite com Repository

- **Estado:** aceito para o escopo inicial.
- **Contexto:** entregar rapidamente uma API pequena, persistente e executável por Compose, com testes e pouca configuração.
- **Decisão:** utilizar a biblioteca padrão do Python para HTTP e SQLite, armazenando dados em volume persistente. A classe `OrderRepository` concentra acesso ao banco; o domínio não depende do mecanismo de armazenamento. É uma aplicação do padrão Repository e do princípio de responsabilidade única.
- **Alternativa descartada:** framework web e servidor PostgreSQL separados. Ofereceriam ecossistema e recursos para maior escala, mas exigiriam mais dependências e operação para o fluxo proposto.
- **Consequências:** instalação e testes são simples, sem dependências em produção; SQLite tem concorrência de escrita limitada e o servidor da biblioteca padrão é apropriado para demonstração, não para exposição direta em produção. Uma aplicação real precisaria avaliar servidor HTTP apropriado, proteção e banco conforme carga.
- **Aceite:** criação e consulta persistem após reabrir o banco, testes passam e Compose inicia a aplicação com volume.
