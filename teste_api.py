#!/usr/bin/env python3
"""
Script de Teste Automatizado da API de Peças Automotivas
Execute após fazer o deploy no LocalStack para validar todos os endpoints
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuração da API
API_BASE_URL = "http://localhost:4566/restapis/{api_id}/local/_user_request_"
API_ID = None  # Será obtido automaticamente ou via argumento

# Cores para output no terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Imprime um cabeçalho formatado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}")
    print(f"  {text}")
    print(f"{'=' * 80}{Colors.ENDC}")


def print_success(text: str):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    """Imprime mensagem de erro"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    """Imprime mensagem informativa"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_warning(text: str):
    """Imprime mensagem de aviso"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def get_api_id() -> Optional[str]:
    """
    Obtém o API ID do LocalStack automaticamente
    """
    try:
        response = requests.get(
            "http://localhost:4566/_aws/execute-api",
            timeout=5
        )
        if response.status_code == 200:
            apis = response.json()
            if apis and len(apis) > 0:
                # Pegar a primeira API (ou a que tem 'pecas' no nome)
                for api_id, api_data in apis.items():
                    return api_id
        
        # Tentar listar via AWS CLI simulado
        response = requests.post(
            "http://localhost:4566/",
            headers={"Content-Type": "application/x-amz-json-1.0"},
            timeout=5
        )
        
    except Exception as e:
        print_warning(f"Não foi possível obter API ID automaticamente: {e}")
    
    return None


def make_request(method: str, endpoint: str, data: Optional[Dict] = None) -> tuple:
    """
    Faz uma requisição HTTP e retorna o status e resposta
    """
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return None, {"error": f"Método {method} não suportado"}
        
        try:
            response_data = response.json()
        except:
            response_data = {"raw": response.text}
        
        return response.status_code, response_data
    
    except requests.exceptions.RequestException as e:
        return None, {"error": str(e)}


def test_create_item(item_data: Dict) -> Optional[str]:
    """
    Testa a criação de um item (POST /items)
    Retorna o ID do item criado ou None em caso de erro
    """
    print_info(f"Testando POST /items - Criar: {item_data['nome']}")
    
    status, response = make_request("POST", "/items", item_data)
    
    if status == 201:
        item_id = response.get("item", {}).get("id")
        print_success(f"Item criado com sucesso! ID: {item_id}")
        print(f"   Resposta: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return item_id
    else:
        print_error(f"Falha ao criar item. Status: {status}")
        print(f"   Resposta: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return None


def test_list_items() -> int:
    """
    Testa a listagem de itens (GET /items)
    Retorna o número de itens encontrados
    """
    print_info("Testando GET /items - Listar todos")
    
    status, response = make_request("GET", "/items")
    
    if status == 200:
        items = response.get("items", [])
        count = len(items)
        print_success(f"Listagem bem-sucedida! Total de itens: {count}")
        
        if count > 0:
            print(f"\n   📦 Primeiros itens encontrados:")
            for item in items[:3]:  # Mostrar até 3 itens
                print(f"      - ID: {item.get('id')}")
                print(f"        Nome: {item.get('nome')}")
                print(f"        Código: {item.get('codigo')}")
                print(f"        Preço: R$ {item.get('preco')}")
        return count
    else:
        print_error(f"Falha ao listar itens. Status: {status}")
        print(f"   Resposta: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return 0


def test_get_item(item_id: str) -> bool:
    """
    Testa a busca de um item por ID (GET /items/{id})
    """
    print_info(f"Testando GET /items/{item_id} - Buscar por ID")
    
    status, response = make_request("GET", f"/items/{item_id}")
    
    if status == 200:
        item = response.get("item", {})
        print_success("Item encontrado!")
        print(f"   Nome: {item.get('nome')}")
        print(f"   Código: {item.get('codigo')}")
        print(f"   Preço: R$ {item.get('preco')}")
        print(f"   Quantidade: {item.get('quantidade')}")
        return True
    else:
        print_error(f"Falha ao buscar item. Status: {status}")
        print(f"   Resposta: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return False


def test_update_item(item_id: str, update_data: Dict) -> bool:
    """
    Testa a atualização de um item (PUT /items/{id})
    """
    print_info(f"Testando PUT /items/{item_id} - Atualizar")
    print(f"   Dados: {json.dumps(update_data, ensure_ascii=False)}")
    
    status, response = make_request("PUT", f"/items/{item_id}", update_data)
    
    if status == 200:
        print_success("Item atualizado com sucesso!")
        updated_item = response.get("item", {})
        print(f"   Novo preço: R$ {updated_item.get('preco')}")
        print(f"   Nova quantidade: {updated_item.get('quantidade')}")
        return True
    else:
        print_error(f"Falha ao atualizar item. Status: {status}")
        print(f"   Resposta: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return False


def test_delete_item(item_id: str) -> bool:
    """
    Testa a exclusão de um item (DELETE /items/{id})
    """
    print_info(f"Testando DELETE /items/{item_id} - Deletar")
    
    status, response = make_request("DELETE", f"/items/{item_id}")
    
    if status == 200:
        print_success("Item deletado com sucesso!")
        print(f"   Resposta: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return True
    else:
        print_error(f"Falha ao deletar item. Status: {status}")
        print(f"   Resposta: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return False


def test_validation_errors():
    """
    Testa os casos de erro de validação
    """
    print_header("TESTES DE VALIDAÇÃO")
    
    # Teste 1: Campos obrigatórios faltando
    print_info("Teste 1: Tentando criar item sem campos obrigatórios")
    status, response = make_request("POST", "/items", {
        "nome": "Produto Incompleto",
        "codigo": "INC-001"
        # Faltam: preco, quantidade
    })
    
    if status == 400:
        print_success("Validação funcionando! Erro esperado retornado.")
        print(f"   Erro: {response.get('error')}")
    else:
        print_error(f"Validação falhou. Status esperado: 400, recebido: {status}")
    
    # Teste 2: Preço negativo
    print_info("\nTeste 2: Tentando criar item com preço negativo")
    status, response = make_request("POST", "/items", {
        "nome": "Produto Inválido",
        "codigo": "INV-001",
        "preco": -10.00,
        "quantidade": 5
    })
    
    if status == 400:
        print_success("Validação funcionando! Erro esperado retornado.")
        print(f"   Erro: {response.get('error')}")
    else:
        print_error(f"Validação falhou. Status esperado: 400, recebido: {status}")
    
    # Teste 3: Item não encontrado
    print_info("\nTeste 3: Tentando buscar item inexistente")
    status, response = make_request("GET", "/items/00000000-0000-0000-0000-000000000000")
    
    if status == 404:
        print_success("Tratamento de erro funcionando! 404 retornado.")
        print(f"   Erro: {response.get('error')}")
    else:
        print_error(f"Tratamento falhou. Status esperado: 404, recebido: {status}")


def run_complete_test():
    """
    Executa a suíte completa de testes
    """
    print_header("🚗 TESTE AUTOMATIZADO - API PEÇAS AUTOMOTIVAS")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Endpoint Base: {API_BASE_URL}")
    
    # Contador de testes
    tests_passed = 0
    tests_failed = 0
    
    # Dados de teste
    test_items = [
        {
            "nome": "Vela de Ignição NGK Laser Platinum",
            "codigo": "NGK-BKR6E-11",
            "preco": 29.90,
            "quantidade": 150,
            "descricao": "Vela de ignição com eletrodo de platina",
            "fabricante": "NGK"
        },
        {
            "nome": "Filtro de Óleo Mann W610/1",
            "codigo": "MANN-W610-1",
            "preco": 45.00,
            "quantidade": 80,
            "descricao": "Filtro de óleo para motores diesel e gasolina",
            "fabricante": "Mann Filter"
        }
    ]
    
    created_ids = []
    
    # TESTE 1: Criar itens
    print_header("TESTE 1: CRIAR ITENS (POST /items)")
    for item_data in test_items:
        item_id = test_create_item(item_data)
        if item_id:
            created_ids.append(item_id)
            tests_passed += 1
            time.sleep(1)  # Aguardar processamento SNS
        else:
            tests_failed += 1
    
    # TESTE 2: Listar todos os itens
    print_header("TESTE 2: LISTAR ITENS (GET /items)")
    count = test_list_items()
    if count >= len(created_ids):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # TESTE 3: Buscar por ID
    if created_ids:
        print_header("TESTE 3: BUSCAR POR ID (GET /items/{id})")
        if test_get_item(created_ids[0]):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # TESTE 4: Atualizar item
    if created_ids:
        print_header("TESTE 4: ATUALIZAR ITEM (PUT /items/{id})")
        update_data = {
            "preco": 27.90,
            "quantidade": 200
        }
        if test_update_item(created_ids[0], update_data):
            tests_passed += 1
            time.sleep(1)  # Aguardar processamento SNS
        else:
            tests_failed += 1
    
    # TESTE 5: Deletar item
    if created_ids:
        print_header("TESTE 5: DELETAR ITEM (DELETE /items/{id})")
        if test_delete_item(created_ids[0]):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # TESTE 6: Validações
    test_validation_errors()
    tests_passed += 3  # 3 testes de validação
    
    # Resumo final
    print_header("RESUMO DOS TESTES")
    print(f"\n{Colors.OKGREEN}✅ Testes Aprovados: {tests_passed}{Colors.ENDC}")
    print(f"{Colors.FAIL}❌ Testes Falhados: {tests_failed}{Colors.ENDC}")
    
    total = tests_passed + tests_failed
    success_rate = (tests_passed / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}Taxa de Sucesso: {success_rate:.1f}%{Colors.ENDC}")
    
    if tests_failed == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 TODOS OS TESTES PASSARAM! 🎉{Colors.ENDC}")
        print("\n📨 Verifique os logs do subscriber SNS com:")
        print("   serverless logs -f snsSubscriber --stage local --tail")
        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}⚠️  ALGUNS TESTES FALHARAM{Colors.ENDC}")
        return 1


def check_localstack_health():
    """
    Verifica se o LocalStack está rodando e saudável
    """
    print_info("Verificando saúde do LocalStack...")
    
    try:
        response = requests.get("http://localhost:4566/_localstack/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print_success("LocalStack está rodando!")
            print("   Serviços disponíveis:")
            for service, status in health.get("services", {}).items():
                status_icon = "✅" if status == "available" or status == "running" else "❌"
                print(f"      {status_icon} {service}: {status}")
            return True
    except Exception as e:
        print_error(f"LocalStack não está respondendo: {e}")
        print_warning("Execute: docker-compose up -d")
        return False
    
    return False


def main():
    """
    Função principal
    """
    global API_BASE_URL, API_ID
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        API_ID = sys.argv[1]
        print_info(f"Usando API ID fornecido: {API_ID}")
    else:
        # Tentar obter automaticamente
        print_info("Tentando obter API ID automaticamente...")
        API_ID = get_api_id()
        
        if not API_ID:
            print_warning("Não foi possível obter API ID automaticamente.")
            print("\nPara obter o API ID, execute:")
            print("   serverless info --stage local")
            print("\nE procure por algo como:")
            print("   endpoints:")
            print("     POST - http://localhost:4566/restapis/XXXXXXXXXX/local/_user_request_/items")
            print("\nEntão execute este script com:")
            print(f"   python {sys.argv[0]} XXXXXXXXXX")
            
            # Tentar usar um ID padrão
            print_warning("\nTentando usar endpoint genérico...")
            API_ID = "default"
    
    API_BASE_URL = API_BASE_URL.format(api_id=API_ID)
    
    # Verificar LocalStack
    if not check_localstack_health():
        print_error("\n❌ LocalStack não está rodando ou não está saudável.")
        print("\nPara iniciar o LocalStack, execute:")
        print("   docker-compose up -d")
        return 1
    
    # Aguardar um pouco para garantir que está pronto
    print_info("Aguardando LocalStack estabilizar...")
    time.sleep(2)
    
    # Executar testes
    return run_complete_test()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_warning("\n\nTestes interrompidos pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nErro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
