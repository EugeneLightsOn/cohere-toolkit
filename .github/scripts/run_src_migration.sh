#!/bin/bash
cd $SSH_PROJECT_DIR
git pull origin TLK-580_automated_migrations
source .venv/bin/activate
cd src/backend
alembic -c alembic.ini upgrade head
echo "Migration complete"
