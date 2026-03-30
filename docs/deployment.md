# Deployment (Azure Web App)

This repository contains a GitHub Actions workflow that builds the Python app and deploys it to an Azure Web App.

## Workflow

Workflow file: [main_airbnb-apiv1.yml](file:///Users/basakkorkut/Desktop/airbnb-api/.github/workflows/main_airbnb-apiv1.yml)

Triggers:

- On push to `main`
- Manual trigger via `workflow_dispatch`

Steps (high level):

1. Checkout repository
2. Set up Python (configured as 3.13)
3. Create a virtual environment and install dependencies from [requirements.txt](file:///Users/basakkorkut/Desktop/airbnb-api/requirements.txt)
4. Upload the repository as a deployment artifact (excluding the virtualenv folder)
5. Deploy artifact to Azure Web App using `azure/webapps-deploy`

## Secrets

The workflow expects an Azure publish profile stored as a GitHub secret:

- `AZUREAPPSERVICE_PUBLISHPROFILE_FC186463C17347AE8A22E31A4A877E8A`

Do not commit publish profiles or other credentials to the repository.

## Runtime Start Command

The application’s production entrypoint is:

- `app.main:app` ([main.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/main.py))

And the repository provides a Gunicorn start script:

- [startup.sh](file:///Users/basakkorkut/Desktop/airbnb-api/startup.sh)
