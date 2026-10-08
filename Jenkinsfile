pipeline {

    agent any

    environment {
        TARGET_BRANCH = "main"
    }

    stages {

        stage('Checkout Incoming') {
            steps {
                checkout scm

                sh '''
                    git fetch origin main
                    git fetch origin incoming
                '''
            }
        }

        stage('Create Feature Branch') {
            steps {
                script {
                    env.FEATURE_BRANCH = "feature/auto-${env.BUILD_NUMBER}"
                }

                sh '''
                    echo "Creating feature branch: ${FEATURE_BRANCH}"

                    git checkout -b ${FEATURE_BRANCH}

                    git push origin ${FEATURE_BRANCH}
                '''
            }
        }

        stage('Validate Environment JSON') {
            steps {
                sh '''
                    python3 validation/validate_environment.py environment/dev.json
                    python3 validation/validate_environment.py environment/stage.json
                    python3 validation/validate_environment.py environment/uat.json
                    python3 validation/validate_environment.py environment/prod.json
                '''
            }
        }

        stage('Validate Node JSON') {
            steps {
                sh '''
                    python3 validation/validate_node.py node/dev.json
                    python3 validation/validate_node.py node/stage.json
                    python3 validation/validate_node.py node/uat.json
                    python3 validation/validate_node.py node/prod.json
                '''
            }
        }
    }

    post {

        success {
            echo "JSON validation completed successfully."
            echo "Feature branch: ${env.FEATURE_BRANCH}"
        }

        failure {
            echo "JSON validation failed."
        }
    }
}