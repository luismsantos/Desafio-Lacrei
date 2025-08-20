#!/bin/bash

echo "🔍 DIAGNÓSTICO POSTGRESQL RDS - Execute no AWS CloudShell ou onde tem AWS CLI"
echo "==========================================================================="

echo ""
echo "1️⃣ VERIFICAR INSTÂNCIA RDS"
echo "aws rds describe-db-instances --db-instance-identifier lacrei-dev-db --region sa-east-1 --query 'DBInstances[0].{Status:DBInstanceStatus,Endpoint:Endpoint.Address,Port:Endpoint.Port,VPC:DBSubnetGroup.VpcId}' --output table"

echo ""
echo "2️⃣ VERIFICAR SECURITY GROUPS DO RDS"
echo "RDS_SG=\$(aws rds describe-db-instances --db-instance-identifier lacrei-dev-db --region sa-east-1 --query 'DBInstances[0].VpcSecurityGroups[0].VpcSecurityGroupId' --output text)"
echo "echo \"RDS Security Group: \$RDS_SG\""
echo "aws ec2 describe-security-groups --group-ids \$RDS_SG --region sa-east-1 --query 'SecurityGroups[0].IpPermissions[?FromPort==\`5432\`]' --output table"

echo ""
echo "3️⃣ VERIFICAR ECS SERVICE"
echo "aws ecs describe-services --cluster lacrei-dev --services lacrei-dev-service --region sa-east-1 --query 'services[0].networkConfiguration.awsvpcConfiguration.{Subnets:subnets,SecurityGroups:securityGroups,PublicIP:assignPublicIp}' --output table"

echo ""
echo "4️⃣ OBTER SECURITY GROUP DO ECS"
echo "ECS_SG=\$(aws ecs describe-services --cluster lacrei-dev --services lacrei-dev-service --region sa-east-1 --query 'services[0].networkConfiguration.awsvpcConfiguration.securityGroups[0]' --output text)"
echo "echo \"ECS Security Group: \$ECS_SG\""

echo ""
echo "5️⃣ VERIFICAR SE ESTÃO NA MESMA VPC"
echo "RDS_VPC=\$(aws rds describe-db-instances --db-instance-identifier lacrei-dev-db --region sa-east-1 --query 'DBInstances[0].DBSubnetGroup.VpcId' --output text)"
echo "ECS_SUBNET=\$(aws ecs describe-services --cluster lacrei-dev --services lacrei-dev-service --region sa-east-1 --query 'services[0].networkConfiguration.awsvpcConfiguration.subnets[0]' --output text)"
echo "ECS_VPC=\$(aws ec2 describe-subnets --subnet-ids \$ECS_SUBNET --region sa-east-1 --query 'Subnets[0].VpcId' --output text)"
echo ""
echo "echo \"RDS VPC: \$RDS_VPC\""
echo "echo \"ECS VPC: \$ECS_VPC\""
echo ""
echo "if [ \"\$RDS_VPC\" = \"\$ECS_VPC\" ]; then"
echo "    echo \"✅ MESMA VPC - OK\""
echo "else"
echo "    echo \"❌ VPCs DIFERENTES - PROBLEMA!\""
echo "fi"

echo ""
echo "6️⃣ CORRIGIR CONECTIVIDADE"
echo "echo \"🔧 Para permitir acesso do ECS ao RDS na porta 5432:\""
echo "echo \"aws ec2 authorize-security-group-ingress --group-id \$RDS_SG --protocol tcp --port 5432 --source-group \$ECS_SG --region sa-east-1\""

echo ""
echo "7️⃣ TESTAR CONECTIVIDADE (OPCIONAL - do container ECS)"
echo "echo \"Para testar conectividade de dentro do container:\""
echo "echo \"telnet lacrei-dev-db.c7ako26eotke.sa-east-1.rds.amazonaws.com 5432\""

echo ""
echo "8️⃣ VERIFICAR LOGS DO ECS"
echo "TASK_ARN=\$(aws ecs list-tasks --cluster lacrei-dev --service lacrei-dev-service --region sa-east-1 --query 'taskArns[0]' --output text)"
echo "echo \"Task ARN: \$TASK_ARN\""
echo "aws logs get-log-events --log-group-name /ecs/lacrei-dev --log-stream-name ecs/web/\$(echo \$TASK_ARN | cut -d'/' -f3) --region sa-east-1 --query 'events[*].message' --output text"
