pipeline {
    agent any
    parameters {
        string(name: 'IMAGE_TAG', defaultValue: '', description: 'Docker image tag to pull and run (leave empty to use this build own tag)')
    }
    environment {
        IMAGE_NAME = "nginx-demo"
        DOCKERHUB_USERNAME = "mubashraiftikhar10"
    }
    stages {
        stage('Checkout') {
            steps {
                script {
                    try {
                        git branch: 'main',
                            url: 'https://github.com/MubashraIftikhar/jenkins.git',
                            credentialsId: 'github-creds'
                        env.STAGE_CHECKOUT = "PASSED"
                    } catch (e) {
                        env.STAGE_CHECKOUT = "FAILED"
                        throw e
                    }
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    try {
                        sh 'docker build -t ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${BUILD_NUMBER} .'
                        env.STAGE_BUILD = "PASSED"
                    } catch (e) {
                        env.STAGE_BUILD = "FAILED"
                        throw e
                    }
                }
            }
        }
        stage('Push to Docker Hub') {
            steps {
                script {
                    try {
                        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                            sh '''
                                echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                                docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${BUILD_NUMBER}
                            '''
                        }
                        env.STAGE_PUSH = "PASSED"
                    } catch (e) {
                        env.STAGE_PUSH = "FAILED"
                        throw e
                    }
                }
            }
        }
        stage('Determine Tag to Pull') {
            steps {
                script {
                    try {
                        env.TAG_TO_USE = params.IMAGE_TAG?.trim() ? params.IMAGE_TAG.trim() : env.BUILD_NUMBER
                        echo "Will pull and run tag: ${env.TAG_TO_USE}"
                        env.STAGE_DETERMINE = "PASSED"
                    } catch (e) {
                        env.STAGE_DETERMINE = "FAILED"
                        throw e
                    }
                }
            }
        }
        stage('Remove Local Image') {
            steps {
                script {
                    try {
                        sh 'docker rmi ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG_TO_USE} || true'
                        env.STAGE_REMOVE = "PASSED"
                    } catch (e) {
                        env.STAGE_REMOVE = "FAILED"
                        throw e
                    }
                }
            }
        }
        stage('Pull from Docker Hub') {
            steps {
                script {
                    try {
                        sh 'docker pull ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG_TO_USE}'
                        env.STAGE_PULL = "PASSED"
                    } catch (e) {
                        env.STAGE_PULL = "FAILED"
                        throw e
                    }
                }
            }
        }
        stage('Run Container') {
            steps {
                script {
                    try {
                        sh '''
                            docker rm -f nginx-demo-run || true
                            docker run -d -p 8082:80 --name nginx-demo-run ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG_TO_USE}
                        '''
                        env.STAGE_RUN = "PASSED"
                    } catch (e) {
                        env.STAGE_RUN = "FAILED"
                        throw e
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                def result = currentBuild.currentResult
                def color = (result == 'SUCCESS') ? 'good' : 'danger'

                def statusEmoji = { s -> s == "PASSED" ? "PASSED" : (s == "FAILED" ? "FAILED" : "SKIPPED") }

                def table = "Checkout: " + statusEmoji(env.STAGE_CHECKOUT) + "\n" +
                            "Build Docker Image: " + statusEmoji(env.STAGE_BUILD) + "\n" +
                            "Push to Docker Hub: " + statusEmoji(env.STAGE_PUSH) + "\n" +
                            "Determine Tag to Pull: " + statusEmoji(env.STAGE_DETERMINE) + "\n" +
                            "Remove Local Image: " + statusEmoji(env.STAGE_REMOVE) + "\n" +
                            "Pull from Docker Hub: " + statusEmoji(env.STAGE_PULL) + "\n" +
                            "Run Container: " + statusEmoji(env.STAGE_RUN)

                slackSend(
                    channel: '#social',
                    color: color,
                    message: "Jenkins Build #${env.BUILD_NUMBER} - ${result}\nJob: nginx-demo-pipeline\nTag running: ${env.TAG_TO_USE ?: 'N/A'}\n\n" + table + "\n\nView Console: ${env.BUILD_URL}console"
                )
            }
        }
    }
}
