# Runbook

## Deployment
- **Frontend:** Automatically deploys to Vercel on every push to `main`.
- **Backend:** Automatically deploys to Render on every push to `main`.

## Fallback
If Render is down, deploy the backend to a different host using the `Dockerfile`.

## Rollback
- **Vercel:** Go to the Deployments tab and promote a previous good deployment.
- **Render:** Go to the Events tab and click "Rollback".