#!/bin/bash

BRANCH=${1:-qa}
SERVER="root@173.212.206.101"

echo ">>> Pushing $BRANCH a GitHub..."
git push origin $BRANCH

echo ">>> Deployando $BRANCH en servidor QA..."
ssh $SERVER << ENDSSH
  cd /opt/ynterx-dev
  git fetch origin
  git checkout $BRANCH
  git pull origin $BRANCH
  docker compose build api
  docker compose up -d api
  docker compose ps
ENDSSH

echo ">>> Deploy completado en QA"
