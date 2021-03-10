#!/bin/bash
while ! nc -z postgres 5432; do sleep 3; done

while ! nc -z lavalink 2333; do sleep 3; done

python -m bot
