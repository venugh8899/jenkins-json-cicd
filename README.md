# Jenkins JSON CI/CD

This project demonstrates Jenkins CI/CD pipelines for validating
environment and node configuration files stored in JSON format.

## Project Structure

- environment/ - Environment configuration files
- node/ - Node configuration files
- validation/ - Python validation scripts
- Jenkinsfile-environment - Environment validation pipeline
- Jenkinsfile-node - Node validation pipeline
- requirements.txt - Python dependencies

## Environments

- DEV
- STAGE
- UAT
- PROD

## Technologies

- GitHub
- Jenkins
- Python
- JSON
- Groovy

## Pipeline Flow

GitHub
↓
Jenkins
↓
Checkout
↓
Read JSON Configuration
↓
Python Validation
↓
Success / Failure
