#!/bin/bash

echo "🔍 DIAGNÓSTICO ECS - Desafio Lacrei"
echo "=================================="

CLUSTER="desafio-lacrei-production"
SERVICE="desafio-lacrei-production-service"

# 1. Status do serviço
echo "📊 1. STATUS DO SERVIÇO"
echo "----------------------"
aws ecs describe-services \
    --cluster $CLUSTER \
    --services $SERVICE \
    --query 'services[0].{TaskDefinition:taskDefinition,RunningCount:runningCount,DesiredCount:desiredCount,Status:status}' \
    --output table

# 2. Últimas tasks
echo -e "\n📋 2. ÚLTIMAS TASKS"
echo "-------------------"
TASKS=$(aws ecs list-tasks --cluster $CLUSTER --service-name $SERVICE --query 'taskArns[0]' --output text)

if [[ "$TASKS" != "None" && "$TASKS" != "" ]]; then
    echo "Task ID: $TASKS"
    
    # Status da task
    aws ecs describe-tasks \
        --cluster $CLUSTER \
        --tasks $TASKS \
        --query 'tasks[0].{LastStatus:lastStatus,DesiredStatus:desiredStatus,HealthStatus:healthStatus,CreatedAt:createdAt}' \
        --output table
    
    # Logs da task (últimas 50 linhas)
    echo -e "\n📝 3. LOGS DA TASK (últimas 50 linhas)"
    echo "-------------------------------------"
    TASK_ID=$(echo $TASKS | cut -d'/' -f3)
    aws logs filter-log-events \
        --log-group-name "/aws/ecs/desafio-lacrei-production" \
        --filter-pattern "$TASK_ID" \
        --query 'events[-50:].message' \
        --output text
else
    echo "❌ Nenhuma task encontrada"
fi

# 4. Problemas comuns
echo -e "\n⚠️  4. DIAGNÓSTICO DE PROBLEMAS"
echo "------------------------------"

# Verificar task definition atual
echo "🔍 Task Definition atual:"
CURRENT_TD=$(aws ecs describe-services --cluster $CLUSTER --services $SERVICE --query 'services[0].taskDefinition' --output text)
echo "  $CURRENT_TD"

# Verificar últimos eventos
echo -e "\n🔍 Últimos eventos do serviço:"
aws ecs describe-services \
    --cluster $CLUSTER \
    --services $SERVICE \
    --query 'services[0].events[:5].message' \
    --output text

# 5. Health check
echo -e "\n🏥 5. HEALTH CHECK"
echo "------------------"
echo "Testando endpoints..."

# Obter IP público da task
if [[ "$TASKS" != "None" && "$TASKS" != "" ]]; then
    TASK_IP=$(aws ecs describe-tasks \
        --cluster $CLUSTER \
        --tasks $TASKS \
        --query 'tasks[0].attachments[0].details[?name==`privateIPv4Address`].value' \
        --output text)
    
    echo "IP da Task: $TASK_IP"
    
    # Test health endpoint (se task estiver rodando)
    if [[ "$TASK_IP" != "" ]]; then
        echo "Testando /health/..."
        timeout 10 curl -s "http://$TASK_IP:8000/health/" || echo "❌ Health check falhou"
        
        echo "Testando /ready/..."
        timeout 10 curl -s "http://$TASK_IP:8000/ready/" || echo "❌ Ready check falhou"
    fi
fi

echo -e "\n✅ Diagnóstico concluído!"
echo -e "\n🔧 PRÓXIMOS PASSOS:"
echo "- Se timeout: Aumentar timeout do Gunicorn"
echo "- Se memory: Aumentar memoria da task definition"
echo "- Se DB: Verificar conectividade PostgreSQL"
echo "- Se health: Verificar endpoints /health/ e /ready/"
