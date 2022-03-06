#!/bin/bash

# Postgres
while ! nc -z postgres 5432; do sleep 3; done

# Lavalink
while ! nc -z lavalink 2333; do sleep 3; done

# Run the bot
python -m bot
