#!/bin/bash
cd $SSH_PROJECT_DIR
git pull origin TLK-580_automated_migrations
source .venv/bin/activate
alembic -c src/backend/alembic.ini upgrade head
echo "Migration complete"
