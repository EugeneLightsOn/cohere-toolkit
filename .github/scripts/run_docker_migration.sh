#!/bin/bash
cd $SSH_PROJECT_DIR
git pull origin TLK-580_automated_migrations
cd src/backend
make migrate
echo "Migration complete"
