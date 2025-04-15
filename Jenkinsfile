pipeline {
    agent any
    environment {
        DOCKER_IMAGE = "arnoldandrade/rag_fastapi:latest"
        CONTAINER_NAME = "rag_fastapi"
        HOST_PORT = "8000"
        CONTAINER_PORT = "8000"
    }
    stages {
        stage('Deploy') {
            steps {
                script {
                    // Pull the latest image from Docker Hub
                    sh "docker pull ${DOCKER_IMAGE}"
                    // Stop and remove any running container with the same name
                    sh "docker rm -f ${CONTAINER_NAME} || true"
                    // Run the new container
                    sh "docker run -d --name ${CONTAINER_NAME} -p ${HOST_PORT}:${CONTAINER_PORT} ${DOCKER_IMAGE}"
                }
            }
        }
    }
}