# Guia Rápido de Deploy e Testes

## 🚀 Passo a Passo Completo

### 1️⃣ Instalar Dependências

```powershell
# Node.js / Serverless
npm install

# Python / Boto3
pip install -r requirements.txt
```

### 2️⃣ Iniciar LocalStack

```powershell
# Iniciar containers Docker
docker-compose up -d

# Verificar se está rodando (deve mostrar o container 'localstack-pecas')
docker ps

# Ver logs do LocalStack (opcional)
docker-compose logs -f
```

### 3️⃣ Deploy da Aplicação

```powershell
# Deploy no LocalStack
serverless deploy --stage local

# Aguarde o deploy completar. Você verá informações sobre:
# - Funções Lambda criadas
# - Endpoints da API
# - Recursos DynamoDB e SNS
```

### 4️⃣ Obter URL da API

Após o deploy, localize a URL da API na saída do comando. Ela será algo como:

```
endpoints:
  POST - http://localhost:4566/restapis/XXXXXXXXXX/local/_user_request_/items
  GET - http://localhost:4566/restapis/XXXXXXXXXX/local/_user_request_/items
  ...
```

**IMPORTANTE**: Anote o `API_ID` (a parte XXXXXXXXXX) para usar nos testes.

### 5️⃣ Testar os Endpoints

#### Exemplo 1: Criar Peça

```powershell
# Substitua XXXXXXXXXX pelo seu API_ID
$API_ID = "XXXXXXXXXX"
$BASE_URL = "http://localhost:4566/restapis/$API_ID/local/_user_request_"

# Criar uma vela de ignição
curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Vela de Ignição NGK",
    "codigo": "NGK-BKR6E",
    "preco": 29.90,
    "quantidade": 150,
    "descricao": "Vela de ignição padrão",
    "fabricante": "NGK"
  }'
```

**✅ Se funcionar, você verá:**
- Status 201 Created
- JSON com os dados da peça incluindo `id` gerado
- Logs no console do subscriber SNS

#### Exemplo 2: Criar Outra Peça

```powershell
# Filtro de óleo
curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Filtro de Óleo Mann",
    "codigo": "W610-1",
    "preco": 45.00,
    "quantidade": 80,
    "descricao": "Filtro de óleo para motores diesel",
    "fabricante": "Mann Filter"
  }'
```

#### Exemplo 3: Listar Todas as Peças

```powershell
curl "$BASE_URL/items"
```

**✅ Deve retornar:**
- Array com todas as peças criadas
- Contador de itens

#### Exemplo 4: Buscar por ID

```powershell
# Copie um ID da resposta anterior
$ITEM_ID = "cole-aqui-um-uuid"

curl "$BASE_URL/items/$ITEM_ID"
```

#### Exemplo 5: Atualizar Peça

```powershell
# Atualizar preço e quantidade
curl -X PUT "$BASE_URL/items/$ITEM_ID" `
  -H "Content-Type: application/json" `
  -d '{
    "preco": 27.90,
    "quantidade": 200
  }'
```

**✅ Isso vai:**
- Atualizar o item no DynamoDB
- Disparar notificação SNS
- Subscriber vai logar a atualização

#### Exemplo 6: Deletar Peça

```powershell
curl -X DELETE "$BASE_URL/items/$ITEM_ID"
```

### 6️⃣ Verificar Notificações SNS

```powershell
# Ver logs do subscriber em tempo real
serverless logs -f snsSubscriber --stage local --tail

# Ou ver logs de todas as funções
docker-compose logs -f
```

**Você deve ver logs como:**

```
================================================================================
🔔 NOTIFICAÇÃO SNS RECEBIDA
================================================================================
📋 Assunto: Peça Automotiva - CREATE
🔧 Operação: CREATE
📦 Dados da Peça:
{
  "id": "...",
  "nome": "Vela de Ignição NGK",
  ...
}
================================================================================
```

### 7️⃣ Verificar Recursos AWS no LocalStack

```powershell
# Ver tabela DynamoDB
aws dynamodb scan `
  --table-name pecas-automotivas-api-local `
  --endpoint-url=http://localhost:4566 `
  --region us-east-1

