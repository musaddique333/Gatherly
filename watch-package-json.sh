#!/bin/bash

export $(grep -v '^#' .env.production | xargs)

ls ./Frontend/gatherly/package.json ./Frontend/gatherly/package-lock.json | entr -r docker compose up --build -d frontend
