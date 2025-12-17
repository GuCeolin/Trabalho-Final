# 🧪 Exemplos de Testes da API

Este arquivo contém exemplos práticos de requisições para testar todos os endpoints da API.

## ⚙️ Configuração Inicial

```powershell
# Defina o API_ID após fazer o deploy
$API_ID = "COLOQUE_SEU_API_ID_AQUI"
$BASE_URL = "http://localhost:4566/restapis/$API_ID/local/_user_request_"
```

## 📝 Exemplos de Peças para Cadastro

### 1. Vela de Ignição

```powershell
curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Vela de Ignição NGK Laser Platinum",
    "codigo": "NGK-BKR6E-11",
    "preco": 29.90,
    "quantidade": 150,
    "descricao": "Vela de ignição com eletrodo de platina para motores 1.0 a 1.6",
    "fabricante": "NGK"
  }'
```

### 2. Filtro de Óleo

```powershell
curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Filtro de Óleo Mann W610/1",
    "codigo": "MANN-W610-1",
    "preco": 45.00,
    "quantidade": 80,
    "descricao": "Filtro de óleo para motores a diesel e gasolina",
    "fabricante": "Mann Filter"
  }'
```

### 3. Pastilha de Freio

```powershell
curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Pastilha de Freio Dianteira",
    "codigo": "BOSCH-BB123",
    "preco": 89.90,
    "quantidade": 45,
    "descricao": "Pastilha de freio dianteira para veículos de passeio",
    "fabricante": "Bosch"
  }'
```

### 4. Correia Dentada

```powershell
curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Correia Dentada com Kit",
    "codigo": "GATES-K015607XS",
    "preco": 285.00,
    "quantidade": 25,
    "descricao": "Kit completo de correia dentada com tensor e roldanas",
    "fabricante": "Gates"
  }'
```

### 5. Bateria Automotiva

```powershell
curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Bateria 60Ah Selada",
    "codigo": "MOURA-60GD",
    "preco": 389.90,
    "quantidade": 15,
    "descricao": "Bateria automotiva 60Ah 12V selada livre de manutenção",
    "fabricante": "Moura"
  }'
```

### 6. Amortecedor

```powershell
curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Amortecedor Dianteiro Gas",
    "codigo": "COFAP-GB27123",
    "preco": 175.00,
    "quantidade": 30,
    "descricao": "Amortecedor dianteiro a gás para veículos de passeio",
    "fabricante": "Cofap"
  }'
```

## 🔍 Testes de Leitura

### Listar Todas as Peças

```powershell
# GET /items
curl "$BASE_URL/items"
```

**Resposta esperada:**
```json
{
  "items": [
    {
      "id": "uuid-1",
      "nome": "Vela de Ignição NGK...",
      ...
    },
    {
      "id": "uuid-2",
      "nome": "Filtro de Óleo Mann...",
      ...
    }
  ],
  "count": 6
}
```

### Buscar Peça por ID

```powershell
# Substitua pelo ID real de um item
$ITEM_ID = "cole-o-uuid-aqui"

curl "$BASE_URL/items/$ITEM_ID"
```

**Resposta esperada (200 OK):**
```json
{
  "item": {
    "id": "uuid-aqui",
    "nome": "Vela de Ignição NGK...",
    "codigo": "NGK-BKR6E-11",
    "preco": 29.90,
    ...
  }
}
```

**Caso não encontre (404 Not Found):**
```json
{
  "error": "Peça não encontrada"
}
```

## ✏️ Testes de Atualização

### Atualizar Preço e Quantidade

```powershell
curl -X PUT "$BASE_URL/items/$ITEM_ID" `
  -H "Content-Type: application/json" `
  -d '{
    "preco": 27.90,
    "quantidade": 200
  }'
```

### Atualizar Apenas a Descrição

```powershell
curl -X PUT "$BASE_URL/items/$ITEM_ID" `
  -H "Content-Type: application/json" `
  -d '{
    "descricao": "Nova descrição detalhada do produto"
  }'
```

### Atualização Completa

```powershell
curl -X PUT "$BASE_URL/items/$ITEM_ID" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Vela de Ignição NGK Iridium",
    "codigo": "NGK-BKR6EIX",
    "preco": 35.90,
    "quantidade": 180,
    "descricao": "Vela premium com eletrodo de irídio",
    "fabricante": "NGK"
  }'
```

## 🗑️ Testes de Exclusão

### Deletar uma Peça

```powershell
curl -X DELETE "$BASE_URL/items/$ITEM_ID"
```

**Resposta esperada (200 OK):**
```json
{
  "message": "Peça deletada com sucesso",
  "id": "uuid-aqui"
}
```

## ❌ Testes de Validação (Erros Esperados)

### Campos Obrigatórios Faltando

```powershell
# Erro: falta o campo 'quantidade'
curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Produto Incompleto",
    "codigo": "INC-001",
    "preco": 50.00
  }'
```

**Resposta esperada (400 Bad Request):**
```json
{
  "error": "Campos obrigatórios faltando: quantidade"
}
```

