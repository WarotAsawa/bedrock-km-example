ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)

REGION=$(aws ec2 describe-availability-zones --output text --query 'AvailabilityZones[0].[RegionName]')

IMAGE_NAME=km-chat
IMAGE_TAG=latest

echo "Building Docker image and tagging"
docker build -t $IMAGE_NAME:$IMAGE_TAG .
docker tag $IMAGE_NAME:$IMAGE_TAG $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$IMAGE_NAME:$IMAGE_TAG

echo "Loggin into ECR"
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

echo "Pusing Image into ECR"
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$IMAGE_NAME:$IMAGE_TAG

echo "Updating ECR Services"
aws ecs update-service --cluster gen-ai-km-demo --service km-$IMAGE_TAG-chat-svc --force-new-deployment --region $REGION
echo "Finishing updating ECR Services"
