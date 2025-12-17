import json
import os
import uuid
import boto3
from datetime import datetime
from decimal import Decimal

# Configuração do LocalStack
# Detecta se está rodando em ambiente local verificando variáveis de ambiente
def is_local_environment():
    """Detecta se está rodando no LocalStack ou AWS real"""
    indicators = [
        os.environ.get('LOCALSTACK_HOSTNAME'),
        os.environ.get('AWS_SAM_LOCAL') == 'true',
        os.environ.get('IS_OFFLINE') == 'true',
        os.environ.get('AWS_ENDPOINT_URL'),
        # Detecta se o AWS_EXECUTION_ENV não está definido (indica ambiente local)
        not os.environ.get('AWS_EXECUTION_ENV')
    ]
    return any(indicators)

# Configurar endpoint do LocalStack
LOCALSTACK_ENDPOINT = os.environ.get('AWS_ENDPOINT_URL', 'http://localhost:4566')
IS_LOCAL = is_local_environment()

# Configurar clientes AWS com detecção automática de ambiente
if IS_LOCAL:
    print(f"🔧 Executando em AMBIENTE LOCAL - Endpoint: {LOCALSTACK_ENDPOINT}")
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=LOCALSTACK_ENDPOINT,
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
    sns_client = boto3.client(
        'sns',
        endpoint_url=LOCALSTACK_ENDPOINT,
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
else:
    print("☁️ Executando em AMBIENTE AWS REAL")
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sns_client = boto3.client('sns', region_name='us-east-1')

table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])


class DecimalEncoder(json.JSONEncoder):
    """Helper para serializar Decimal do DynamoDB"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def response(status_code, body):
    """Helper para formatar respostas HTTP"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }


def validate_peca_data(data, is_update=False):
    """
    Valida os dados de uma peça automotiva.
    Campos obrigatórios: nome, codigo, preco, quantidade
    """
    required_fields = ['nome', 'codigo', 'preco', 'quantidade']
    
    if not is_update:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f"Campos obrigatórios faltando: {', '.join(missing_fields)}"
    
    # Validar tipos de dados quando presentes
    if 'preco' in data:
        try:
            preco = float(data['preco'])
            if preco < 0:
                return False, "Preço não pode ser negativo"
        except (ValueError, TypeError):
            return False, "Preço deve ser um número válido"
    
    if 'quantidade' in data:
        try:
            quantidade = int(data['quantidade'])
            if quantidade < 0:
                return False, "Quantidade não pode ser negativa"
        except (ValueError, TypeError):
            return False, "Quantidade deve ser um número inteiro"
    
    return True, None


def publish_to_sns(operation, item_data):
    """Publica mensagem no tópico SNS"""
    try:
        topic_arn = os.environ.get('SNS_TOPIC_ARN')
        if not topic_arn:
            print("AVISO: SNS_TOPIC_ARN não configurado")
            return
        
        message = {
            'operation': operation,
            'timestamp': datetime.now().isoformat(),
            'item': item_data
        }
        
        sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message, cls=DecimalEncoder),
            Subject=f'Peça Automotiva - {operation}'
        )
        print(f"Mensagem publicada no SNS: {operation} - Item ID: {item_data.get('id')}")
    except Exception as e:
        print(f"Erro ao publicar no SNS: {str(e)}")
        # Não falhar a operação se o SNS falhar


