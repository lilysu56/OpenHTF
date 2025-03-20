pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/lilysu56/OpenHTF.git', branch: 'main'
            }
        }
        stage('Run Python') {
            steps {
                bat 'python export_results.py'
            }
        }
    }
}