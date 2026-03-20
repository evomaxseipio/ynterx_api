#!/bin/bash

BRANCH=${1:-qa}
SERVER="root@173.212.206.101"
CURRENT=$(git branch --show-current)

# Si estás en una feature branch, hacer merge a qa automáticamente
if [ "$CURRENT" != "qa" ] && [ "$CURRENT" != "main" ]; then
  echo ">>> Rama actual: $CURRENT"
  echo ">>> Haciendo merge a qa automaticamente..."
  git checkout qa
  if ! git merge "$CURRENT"; then
    echo "Error: merge fallido. Resuelve los conflictos manualmente."
    exit 1
  fi
  echo ">>> Merge exitoso: $CURRENT -> qa"
fi

# Actualizar CURRENT despues del posible checkout
CURRENT=$(git branch --show-current)

echo ">>> Pushing $CURRENT a GitHub..."
git push origin "$CURRENT"

echo ">>> Deployando $CURRENT en servidor QA..."
ssh $SERVER << ENDSSH
  cd /opt/ynterx-dev
  git fetch origin
  git checkout $CURRENT
  git pull origin $CURRENT
  docker compose build api
  docker compose up -d api
  docker compose ps
ENDSSH

echo ">>> Deploy completado en QA"
