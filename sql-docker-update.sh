echo "Building Docker image and tagging"
docker build -t kb-sql-chat .
docker tag kb-sql-chat:latest 638806779113.dkr.ecr.us-east-1.amazonaws.com/kb-sql-chat:latest

echo "Loggin into ECR"
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 638806779113.dkr.ecr.us-east-1.amazonaws.com

echo "Pusing Image into ECR"
docker push 638806779113.dkr.ecr.us-east-1.amazonaws.com/kb-sql-chat:latest

echo "Updating ECR Services"
aws ecs update-service --cluster gen-ai-km-demo --service km-sql-svc --force-new-deployment --region us-east-1
echo "Finishing updating ECR Services"
