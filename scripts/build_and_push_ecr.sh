#!/usr/bin/env bash
set -euo pipefail

REGION="eu-north-1"
ACCOUNT_ID="901762117746"
REPO_NAME="uplift-tlearner"
TAG="latest"

ECR_HOST="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
ECR_URI="${ECR_HOST}/${REPO_NAME}:${TAG}"

echo "==> ECR URI: ${ECR_URI}"

echo "==> Login to ECR..."
aws ecr get-login-password --region "${REGION}" | \
  docker login --username AWS --password-stdin "${ECR_HOST}"

echo "==> Build image (linux/amd64)..."
docker buildx build --platform linux/amd64 -t "${REPO_NAME}:${TAG}" .

echo "==> Tag image..."
docker tag "${REPO_NAME}:${TAG}" "${ECR_URI}"

echo "==> Push image..."
docker push "${ECR_URI}"

echo "✅ Done. Pushed: ${ECR_URI}"
