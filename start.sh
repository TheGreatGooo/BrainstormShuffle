#!/bin/bash
set -e
pushd frontend/brainstorm-shuffle-app
npm install
npm run build
popd
docker build -f Dockerfile.backend -t local/brainstorm-shuffle-backend
docker build -f Dockerfile.nginx -t local/brainstorm-shuffle-nginx
docker run -d -p 8000:8000 -v ./backend:/app --name brainstorm-shuffle-backend local/brainstorm-shuffle-backend
docker run -d -p 8080:80 -v ./frontend/brainstorm-shuffle-app/dist:/config/www -v ./nginx.conf:/config/nginx/site-confs/default.conf --name brainstorm-shuffle-nginx local/brainstorm-shuffle-nginx

