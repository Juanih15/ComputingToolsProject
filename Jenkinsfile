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
                echo 'Building Docker image...'
                sh 'docker build -t usf-flask-app:latest ./flask-mongo-pipeline/app'
            }
        }

        stage('Verify') {
            steps {
                echo 'Verifying image was built successfully...'
                sh 'docker image inspect usf-flask-app:latest'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying stack with Docker Compose...'
                sh 'cd flask-mongo-pipeline && docker compose down || true'
                sh 'cd flask-mongo-pipeline && docker compose up -d'
            }
        }
    }

    post {
        success {
            echo 'Pipeline succeeded. Flask app is live at http://localhost:5000'
        }
        failure {
            echo 'Pipeline failed. Review console output for details.'
        }
    }
}