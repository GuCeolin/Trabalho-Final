# 🎓 Trabalho Universitário - API REST Serverless para Peças Automotivas

## 📋 Visão Geral do Projeto

Este projeto implementa uma **API REST Serverless completa** para gerenciamento de peças automotivas, utilizando a stack AWS simulada localmente via LocalStack. Desenvolvido como trabalho universitário seguindo a **Opção A** do roteiro.

### 🎯 Objetivos Alcançados

- ✅ CRUD completo de peças automotivas
- ✅ Persistência em DynamoDB
- ✅ Sistema de mensageria com SNS
- ✅ Subscriber Lambda para notificações
- ✅ Validação robusta de dados
- ✅ Simulação 100% local com LocalStack
- ✅ Testes automatizados completos

## 🏗️ Arquitetura da Solução

```
┌─────────────────────────────────────────────────────────────┐
│                         API Gateway                          │
│              http://localhost:4566/restapis/...              │
└─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
    ┌────▼─────┐            ┌─────▼────┐
    │ Lambda   │            │ Lambda   │
    │ Functions│            │ Functions│
    │ (CRUD)   │            │ (CRUD)   │
    └────┬─────┘            └─────┬────┘
         │                        │
         ├────────────┬───────────┤
         │            │           │
    ┌────▼─────┐  ┌──▼────┐  ┌──▼──────────┐
    │ DynamoDB │  │  SNS  │  │   Lambda     │
    │  Table   │  │ Topic │  │  Subscriber  │
    └──────────┘  └───────┘  └─────────────┘
```

### Componentes Principais

1. **6 Funções Lambda:**
   - `createItem` - Cria nova peça + publica SNS
   - `listItems` - Lista todas as peças
   - `getItem` - Busca peça por ID
   - `updateItem` - Atualiza peça + publica SNS
   - `deleteItem` - Remove peça
   - `snsSubscriber` - Processa notificações SNS

2. **Recursos AWS (LocalStack):**
   - DynamoDB Table: `pecas-automotivas-api-local`
   - SNS Topic: `pecas-automotivas-topic`
   - API Gateway: REST API completa

## 🛠️ Stack Tecnológica

- **Linguagem:** Python 3.9+
- **SDK AWS:** Boto3
- **Framework:** Serverless Framework v3
- **Simulação Cloud:** LocalStack (Docker)
- **Banco de Dados:** DynamoDB
- **Mensageria:** Amazon SNS
- **Testes:** Requests (Python)

## 📦 Estrutura do Projeto

```
Trabalho-Final/
├── handler.py              # Lógica das funções Lambda
├── serverless.yml          # Configuração Serverless Framework
├── docker-compose.yml      # Setup do LocalStack
├── requirements.txt        # Dependências Python
├── package.json            # Dependências Node.js
├── teste_api.py           # Script de testes automatizado
├── setup.ps1              # Script de setup automatizado (PowerShell)
├── README.md              # Documentação principal
├── DEPLOY.md              # Guia detalhado de deploy
├── EXEMPLOS.md            # Exemplos de requisições
├── GUIA_RAPIDO.md         # Início rápido
└── .gitignore             # Arquivos ignorados
```

## 🚀 Como Executar

### Opção 1: Setup Automatizado (Recomendado)

```powershell
# Executa todo o processo: dependências, LocalStack, deploy e testes
.\setup.ps1

# Ou com limpeza completa antes:
.\setup.ps1 -Clean

# Ou sem executar os testes:
.\setup.ps1 -SkipTests
```

### Opção 2: Passo a Passo Manual

```powershell
# 1. Instalar dependências
npm install
pip install -r requirements.txt

# 2. Iniciar LocalStack
docker-compose up -d

# 3. Deploy da aplicação
serverless deploy --stage local

# 4. Executar testes
python teste_api.py
```

## 📊 Endpoints da API

| Método | Endpoint | Descrição | Dispara SNS |
|--------|----------|-----------|-------------|
| POST | `/items` | Criar peça | ✅ Sim |
| GET | `/items` | Listar todas | ❌ Não |
| GET | `/items/{id}` | Buscar por ID | ❌ Não |
| PUT | `/items/{id}` | Atualizar peça | ✅ Sim |
| DELETE | `/items/{id}` | Deletar peça | ❌ Não |

### Modelo de Dados: Peça Automotiva

```json
{
  "id": "uuid-gerado-automaticamente",
  "nome": "string (obrigatório)",
  "codigo": "string (obrigatório)",
  "preco": "number (obrigatório, >= 0)",
  "quantidade": "integer (obrigatório, >= 0)",
  "descricao": "string (opcional)",
  "fabricante": "string (opcional)",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp"
}
```

## 🧪 Testes Automatizados

O script `teste_api.py` executa uma suíte completa de testes:

```powershell
# Executar com API ID específico
python teste_api.py abc123def456

# Ou deixar detectar automaticamente
python teste_api.py
```

### Cobertura de Testes

1. ✅ **Criar Itens** - Valida POST com sucesso
2. ✅ **Listar Itens** - Valida GET collection
3. ✅ **Buscar por ID** - Valida GET específico
4. ✅ **Atualizar Item** - Valida PUT com sucesso
5. ✅ **Deletar Item** - Valida DELETE
6. ✅ **Validações** - Testa erros 400, 404
7. ✅ **SNS** - Verifica publicação de mensagens

