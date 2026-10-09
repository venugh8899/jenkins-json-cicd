
pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    environment {
        GITHUB_REPO = 'venugh8899/jenkins-json-cicd'
        TARGET_BRANCH = 'main'
        GIT_CREDENTIAL_ID = 'github-jenugh-cicd'
        API_CREDENTIAL_ID = 'github-api-token-text'
    }

    stages {

        stage('Checkout Incoming') {
            steps {
                checkout scm

                sh '''
                    set -e
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

                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-jenugh-cicd',
                        usernameVariable: 'GIT_USERNAME',
                        passwordVariable: 'GIT_PASSWORD'
                    )
                ]) {
                    sh '''
                        set +x
                        set -e

                        echo "Creating ${FEATURE_BRANCH}"

                        git checkout -b "${FEATURE_BRANCH}"

                        # Use a temporary askpass helper so the token
                        # is not embedded in the remote URL.
                        ASKPASS_FILE=$(mktemp)
                        trap 'rm -f "$ASKPASS_FILE"' EXIT

                        cat > "$ASKPASS_FILE" <<'EOF'
#!/bin/sh
case "$1" in
  *Username*) printf '%s\\n' "$GIT_USERNAME" ;;
  *Password*) printf '%s\\n' "$GIT_PASSWORD" ;;
  *) exit 1 ;;
esac
EOF
                        chmod 700 "$ASKPASS_FILE"

                        GIT_ASKPASS="$ASKPASS_FILE" \
                        GIT_TERMINAL_PROMPT=0 \
                        git push origin "${FEATURE_BRANCH}"

                        echo "Feature branch pushed successfully."
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
                        credentialsId: 'github-api-token-text',
                        variable: 'GITHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        set -e

                        RESPONSE=$(curl -sS \
                          -w "\\n%{http_code}" \
                          -X POST \
                          -H "Accept: application/vnd.github+json" \
                          -H "Authorization: Bearer ${GITHUB_TOKEN}" \
                          -H "X-GitHub-Api-Version: 2022-11-28" \
                          "https://api.github.com/repos/${GITHUB_REPO}/pulls" \
                          -d "{
                            \\"title\\": \\"Automated JSON Configuration Update - Build ${BUILD_NUMBER}\\",
                            \\"body\\": \\"JSON validation completed successfully in Jenkins.\\",
                            \\"head\\": \\"${FEATURE_BRANCH}\\",
                            \\"base\\": \\"${TARGET_BRANCH}\\"
                          }")

                        HTTP_CODE=$(printf '%s\\n' "$RESPONSE" | tail -n 1)
                        BODY=$(printf '%s\\n' "$RESPONSE" | sed '$d')

                        if [ "$HTTP_CODE" != "201" ]; then
                            echo "PR creation failed. HTTP: $HTTP_CODE"
                            printf '%s\\n' "$BODY"
                            exit 1
                        fi

                        printf '%s\\n' "$BODY" > pr-response.json

                        python3 -c '
import json
p = json.load(open("pr-response.json"))
print("PR number:", p["number"])
print("PR URL:", p["html_url"])
print(p["number"], file=open("pr-number.txt", "w"))
'
                    '''
                }

                script {
                    env.PR_NUMBER = readFile('pr-number.txt').trim()
                }
            }
        }

        stage('Verify Pull Request') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'github-api-token-text',
                        variable: 'GITHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        set -e

                        curl -fsS \
                          -H "Accept: application/vnd.github+json" \
                          -H "Authorization: Bearer ${GITHUB_TOKEN}" \
                          -H "X-GitHub-Api-Version: 2022-11-28" \
                          "https://api.github.com/repos/${GITHUB_REPO}/pulls/${PR_NUMBER}" \
                          -o pr-details.json

                        python3 -c '
import json
p = json.load(open("pr-details.json"))

assert p["state"] == "open", "PR is not open"
assert p["base"]["ref"] == "main", "PR does not target main"
assert p["head"]["ref"] == "'"${FEATURE_BRANCH}"'", "Unexpected PR source branch"
assert p["mergeable"] is not False, "PR has merge conflicts"

print("PR state, target, source, and mergeability checks passed.")
'
                    '''
                }
            }
        }

        stage('Automatic Merge Pull Request') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'github-api-token-text',
                        variable: 'GITHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        set -e

                        echo "Merging PR #${PR_NUMBER}"

                        RESPONSE=$(curl -sS \
                          -w "\\n%{http_code}" \
                          -X PUT \
                          -H "Accept: application/vnd.github+json" \
                          -H "Authorization: Bearer ${GITHUB_TOKEN}" \
                          -H "X-GitHub-Api-Version: 2022-11-28" \
                          "https://api.github.com/repos/${GITHUB_REPO}/pulls/${PR_NUMBER}/merge" \
                          -d '{"merge_method":"squash"}')

                        HTTP_CODE=$(printf '%s\\n' "$RESPONSE" | tail -n 1)
                        BODY=$(printf '%s\\n' "$RESPONSE" | sed '$d')

                        if [ "$HTTP_CODE" != "200" ]; then
                            echo "Merge failed. HTTP: $HTTP_CODE"
                            printf '%s\\n' "$BODY"
                            exit 1
                        fi

                        printf '%s\\n' "$BODY" > merge-response.json

                        python3 -c '
import json
m = json.load(open("merge-response.json"))
if not m.get("merged"):
    raise SystemExit("GitHub did not confirm the merge.")
print("Pull request merged successfully.")
print(m.get("message", ""))
'
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'JSON validation, PR creation, and automatic merge completed successfully.'
            echo "Feature branch: ${env.FEATURE_BRANCH}"
            echo "Merged PR: #${env.PR_NUMBER}"
        }

        failure {
            echo 'Pipeline failed. Review Console Output before retrying.'
        }

        always {
            echo 'JSON CI/CD pipeline execution finished.'
        }
    }
}
