#!/bin/bash
# Runs as the devcontainer postCreateCommand.
set -e

cd "$(dirname "$0")/.."

echo "Installing Python dependencies with uv..."
uv sync

echo "Installing frontend dependencies..."
npm --prefix frontend ci

if [ ! -f .env ]; then
  echo "Creating .env from .env.example — edit it before running the app."
  cp .env.example .env
fi

echo "Done. Run 'make dev' to start the app, or 'make help' to see all targets."
