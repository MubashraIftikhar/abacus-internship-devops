# 🔧 Jenkins

## 📌 What is Jenkins?

Jenkins is an open-source **automation server** used to build, test, and deploy software continuously — forming the backbone of CI/CD (Continuous Integration / Continuous Deployment) pipelines. It automates repetitive tasks like pulling code, building Docker images, running tests, and pushing artifacts, triggered automatically whenever code changes (e.g., via a GitHub push).

## 🏗️ Components

| Component | Description |
|---|---|
| **Controller (Master)** | The core Jenkins server — schedules jobs, manages configuration, dispatches work to agents |
| **Agent (Node)** | A machine (or container) that actually executes the build/pipeline steps |
| **Executor** | A slot on an agent where a single build runs at a time |
| **Job/Project** | A defined task Jenkins runs (Freestyle project or Pipeline) |
| **Plugin** | Extends Jenkins functionality (Git, Docker, Slack notifications, etc.) |
| **Jenkinsfile** | A text file (checked into source control) defining the pipeline as code |

## 📜 Declarative vs Scripted Pipeline

| Declarative Pipeline | Scripted Pipeline |
|---|---|
| Structured, simplified syntax (`pipeline { ... }`) | Written in Groovy, more flexible/imperative |
| Easier to read and maintain | Gives full programmatic control (loops, conditionals) |
| Recommended for most use cases | Used for complex/custom logic |

**Declarative example:**
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
    }
}
```

**Scripted example:**
```groovy
node {
    stage('Build') {
        echo 'Building...'
    }
}
```
## 🆚 Freestyle vs Pipeline Jobs

| Freestyle Project | Pipeline Job |
|---|---|
| Configured entirely through the Jenkins UI (point & click) | Defined as code (Jenkinsfile), version-controlled with the repo |
| No native support for complex logic (stages, conditionals, loops) | Supports complex, multi-stage workflows with full logic control |
| Harder to reuse across projects | Easily reusable (via Shared Libraries) across multiple projects |
| Good for simple, one-off tasks | Recommended for real CI/CD pipelines |
| Changes not tracked in version history | Changes tracked in Git (auditable, reviewable via PRs) |
| Limited plugin-based extensibility | More flexible — can script custom logic beyond plugins |


## 🎛️ Parametrized Pipeline

Allows users to pass custom input values (strings, booleans, choices) when triggering a build manually — useful for things like choosing environment, branch, or version tag.

```groovy
pipeline {
    agent any
    parameters {
        string(name: 'BRANCH', defaultValue: 'main', description: 'Branch to build')
        choice(name: 'ENV', choices: ['dev', 'staging', 'prod'], description: 'Target environment')
    }
    stages {
        stage('Build') {
            steps {
                echo "Building branch: ${params.BRANCH} for ${params.ENV}"
            }
        }
    }
}
```
## 🎛️ Parameter Types

| Parameter Type | Description | Example |
|---|---|---|
| **string** | Accepts free-form text input from the user | `string(name: 'VERSION_TAG', defaultValue: 'v1.0')` |
| **choice** | Presents a dropdown list of predefined options | `choice(name: 'ENV', choices: ['dev', 'staging', 'prod'])` |
| **booleanParam** | A simple true/false checkbox | `booleanParam(name: 'RUN_TESTS', defaultValue: true)` |

## 🔐 Secrets & Security

Jenkins never stores sensitive data (passwords, tokens, API keys) in plain text inside the pipeline. Instead:

- **Credentials Manager** (Manage Jenkins → Credentials) securely stores secrets
- Secrets are referenced in the pipeline using an ID, never hardcoded
- Common types: Username/Password, Secret Text, SSH Key, Personal Access Token (PAT)

```groovy
pipeline {
    agent any
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds-id')
    }
    stages {
        stage('Login') {
            steps {
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
            }
        }
    }
}
```

## 📚 Shared Library

A **Jenkins Shared Library** is reusable Groovy code (common pipeline steps/functions) stored in a separate Git repository, which multiple Jenkinsfiles across different projects can import — avoiding duplicated pipeline logic.

```groovy
@Library('my-shared-library') _
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                buildAndPush()   // function defined in shared library
            }
        }
    }
}
```

## ⏭️ Post Actions

The `post` block defines steps that run **after** all stages complete, based on the build result — useful for notifications, cleanup, or conditional logic.


```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
    }
    post {
        success {
            echo 'Build succeeded!'
        }
        failure {
            echo 'Build failed!'
        }
        always {
            echo 'This always runs, regardless of result.'
        }
    }
}
```

## 🔁 Post Action Conditions

| Condition | Runs When |
|---|---|
| **always** | Runs regardless of the build result (success, failure, aborted, etc.) |
| **success** | Runs only if the current build succeeded |
| **failure** | Runs only if the current build failed |
| **unstable** | Runs if the build finished with an unstable status (e.g., test failures but not a hard failure) |
| **changed** | Runs only if the current build's result is different from the previous build's result |
| **fixed** | Runs if the current build succeeded **and** the previous build had failed/unstable (i.e., it just got fixed) |
| **regression** | Runs if the current build's status is worse than the previous one (e.g., success → failure) |
| **aborted** | Runs if the build was manually aborted/cancelled |
| **cleanup** | Runs last, after all other post conditions — typically used for workspace cleanup |


## ❓ Questions & Answers

**Q1. Declarative vs Scripted pipeline — when would you use each?**
> Declarative is preferred for standard, straightforward CI/CD pipelines due to its readability and built-in validation. Scripted is used when complex custom logic (loops, conditionals, dynamic stages) is needed that declarative syntax can't easily express.

**Q2. How does Jenkins securely handle secrets like Docker Hub credentials or GitHub tokens?**
> Secrets are stored in Jenkins' built-in Credentials Manager, encrypted at rest, and referenced by ID inside the pipeline — never exposed as plain text in the Jenkinsfile or logs.

**Q3. Why use a Shared Library instead of repeating pipeline code across projects?**
> It centralizes common logic (e.g., build/push steps), making pipelines DRY, easier to maintain, and consistent across multiple repositories/projects.
