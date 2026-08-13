#!/usr/bin/env bash

set -e

PROJECT="$(dirname "$(realpath "$0")")/.."
PROJECT="$(realpath "$PROJECT")"

cd "$PROJECT"

git fetch origin main --quiet

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    exit 0
fi

echo "$(date): Nuevo commit detectado: $REMOTE"

git reset --hard origin/main

pnpm install --frozen-lockfile

cd apps/octobeat
pnpm run build

echo "$(date): Deploy completado"