# Ver tópicos SNS
aws sns list-topics `
  --endpoint-url=http://localhost:4566 `
  --region us-east-1

# Ver funções Lambda
aws lambda list-functions `
  --endpoint-url=http://localhost:4566 `
  --region us-east-1
```

## 🧪 Script de Teste Completo

Salve este script como `test-api.ps1`:

```powershell
# Configuração
$API_ID = "SEU_API_ID_AQUI"  # Substitua pelo seu API ID
$BASE_URL = "http://localhost:4566/restapis/$API_ID/local/_user_request_"

Write-Host "`n=== TESTE 1: Criar Peça ===" -ForegroundColor Cyan
$response1 = curl -X POST "$BASE_URL/items" `
  -H "Content-Type: application/json" `
  -d '{
    "nome": "Vela de Ignição NGK",
    "codigo": "NGK-BKR6E",
    "preco": 29.90,
    "quantidade": 150,
    "fabricante": "NGK"
  }' | ConvertFrom-Json

$ITEM_ID = $response1.item.id
Write-Host "✅ Peça criada com ID: $ITEM_ID" -ForegroundColor Green

Write-Host "`n=== TESTE 2: Listar Peças ===" -ForegroundColor Cyan
curl "$BASE_URL/items"

Write-Host "`n=== TESTE 3: Buscar por ID ===" -ForegroundColor Cyan
curl "$BASE_URL/items/$ITEM_ID"

Write-Host "`n=== TESTE 4: Atualizar Peça ===" -ForegroundColor Cyan
curl -X PUT "$BASE_URL/items/$ITEM_ID" `
  -H "Content-Type: application/json" `
  -d '{"preco": 27.90, "quantidade": 200}'

Write-Host "`n=== TESTE 5: Deletar Peça ===" -ForegroundColor Cyan
curl -X DELETE "$BASE_URL/items/$ITEM_ID"

Write-Host "`n✅ Todos os testes concluídos!" -ForegroundColor Green
```

Execute:

```powershell
.\test-api.ps1
```

## 🔧 Comandos de Manutenção

```powershell
# Limpar tudo e recomeçar
serverless remove --stage local
docker-compose down
docker-compose up -d
serverless deploy --stage local

# Ver logs específicos
serverless logs -f createItem --stage local
serverless logs -f updateItem --stage local
serverless logs -f snsSubscriber --stage local

# Invocar função diretamente (sem API Gateway)
serverless invoke local -f listItems
```

## ✅ Checklist de Validação

- [ ] LocalStack rodando (docker ps mostra container ativo)
- [ ] Deploy concluído sem erros
- [ ] POST cria item e retorna 201
- [ ] GET /items lista todos os itens
- [ ] GET /items/{id} retorna item específico
- [ ] PUT atualiza item e retorna 200
- [ ] DELETE remove item e retorna 200
- [ ] Subscriber SNS loga CREATE e UPDATE
- [ ] Validação rejeita dados inválidos (400)
- [ ] Busca de item inexistente retorna 404

## 🆘 Problemas Comuns

### "Connection refused"
```powershell
# Reiniciar LocalStack
docker-compose restart
```

### "Table not found"
```powershell
# Refazer deploy
serverless remove --stage local
serverless deploy --stage local
```

### "Module not found"
```powershell
# Reinstalar dependências
pip install -r requirements.txt
npm install
```

## 📊 Entrega do Trabalho

Para entregar o trabalho, inclua:

1. ✅ Código fonte (handler.py, serverless.yml, etc.)
2. ✅ README.md com documentação
3. ✅ Screenshots dos testes funcionando
4. ✅ Logs mostrando subscriber SNS
5. ✅ Arquivo com comandos utilizados

**Capturar evidências:**

```powershell
# Durante os testes, capture:
# - Resposta de cada endpoint
# - Logs do subscriber SNS
# - Lista de recursos criados no LocalStack

# Exemplo para salvar saída em arquivo:
curl "$BASE_URL/items" | Out-File -FilePath "./teste-listar.json"
serverless logs -f snsSubscriber --stage local | Out-File -FilePath "./logs-sns.txt"
```

Pronto! Agora você tem tudo para executar e testar a aplicação. 🚀