### Preço Negativo

```powershell
curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Produto Inválido",
    "codigo": "INV-001",
    "preco": -10.00,
    "quantidade": 5
  }'
```

**Resposta esperada (400 Bad Request):**
```json
{
  "error": "Preço não pode ser negativo"
}
```

### JSON Inválido

```powershell
curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d 'JSON-MALFORMADO{nome}'
```

**Resposta esperada (400 Bad Request):**
```json
{
  "error": "JSON inválido"
}
```

### Item Não Encontrado

```powershell
# Usando um UUID que não existe
curl "$BASE_URL/items/00000000-0000-0000-0000-000000000000"
```

**Resposta esperada (404 Not Found):**
```json
{
  "error": "Peça não encontrada"
}
```

## 📊 Fluxo Completo de Teste

```powershell
# 1. CRIAR uma peça
Write-Host "`n1️⃣ Criando peça..." -ForegroundColor Yellow
$response = curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Teste Completo",
    "codigo": "TEST-001",
    "preco": 100.00,
    "quantidade": 10,
    "fabricante": "Teste"
  }' | ConvertFrom-Json

$ITEM_ID = $response.item.id
Write-Host "✅ Criado com ID: $ITEM_ID" -ForegroundColor Green

# 2. LISTAR todas
Write-Host "`n2️⃣ Listando todas as peças..." -ForegroundColor Yellow
curl "$BASE_URL/items"

# 3. BUSCAR por ID
Write-Host "`n3️⃣ Buscando peça por ID..." -ForegroundColor Yellow
curl "$BASE_URL/items/$ITEM_ID"

# 4. ATUALIZAR
Write-Host "`n4️⃣ Atualizando peça..." -ForegroundColor Yellow
curl -X PUT "$BASE_URL/items/$ITEM_ID" `
  -H "Content-Type: application/json" `
  -d '{"preco": 95.00, "quantidade": 15}'

# 5. VERIFICAR atualização
Write-Host "`n5️⃣ Verificando atualização..." -ForegroundColor Yellow
curl "$BASE_URL/items/$ITEM_ID"

# 6. DELETAR
Write-Host "`n6️⃣ Deletando peça..." -ForegroundColor Yellow
curl -X DELETE "$BASE_URL/items/$ITEM_ID"

# 7. VERIFICAR exclusão (deve retornar 404)
Write-Host "`n7️⃣ Tentando buscar peça deletada (deve dar 404)..." -ForegroundColor Yellow
curl "$BASE_URL/items/$ITEM_ID"

Write-Host "`n✅ Teste completo finalizado!" -ForegroundColor Green
```

## 📨 Verificar Notificações SNS

### Ver Logs do Subscriber

```powershell
# Logs em tempo real
serverless logs -f snsSubscriber --stage local --tail

# Ou ver logs do Docker
docker-compose logs -f localstack
```

### Exemplo de Log Esperado

Quando você criar ou atualizar uma peça, deve ver algo assim:

```
================================================================================
🔔 NOTIFICAÇÃO SNS RECEBIDA
================================================================================

📋 Assunto: Peça Automotiva - CREATE
📅 Timestamp: 2025-12-15T14:30:25.123Z
🔧 Operação: CREATE
⏰ Data/Hora: 2025-12-15T14:30:25.123456

📦 Dados da Peça:
{
  "id": "abc-123-def-456",
  "nome": "Vela de Ignição NGK Laser Platinum",
  "codigo": "NGK-BKR6E-11",
  "preco": 29.9,
  "quantidade": 150,
  "descricao": "Vela de ignição com eletrodo de platina...",
  "fabricante": "NGK",
  "created_at": "2025-12-15T14:30:25.123456",
  "updated_at": "2025-12-15T14:30:25.123456"
}
================================================================================
```

## 🔧 Ferramentas Auxiliares

### Usar Postman

Se preferir usar Postman em vez de curl:

1. Importe esta coleção base:
   - Base URL: `http://localhost:4566/restapis/{{API_ID}}/local/_user_request_`
   - Headers: `Content-Type: application/json`

2. Crie variáveis de ambiente:
   - `API_ID`: seu ID da API
   - `ITEM_ID`: ID de teste

### Usar AWS CLI

```powershell
# Escanear tabela DynamoDB
aws dynamodb scan `
  --table-name pecas-automotivas-api-local `
  --endpoint-url=http://localhost:4566 `
  --region us-east-1

# Ver item específico
aws dynamodb get-item `
  --table-name pecas-automotivas-api-local `
  --key '{"id":{"S":"seu-uuid-aqui"}}' `
  --endpoint-url=http://localhost:4566 `
  --region us-east-1
```

## 💡 Dicas

- **Sempre salve os IDs** retornados nas criações para usar nos testes seguintes
- **Verifique os logs** do subscriber SNS após CREATE e UPDATE
- **Use ferramentas como Postman** para testes mais visuais
- **Capture screenshots** das respostas para documentação do trabalho
- **Teste os casos de erro** para demonstrar validação robusta

Bons testes! 🚀
