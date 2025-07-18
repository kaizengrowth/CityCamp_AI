#!/bin/bash

echo "Updating ECS service with load balancer configuration..."

# First, let's check if we have a working target group
echo "Checking target groups..."
/usr/local/bin/aws elbv2 describe-target-groups \
  --names citycamp-ai-tg-ip \
  --region us-east-1 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text > /tmp/tg_arn.txt 2>/dev/null

if [ $? -eq 0 ]; then
    TG_ARN=$(cat /tmp/tg_arn.txt)
    echo "Found target group: $TG_ARN"
    
    # Update the service with load balancer configuration
    /usr/local/bin/aws ecs update-service \
      --cluster citycamp-ai-cluster \
      --service citycamp-ai-backend \
      --load-balancers "targetGroupArn=$TG_ARN,containerName=backend,containerPort=8000" \
      --region us-east-1
    
    echo "Service updated with load balancer configuration!"
else
    echo "Target group not found. Using old target group..."
    /usr/local/bin/aws ecs update-service \
      --cluster citycamp-ai-cluster \
      --service citycamp-ai-backend \
      --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:538569249671:targetgroup/citycamp-ai-tg/d2a2c1bc27389182,containerName=backend,containerPort=8000" \
      --region us-east-1
    
    echo "Service updated with existing target group!"
fi

rm -f /tmp/tg_arn.txt

echo ""
echo "Wait 2-3 minutes for the service to stabilize, then test:"
echo "http://citycamp-ai-alb-520842713.us-east-1.elb.amazonaws.com/health" 