def create_item(event, context):
    """
    POST /items - Cria uma nova peça automotiva
    """
    try:
        # Parse do body
        if isinstance(event.get('body'), str):
            data = json.loads(event['body'])
        else:
            data = event.get('body', {})
        
        # Validar dados
        is_valid, error_message = validate_peca_data(data)
        if not is_valid:
            return response(400, {'error': error_message})
        
        # Gerar ID único
        item_id = str(uuid.uuid4())
        
        # Preparar item
        timestamp = datetime.now().isoformat()
        item = {
            'id': item_id,
            'nome': data['nome'],
            'codigo': data['codigo'],
            'preco': Decimal(str(data['preco'])),
            'quantidade': int(data['quantidade']),
            'descricao': data.get('descricao', ''),
            'fabricante': data.get('fabricante', ''),
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        # Salvar no DynamoDB
        table.put_item(Item=item)
        
        # Publicar no SNS
        publish_to_sns('CREATE', item)
        
        return response(201, {
            'message': 'Peça criada com sucesso',
            'item': item
        })
    
    except json.JSONDecodeError:
        return response(400, {'error': 'JSON inválido'})
    except Exception as e:
        print(f"Erro ao criar item: {str(e)}")
        return response(500, {'error': f'Erro interno do servidor: {str(e)}'})


def list_items(event, context):
    """
    GET /items - Lista todas as peças automotivas
    """
    try:
        result = table.scan()
        items = result.get('Items', [])
        
        return response(200, {
            'items': items,
            'count': len(items)
        })
    
    except Exception as e:
        print(f"Erro ao listar itens: {str(e)}")
        return response(500, {'error': f'Erro interno do servidor: {str(e)}'})


def get_item(event, context):
    """
    GET /items/{id} - Busca uma peça específica por ID
    """
    try:
        item_id = event['pathParameters']['id']
        
        result = table.get_item(Key={'id': item_id})
        
        if 'Item' not in result:
            return response(404, {'error': 'Peça não encontrada'})
        
        return response(200, {'item': result['Item']})
    
    except Exception as e:
        print(f"Erro ao buscar item: {str(e)}")
        return response(500, {'error': f'Erro interno do servidor: {str(e)}'})


def update_item(event, context):
    """
    PUT /items/{id} - Atualiza uma peça existente
    """
    try:
        item_id = event['pathParameters']['id']
        
        # Verificar se o item existe
        result = table.get_item(Key={'id': item_id})
        if 'Item' not in result:
            return response(404, {'error': 'Peça não encontrada'})
        
        # Parse do body
        if isinstance(event.get('body'), str):
            data = json.loads(event['body'])
        else:
            data = event.get('body', {})
        
        # Validar dados
        is_valid, error_message = validate_peca_data(data, is_update=True)
        if not is_valid:
            return response(400, {'error': error_message})
        
        # Construir expressão de atualização
        update_expression = "SET updated_at = :updated_at"
        expression_values = {':updated_at': datetime.now().isoformat()}
        expression_names = {}
        
        # Adicionar campos a atualizar
        if 'nome' in data:
            update_expression += ", nome = :nome"
            expression_values[':nome'] = data['nome']
        
        if 'codigo' in data:
            update_expression += ", codigo = :codigo"
            expression_values[':codigo'] = data['codigo']
        
        if 'preco' in data:
            update_expression += ", preco = :preco"
            expression_values[':preco'] = Decimal(str(data['preco']))
        
        if 'quantidade' in data:
            update_expression += ", quantidade = :quantidade"
            expression_values[':quantidade'] = int(data['quantidade'])
        
        if 'descricao' in data:
            update_expression += ", descricao = :descricao"
            expression_values[':descricao'] = data['descricao']
        
        if 'fabricante' in data:
            update_expression += ", fabricante = :fabricante"
            expression_values[':fabricante'] = data['fabricante']
        
        # Atualizar no DynamoDB
        response_db = table.update_item(
            Key={'id': item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )
        
        updated_item = response_db['Attributes']
        
        # Publicar no SNS
        publish_to_sns('UPDATE', updated_item)
        
        return response(200, {
            'message': 'Peça atualizada com sucesso',
            'item': updated_item
        })
    
    except json.JSONDecodeError:
        return response(400, {'error': 'JSON inválido'})
    except Exception as e:
        print(f"Erro ao atualizar item: {str(e)}")
        return response(500, {'error': f'Erro interno do servidor: {str(e)}'})


def delete_item(event, context):
    """
    DELETE /items/{id} - Remove uma peça
    """
    try:
        item_id = event['pathParameters']['id']
        
        # Verificar se o item existe antes de deletar
        result = table.get_item(Key={'id': item_id})
        if 'Item' not in result:
            return response(404, {'error': 'Peça não encontrada'})
        
        # Deletar do DynamoDB
        table.delete_item(Key={'id': item_id})
        
        return response(200, {
            'message': 'Peça deletada com sucesso',
            'id': item_id
        })
    
    except Exception as e:
        print(f"Erro ao deletar item: {str(e)}")
        return response(500, {'error': f'Erro interno do servidor: {str(e)}'})


def sns_subscriber(event, context):
    """
    Função que é disparada pelo SNS Topic.
    Apenas loga a mensagem recebida.
    """
    try:
        print("=" * 80)
        print("🔔 NOTIFICAÇÃO SNS RECEBIDA")
        print("=" * 80)
        
        for record in event['Records']:
            sns_message = record['Sns']
            message_body = json.loads(sns_message['Message'])
            
            print(f"\n📋 Assunto: {sns_message.get('Subject', 'N/A')}")
            print(f"📅 Timestamp: {sns_message.get('Timestamp', 'N/A')}")
            print(f"🔧 Operação: {message_body.get('operation', 'N/A')}")
            print(f"⏰ Data/Hora: {message_body.get('timestamp', 'N/A')}")
            print(f"\n📦 Dados da Peça:")
            print(json.dumps(message_body.get('item', {}), indent=2, cls=DecimalEncoder))
            print("=" * 80)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Notificação processada com sucesso'})
        }
    
    except Exception as e:
        print(f"❌ Erro ao processar notificação SNS: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
