#!/bin/bash

# Test script for Odoo 13.0 module in Docker connecting to local PostgreSQL

echo "Building and testing Mail Reply-To Interceptor module for Odoo 13.0..."
echo "Using local PostgreSQL database..."

# Run tests only
echo "Running module tests..."
docker-compose run --rm odoo bash -c "
  until pg_isready -h host.docker.internal -p 5432 -U dd; do
    echo 'Waiting for local database...'
    sleep 2
  done
  echo 'Database ready, running tests...'
  odoo --addons-path=/mnt/extra-addons -d odoo13_test --stop-after-init -i mail_reply_to_interceptor --test-enable --test-tags=mail_reply_to_interceptor
"

# Check the exit code
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed!"
    exit 1
fi

# Cleanup
echo "Cleaning up..."
docker-compose down -v

echo "Test completed!"