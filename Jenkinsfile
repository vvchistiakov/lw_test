pipeline {
    agent any
    environment {
        dockerName = 'vovochko/lw_test'
        dockerCredential = 'dockerhub'
        dockerImage = ''
    }
    parameters {
        string(name: 'AWS_REGION', defaultValue: 'eu-central-1')
        string(name: 'S3_BUCKET', defaultValue: 'lwtest9456')
    }

    stages {
        stage('Build') {
            steps {
                echo 'Building'
                script {
                    dockerImage = docker.build(dockerName + ":$BUILD_NUMBER")
                }
            }
        }
        stage('publish'){
            when {
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                echo 'Publish'
                script {
                    docker.withRegistry('', dockerCredential) {
                        dockerImage.push()
                    }
                }
            }
        }
        stage('Deploy') {
            agent {
                dockerfile {
                    filename 'AWS.Dockerfile'
                    dir "jenkins"
                }
            }
            when {
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            environment{
                AWS_ACCESS_KEY_ID     = credentials('jenkins-aws-secret-key-id')
                AWS_SECRET_ACCESS_KEY = credentials('jenkins-aws-secret-access-key')
                AWS_DEFAULT_REGION    = "${AWS_REGION}"
            }
            steps {
                echo 'Deploy'
                sh(script: './deploy.sh', returnStdout: true)
            }
        }
    }
    post {
        cleanup {
            deleteDir()
            sh "docker rmi $dockerName:$BUILD_NUMBER"
        }
    }
}