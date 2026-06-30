#!/bin/bash
set -e

mkdir -p /app/backups /app/uploads /app/uploads/logos
chown -R appuser:appuser /app/backups /app/uploads

exec gosu appuser "$@"
