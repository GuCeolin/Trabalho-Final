# Script de Setup e Teste Automatizado
# Execute este script para configurar e testar toda a aplicação

param(
    [switch]$Clean,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

# Cores para output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-ColorOutput "================================================================================" "Cyan"
    Write-ColorOutput "  $Message" "Cyan"
    Write-ColorOutput "================================================================================" "Cyan"
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" "Green"
}

function Write-Error-Custom {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ️  $Message" "Yellow"
}

# Início
Write-Header "🚗 SETUP AUTOMÁTICO - API PEÇAS AUTOMOTIVAS"

# Limpeza (se solicitado)
if ($Clean) {
    Write-Header "LIMPEZA DE AMBIENTE"
    
    Write-Info "Removendo deploy anterior..."
    try {
        serverless remove --stage local
        Write-Success "Deploy anterior removido"
    } catch {
        Write-Info "Nenhum deploy anterior encontrado"
    }
    
    Write-Info "Parando containers Docker..."
    docker-compose down -v
    Write-Success "Containers parados e volumes removidos"
    
    Write-Info "Limpando cache..."
    if (Test-Path ".serverless") {
        Remove-Item -Recurse -Force ".serverless"
    }
    if (Test-Path "volume") {
        Remove-Item -Recurse -Force "volume"
    }
    Write-Success "Cache limpo"
}

# Verificar pré-requisitos
Write-Header "VERIFICANDO PRÉ-REQUISITOS"

Write-Info "Verificando Node.js..."
try {
    $nodeVersion = node --version
    Write-Success "Node.js instalado: $nodeVersion"
} catch {
    Write-Error-Custom "Node.js não encontrado! Instale: https://nodejs.org/"
    exit 1
}

Write-Info "Verificando Python..."
try {
    $pythonVersion = python --version
    Write-Success "Python instalado: $pythonVersion"
} catch {
    Write-Error-Custom "Python não encontrado! Instale: https://www.python.org/"
    exit 1
}

Write-Info "Verificando Docker..."
try {
    $dockerVersion = docker --version
    Write-Success "Docker instalado: $dockerVersion"
} catch {
    Write-Error-Custom "Docker não encontrado! Instale: https://www.docker.com/products/docker-desktop/"
    exit 1
}

Write-Info "Verificando Serverless Framework..."
try {
    $slsVersion = serverless --version
    Write-Success "Serverless Framework instalado"
} catch {
    Write-Error-Custom "Serverless Framework não encontrado!"
    Write-Info "Instalando Serverless Framework globalmente..."
    npm install -g serverless
    Write-Success "Serverless Framework instalado"
}

# Instalar dependências
Write-Header "INSTALANDO DEPENDÊNCIAS"

Write-Info "Instalando dependências Node.js..."
if (-not (Test-Path "package.json")) {
    Write-Error-Custom "package.json não encontrado!"
    exit 1
}
npm install
Write-Success "Dependências Node.js instaladas"

Write-Info "Instalando dependências Python..."
if (-not (Test-Path "requirements.txt")) {
    Write-Error-Custom "requirements.txt não encontrado!"
    exit 1
}
pip install -r requirements.txt
Write-Success "Dependências Python instaladas"

# Iniciar LocalStack
Write-Header "INICIANDO LOCALSTACK"

Write-Info "Subindo container Docker..."
docker-compose up -d

Write-Info "Aguardando LocalStack inicializar (20 segundos)..."
Start-Sleep -Seconds 20

# Verificar saúde do LocalStack
Write-Info "Verificando saúde do LocalStack..."
$maxRetries = 5
$retryCount = 0
$healthy = $false

while (-not $healthy -and $retryCount -lt $maxRetries) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:4566/_localstack/health" -TimeoutSec 5
        if ($response) {
            $healthy = $true
            Write-Success "LocalStack está rodando e saudável!"
            
            Write-Info "Serviços disponíveis:"
            foreach ($service in $response.services.PSObject.Properties) {
                $status = $service.Value
                $icon = if ($status -eq "available" -or $status -eq "running") { "✅" } else { "❌" }
                Write-Host "   $icon $($service.Name): $status"
            }
        }
    } catch {
        $retryCount++
        Write-Info "Tentativa $retryCount/$maxRetries - Aguardando LocalStack..."
        Start-Sleep -Seconds 5
    }
}

if (-not $healthy) {
    Write-Error-Custom "LocalStack não respondeu após $maxRetries tentativas"
    Write-Info "Verificando logs do Docker..."
    docker-compose logs --tail=50
    exit 1
}

# Deploy da aplicação
Write-Header "DEPLOY DA APLICAÇÃO"

Write-Info "Executando deploy no LocalStack..."
try {
    serverless deploy --stage local --verbose
    Write-Success "Deploy concluído com sucesso!"
} catch {
    Write-Error-Custom "Erro durante o deploy"
    Write-Info "Logs do erro:"
    Write-Host $_.Exception.Message
    exit 1
}

# Obter informações da API
Write-Header "INFORMAÇÕES DA API"

Write-Info "Obtendo detalhes da API..."
$apiInfo = serverless info --stage local

Write-Host $apiInfo

# Extrair API ID
$apiId = $null
if ($apiInfo -match "restapis/([a-zA-Z0-9]+)/local") {
    $apiId = $matches[1]
    Write-Success "API ID identificado: $apiId"
}

# Executar testes (se não for pulado)
if (-not $SkipTests) {
    Write-Header "EXECUTANDO TESTES AUTOMATIZADOS"
    
    if ($apiId) {
        Write-Info "Executando script de testes Python com API ID: $apiId"
        python teste_api.py $apiId
    } else {
        Write-Info "Executando script de testes Python (detecção automática)"
        python teste_api.py
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Todos os testes passaram!"
    } else {
        Write-Error-Custom "Alguns testes falharam. Verifique a saída acima."
    }
    
    # Mostrar como ver logs do SNS
    Write-Host ""
    Write-Info "Para ver logs do subscriber SNS, execute:"
    Write-ColorOutput "   serverless logs -f snsSubscriber --stage local --tail" "Cyan"
}

# Resumo final
Write-Header "SETUP COMPLETO!"

Write-Host ""
Write-ColorOutput "🎉 Aplicação configurada e rodando no LocalStack!" "Green"
Write-Host ""
Write-Info "Próximos passos:"
Write-Host "   1. Ver logs do SNS subscriber:"
Write-ColorOutput "      serverless logs -f snsSubscriber --stage local --tail" "Cyan"
Write-Host ""
Write-Host "   2. Testar endpoints manualmente:"
if ($apiId) {
    Write-ColorOutput "      `$API_ID = `"$apiId`"" "Cyan"
} else {
    Write-ColorOutput "      `$API_ID = `"SEU_API_ID_AQUI`"" "Cyan"
}
Write-ColorOutput "      `$BASE_URL = `"http://localhost:4566/restapis/`$API_ID/local/_user_request_`"" "Cyan"
Write-ColorOutput "      curl `"`$BASE_URL/items`"" "Cyan"
Write-Host ""
Write-Host "   3. Ver saúde do LocalStack:"
Write-ColorOutput "      curl http://localhost:4566/_localstack/health" "Cyan"
Write-Host ""
Write-Host "   4. Parar tudo:"
Write-ColorOutput "      docker-compose down" "Cyan"
Write-Host ""

Write-ColorOutput "📚 Consulte README.md e EXEMPLOS.md para mais informações" "Yellow"
Write-Host ""
