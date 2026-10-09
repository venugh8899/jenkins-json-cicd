
pipeline {
    agent any

    environment {
        GITHUB_REPO = 'venugh8899/jenkins-json-cicd'
        TARGET_BRANCH = 'main'
        GITHUB_CREDENTIAL_ID = 'github-jenugh-cicd'
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
                    env.FEATURE_BRANCH =
                        "feature/auto-${env.BUILD_NUMBER}"
                }

                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-jenugh-cicd',
                        usernameVariable: 'GIT_USERNAME',
                        passwordVariable: 'GIT_PASSWORD'
                    )
                ]) {
                    sh '''
                        set +x

                        echo "Creating feature branch: ${FEATURE_BRANCH}"

                        git checkout -b "${FEATURE_BRANCH}"

                        git push \
                          "https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/${GITHUB_REPO}.git" \
                          "${FEATURE_BRANCH}"
                    '''
                }
            }
        }

        stage('Validate Environment JSON') {
            steps {
                sh '''
                    set -e

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
                    set -e

                    python3 validation/validate_node.py node/dev.json
                    python3 validation/validate_node.py node/stage.json
                    python3 validation/validate_node.py node/uat.json
                    python3 validation/validate_node.py node/prod.json
                '''
            }
        }

        stage('Create Pull Request') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'github-api-token',
                        variable: 'GITHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x

                        RESPONSE=$(curl -sS \
                          -w "\\n%{http_code}" \
                          -X POST \
                          -H "Accept: application/vnd.github+json" \
                          -H "Authorization: Bearer ${GITHUB_TOKEN}" \
                          -H "X-GitHub-Api-Version: 2022-11-28" \
                          "https://api.github.com/repos/${GITHUB_REPO}/pulls" \
                          -d "{
                            \\"title\\": \\"Automated JSON Configuration Update - Build ${BUILD_NUMBER}\\",
                            \\"body\\": \\"JSON configuration validated successfully by Jenkins.\\",
                            \\"head\\": \\"${FEATURE_BRANCH}\\",
                            \\"base\\": \\"${TARGET_BRANCH}\\"
                          }")

                        HTTP_CODE=$(printf '%s\\n' "$RESPONSE" | tail -n 1)
                        BODY=$(printf '%s\\n' "$RESPONSE" | sed '$d')

                        if [ "$HTTP_CODE" = "201" ]; then
                            echo "Pull request created successfully."

                            printf '%s\\n' "$BODY" | python3 -c \
                              'import json,sys; d=json.load(sys.stdin); print("PR number:", d["number"]); print("PR URL:", d["html_url"])'

                        elif [ "$HTTP_CODE" = "422" ]; then
                            echo "GitHub rejected the PR request."
                            echo "A PR may already exist, or the request is invalid."
                            printf '%s\\n' "$BODY"
                            exit 1

                        else
                            echo "Pull request creation failed. HTTP: ${HTTP_CODE}"
                            printf '%s\\n' "$BODY"
                            exit 1
                        fi
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'JSON validation and PR creation completed successfully.'
            echo "Feature branch: ${env.FEATURE_BRANCH}"
        }

        failure {
            echo 'Pipeline failed. Check the Console Output.'
        }
    }
}
