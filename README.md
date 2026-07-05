# OdontoMS Backend

Backend do **OdontoMS**, um sistema SaaS multi-tenant para gerenciamento de clínicas odontológicas.

O projeto fornece a API responsável por autenticação, gestão de clínicas, usuários, pacientes, procedimentos, expedientes, agendamentos, calendário e notificações automáticas via WhatsApp.

## Tecnologias

* **Backend**: Python, Django, Django REST Framework;
* **Bancos de dados**: MariaDB, Redis;
* **Filas**: RabbitMQ;
* **Integração externa**: Evolution API;
* **Infraestrutura**: Docker;
* **Documentação**: Swagger/OpenAPI.

## Como rodar localmente

Clone o repositório:

```bash
git clone <url-do-repositorio>
cd backend
```

Crie um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

Garanta a instalação do Poetry e instale as dependências:

```bash
pipx install poetry
poetry install
```

Preencha o `.env` com base no arquivo `.env.example`.

Aplique as migrations:

```bash
python manage.py migrate
```

Inicie o servidor:

```bash
python manage.py runserver
```

## RabbitMQ

O projeto utiliza RabbitMQ para processar lembretes de WhatsApp de forma assíncrona.

Para rodar localmente com Docker:

```bash
docker run -d --rm \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:4-management
```

O painel de administração fica disponível em:

```txt
http://localhost:15672
```

Credenciais padrão:

```txt
guest / guest
```

## Zap Worker

Para iniciar o consumer responsável pelo envio dos lembretes de WhatsApp, execute em outro terminal:

```bash
python manage.py startconsumer
```

Fluxo resumido:

```txt
agendamento criado
→ mensagem publicada na fila de delay
→ RabbitMQ entrega a mensagem 24h antes da consulta
→ consumer processa a mensagem
→ Evolution API envia o lembrete via WhatsApp
```

## Evolution API

O módulo de WhatsApp depende de uma instância da Evolution API em execução.

Configure as variáveis no `.env`:

```env
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua_api_key
```

## Documentação da API

A documentação Swagger fica disponível em:

```txt
/api/docs/
```

O schema OpenAPI fica disponível em:

```txt
/api/schema/
```

## Padrão de resposta

As respostas da API seguem um envelope comum:

```json
{
  "success": true,
  "message": "Operação realizada com sucesso.",
  "data": {},
  "errors": null,
  "meta": {}
}
```

Exemplo de erro:

```json
{
  "success": false,
  "message": "Falha ao realizar operação.",
  "data": null,
  "errors": {
    "campo": ["Mensagem de erro."]
  },
  "meta": {}
}
```

## Testes

Para rodar os testes:

```bash
python manage.py test
```

## Dados mock

Para popular o banco local com dados de teste para todas as telas do frontend:

```bash
python manage.py seedmockdata
```

Para limpar e recriar apenas os dados mock:

```bash
python manage.py seedmockdata --reset
```

Senha padrão dos usuários criados:

```txt
mock12345
```

Usuários principais:

```txt
app.admin@odontoms.local
admin.centro@odontoms.local
recepcao.centro@odontoms.local
ana.clinico@odontoms.local
bruno.clinico@odontoms.local
admin.norte@odontoms.local
recepcao.norte@odontoms.local
diego.clinico@odontoms.local
```

## Próximos passos

* Implementar frontend web;
* Criar dashboard operacional;
* Melhorar logs do worker;
* Adicionar Docker Compose para ambiente completo;