## 📨 Sistema de Notificações SNS

### Quando é Disparado?

- ✅ Ao **CRIAR** uma nova peça (POST)
- ✅ Ao **ATUALIZAR** uma peça existente (PUT)
- ❌ Não dispara em GET ou DELETE

### Estrutura da Mensagem SNS

```json
{
  "operation": "CREATE",
  "timestamp": "2025-12-16T10:30:00.123456",
  "item": {
    "id": "abc-123",
    "nome": "Vela de Ignição",
    "codigo": "NGK-001",
    "preco": 29.90,
    ...
  }
}
```

### Ver Logs do Subscriber

```powershell
# Logs em tempo real
serverless logs -f snsSubscriber --stage local --tail

# Ou via Docker
docker-compose logs -f localstack
```

## 🔍 Validações Implementadas

### Campos Obrigatórios
- `nome` - Nome da peça
- `codigo` - Código único
- `preco` - Preço (número >= 0)
- `quantidade` - Quantidade em estoque (inteiro >= 0)

### Regras de Validação
- Preço não pode ser negativo
- Quantidade não pode ser negativa
- JSON deve ser válido
- Item deve existir para UPDATE/DELETE

### Códigos de Erro
- `400 Bad Request` - Dados inválidos
- `404 Not Found` - Item não encontrado
- `500 Internal Server Error` - Erro no servidor

## 🔧 Comandos Úteis

### Gerenciamento da API

```powershell
# Informações da API
serverless info --stage local

# Ver logs de uma função
serverless logs -f createItem --stage local

# Invocar função localmente
serverless invoke local -f listItems

# Remover deploy
serverless remove --stage local
```

### Gerenciamento do LocalStack

```powershell
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Reiniciar (limpar dados)
docker-compose down -v
docker-compose up -d

# Verificar saúde
curl http://localhost:4566/_localstack/health
```

### AWS CLI com LocalStack

```powershell
# Listar tabelas DynamoDB
aws dynamodb list-tables `
  --endpoint-url=http://localhost:4566 `
  --region us-east-1

# Escanear tabela
aws dynamodb scan `
  --table-name pecas-automotivas-api-local `
  --endpoint-url=http://localhost:4566 `
  --region us-east-1

# Listar tópicos SNS
aws sns list-topics `
  --endpoint-url=http://localhost:4566 `
  --region us-east-1

# Listar funções Lambda
aws lambda list-functions `
  --endpoint-url=http://localhost:4566 `
  --region us-east-1
```

## 💡 Compatibilidade com LocalStack

### Configuração Específica

O projeto foi desenvolvido seguindo rigorosamente o padrão do LocalStack:

1. **Porta Única:** 4566 (gateway unificado)
2. **Detecção de Ambiente:** Automática via variáveis
3. **Endpoint Fixo:** `http://localhost:4566`
4. **Região:** `us-east-1` (padrão)
5. **Credenciais Fake:** `test/test`

### Código de Detecção

```python
def is_local_environment():
    indicators = [
        os.environ.get('LOCALSTACK_HOSTNAME'),
        os.environ.get('AWS_SAM_LOCAL') == 'true',
        os.environ.get('IS_OFFLINE') == 'true',
        not os.environ.get('AWS_EXECUTION_ENV')
    ]
    return any(indicators)
```

## 📚 Documentação Adicional

- **DEPLOY.md** - Guia detalhado passo a passo
- **EXEMPLOS.md** - Exemplos completos de requisições
- **GUIA_RAPIDO.md** - Referência rápida de comandos

## ✅ Requisitos do Trabalho Atendidos

- [x] CRUD completo implementado
- [x] Persistência em DynamoDB
- [x] Publicação SNS em CREATE e UPDATE
- [x] Subscriber Lambda funcional
- [x] Validação de campos obrigatórios
- [x] Tratamento de erros robusto
- [x] Simulação local com LocalStack
- [x] Documentação completa
- [x] Script de testes automatizado
- [x] Código limpo e comentado

## 🐛 Troubleshooting

### LocalStack não inicia
```powershell
docker-compose down -v
docker-compose up -d
docker-compose logs -f
```

### Deploy falha
```powershell
# Verificar plugin
npm install --save-dev serverless-localstack

# Verificar LocalStack está rodando
curl http://localhost:4566/_localstack/health
```

### Testes falham
```powershell
# Obter API ID correto
serverless info --stage local

# Executar com API ID explícito
python teste_api.py SEU_API_ID_AQUI
```

### Credenciais AWS
O projeto usa credenciais fake (`test/test`) para LocalStack.
**Não** é necessário configurar credenciais AWS reais.

## 👨‍💻 Autor

**Trabalho Universitário - Computação em Nuvem**  
Implementação: Opção A - CRUD Serverless  
Data: Dezembro 2025

## 📄 Licença

Este projeto é de código aberto e está disponível para fins educacionais.

---

**🎯 Pronto para usar!** Execute `.\setup.ps1` e comece a testar sua API serverless. 🚀
