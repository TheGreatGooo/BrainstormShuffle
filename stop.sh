#!/bin/bash
set -e
podman stop brainstorm-shuffle-backend
podman stop brainstorm-shuffle-nginx
podman rm brainstorm-shuffle-backend
podman rm brainstorm-shuffle-nginx