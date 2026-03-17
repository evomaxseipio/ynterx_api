#!/bin/bash

BRANCH=${1:-qa}
SERVER="root@173.212.206.101"

# Protección: solo deployar desde qa o main
CURRENT=$(git branch --show-current)
if [ "$CURRENT" != "qa" ] && [ "$CURRENT" != "main" ]; then
  echo "Error: debes estar en rama 'qa' o 'main' para deployar."
  echo "Rama actual: $CURRENT"
  echo "Haz: git checkout qa && git merge $CURRENT"
  exit 1
fi

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
