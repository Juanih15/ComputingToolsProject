pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checked out from GitHub.'
            }
        }

        stage('Build') {
            steps {
                echo 'Building Docker images...'
                sh 'cd flask-mongo-pipeline && docker compose build --no-cache'
            }
        }

        stage('Verify') {
            steps {
                echo 'Verifying Docker images were built...'
                sh 'docker images | grep -E "flask-mongo-pipeline|mongo"'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying stack with Docker Compose...'
                sh 'cd flask-mongo-pipeline && docker compose down -v || true'
                sh 'cd flask-mongo-pipeline && docker compose up -d'
                echo 'Waiting for services to become healthy...'
                sh 'sleep 10'
            }
        }

        stage('Test') {
            steps {
                echo 'Running smoke tests against live endpoints...'

                sh '''
                    echo "--- Test 1: Health check ---"
                    curl -sf http://localhost:5000/health | grep -q '"status":"ok"' \
                        && echo "PASS: /health returned ok" \
                        || (echo "FAIL: /health did not return ok" && exit 1)
                '''

                sh '''
                    echo "--- Test 2: Home page ---"
                    curl -sf http://localhost:5000/ | grep -q '"app"' \
                        && echo "PASS: / returned app info" \
                        || (echo "FAIL: / did not respond" && exit 1)
                '''

                sh '''
                    echo "--- Test 3: Create a task ---"
                    RESPONSE=$(curl -sf -X POST http://localhost:5000/tasks \
                        -H "Content-Type: application/json" \
                        -d '{"title":"Jenkins test task","description":"Created by CI pipeline"}')
                    echo "$RESPONSE"
                    echo "$RESPONSE" | grep -q '"title":"Jenkins test task"' \
                        && echo "PASS: POST /tasks created a task" \
                        || (echo "FAIL: POST /tasks failed" && exit 1)
                '''

                sh '''
                    echo "--- Test 4: List tasks ---"
                    curl -sf http://localhost:5000/tasks | grep -q 'Jenkins test task' \
                        && echo "PASS: GET /tasks lists the created task" \
                        || (echo "FAIL: GET /tasks did not return tasks" && exit 1)
                '''

                echo 'All smoke tests passed.'
            }
        }
    }

    post {
        success {
            echo 'Pipeline succeeded. Flask + MongoDB app is live at http://localhost:5000'
        }
        failure {
            echo 'Pipeline failed. Tearing down containers...'
            sh 'cd flask-mongo-pipeline && docker compose down -v || true'
        }
        always {
            echo 'Pipeline finished.'
        }
    }
}
