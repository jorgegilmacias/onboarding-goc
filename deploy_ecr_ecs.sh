#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./deploy_ecr_ecs.sh <ecr-repo-name> <ecs-cluster-name> <ecs-service-name> [image-tag]
#
# Example:
#   ./deploy_ecr_ecs.sh onboarding-goc onboarding-cluster onboarding-service v1

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <ecr-repo-name> <ecs-cluster-name> <ecs-service-name> [image-tag]"
  exit 1
fi

ECR_REPO_NAME="$1"
ECS_CLUSTER_NAME="$2"
ECS_SERVICE_NAME="$3"
IMAGE_TAG="${4:-$(date +%Y%m%d%H%M%S)}"

AWS_REGION="${AWS_REGION:-us-east-2}"
AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_URI="${ECR_REGISTRY}/${ECR_REPO_NAME}:${IMAGE_TAG}"

echo "AWS Account: ${AWS_ACCOUNT_ID}"
echo "AWS Region: ${AWS_REGION}"
echo "ECR Repo: ${ECR_REPO_NAME}"
echo "ECS Cluster: ${ECS_CLUSTER_NAME}"
echo "ECS Service: ${ECS_SERVICE_NAME}"
echo "Image URI: ${IMAGE_URI}"

if ! aws ecr describe-repositories --repository-names "${ECR_REPO_NAME}" >/dev/null 2>&1; then
  echo "ECR repository ${ECR_REPO_NAME} not found. Creating it..."
  aws ecr create-repository --repository-name "${ECR_REPO_NAME}" >/dev/null
fi

echo "Logging in to ECR..."
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ECR_REGISTRY}"

echo "Building image..."
docker build -t "${ECR_REPO_NAME}:${IMAGE_TAG}" .

echo "Tagging image..."
docker tag "${ECR_REPO_NAME}:${IMAGE_TAG}" "${IMAGE_URI}"

echo "Pushing image to ECR..."
docker push "${IMAGE_URI}"

echo "Forcing ECS new deployment..."
aws ecs update-service \
  --cluster "${ECS_CLUSTER_NAME}" \
  --service "${ECS_SERVICE_NAME}" \
  --force-new-deployment >/dev/null

echo "Deployment triggered successfully."
echo "Image pushed: ${IMAGE_URI}"
