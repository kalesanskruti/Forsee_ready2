#! /usr/bin/env bash

# Let the DB start
sleep 10;

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Start the application
# This script assumes it's being chained or the user will run the app command after this.
# But usually prestart is just for setup.
