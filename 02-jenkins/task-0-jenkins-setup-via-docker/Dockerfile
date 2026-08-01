# Stage 1: Download Jenkins plugins
FROM jenkins/jenkins:lts AS plugin-builder
USER jenkins
RUN jenkins-plugin-cli \
    --plugins "git workflow-aggregator docker-workflow" \
    --plugin-download-directory /tmp/plugins

# Stage 2: Final image
FROM jenkins/jenkins:lts
COPY --from=plugin-builder --chown=jenkins:jenkins \
    /tmp/plugins/ /usr/share/jenkins/ref/plugins/
USER jenkins
VOLUME /var/jenkins_home