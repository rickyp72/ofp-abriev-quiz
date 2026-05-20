#!/bin/bash
set -euo pipefail

# Update and install Docker + git
dnf update -y
dnf install -y docker git

# Start Docker and enable on boot
systemctl enable docker
systemctl start docker
usermod -aG docker ec2-user

# Install Docker Compose plugin
COMPOSE_VERSION="v2.24.6"
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL "https://github.com/docker/compose/releases/download/$${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Clone the repo and start the app
git clone ${repo_url} /opt/ofp-abriev-quiz
chown -R ec2-user:ec2-user /opt/ofp-abriev-quiz
cd /opt/ofp-abriev-quiz
docker compose up -d
