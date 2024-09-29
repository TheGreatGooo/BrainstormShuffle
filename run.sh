#!/bin/bash
podman build -f Dockerfile.backend -t local/brainstorm-shuffle-backend
podman build -f Dockerfile.nginx -t local/brainstorm-shuffle-nginx
podman run -p 8000:8000 local/brainstorm-shuffle-backend
podman run -p 8080:80 local/brainstorm-shuffle-nginx
