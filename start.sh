#!/bin/bash
set -e
pushd frontend/brainstorm-shuffle-app
npm install
npm run build
popd
podman build -f Dockerfile.backend -t local/brainstorm-shuffle-backend
podman build -f Dockerfile.nginx -t local/brainstorm-shuffle-nginx
podman run -d -p 8000:8000 --name brainstorm-shuffle-backend local/brainstorm-shuffle-backend
podman run -d -p 8080:80 --name brainstorm-shuffle-nginx local/brainstorm-shuffle-nginx
