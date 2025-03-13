#!/bin/bash

# Allow X server connections from Docker
xhost +local:docker

# Build and run the Electron Docker container
docker-compose -f docker-compose.electron.yml up --build

# Disallow X server connections when done
xhost -local:docker
