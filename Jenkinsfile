pipeline {
    agent any
    environment {
        DOCKER_IMAGE = "arnold-andrade/rag_fastapi:latest"
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}")
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    sh 'docker rm -f rag_fastapi || true'
                    sh 'docker run -d --name rag_fastapi -p 8000:8000 arnold-andrade/rag_fastapi:latest'
                }
            }
        }
    }
}