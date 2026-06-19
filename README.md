# onboarding-goc

Onboarding portal for new GOC users.

## Branching and environments

- `main` -> production
- `develop` -> development
- Feature branches -> PR into `develop`

## GitHub Actions deployment model

This repo includes two workflows:

- `.github/workflows/deploy-dev.yml`
  - Trigger: push to `develop`
  - Deploys to ECS DEV service
  - Image tag format: `dev-<commit_sha>`

- `.github/workflows/deploy-prod.yml`
  - Trigger: manual (`workflow_dispatch`)
  - Deploys to ECS PROD service
  - Can promote an existing image tag (`image_tag` input), or build a new `prod-<commit_sha>` image

## Required GitHub configuration

### Environments

Create two GitHub Environments:

- `dev`
- `prod` (recommended: require approval)

### Repository secrets

Set these secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Repository variables

Set these variables:

- `AWS_REGION` (example: `us-west-2`)
- `ECR_REPOSITORY` (example: `onboarding-goc`)
- `ECS_CONTAINER_NAME` (example: `onboarding-goc`)
- `ECS_CLUSTER_DEV`
- `ECS_SERVICE_DEV`
- `ECS_TASK_FAMILY_DEV`
- `ECS_CLUSTER_PROD`
- `ECS_SERVICE_PROD`
- `ECS_TASK_FAMILY_PROD`

## Recommended promotion flow

1. Merge feature branches into `develop`.
2. `deploy-dev.yml` deploys to DEV automatically.
3. Validate in DEV.
4. Run `Deploy PROD` workflow manually, ideally promoting the same tested image tag.
# onboarding-goc
onboarding for new users
