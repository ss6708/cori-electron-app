# Docker Setup for Cori Electron App

This guide explains how to run the Cori Electron App using Docker, which provides an isolated environment with all dependencies pre-configured.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/ss6708/cori-electron-app.git
   cd cori-electron-app
   ```

2. **Configure environment variables**

   Copy the example environment file and add your OpenAI API key:

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file and replace `your_openai_api_key_here` with your actual OpenAI API key.

3. **Build and start the containers**

   ```bash
   docker-compose up -d
   ```

   This will build the Docker images and start the containers in detached mode.

4. **Access the application**

   The application will be running in containers, but you'll need to expose the ports to access it from outside the Docker environment.

## Development Workflow

### Viewing logs

```bash
# View logs from all services
docker-compose logs -f

# View logs from a specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuilding containers

If you make changes to the Dockerfiles or need to rebuild the containers:

```bash
docker-compose up -d --build
```

### Stopping containers

```bash
docker-compose down
```

### Running commands inside containers

```bash
# Run a command in the backend container
docker-compose exec backend python -m flask --help

# Run a command in the frontend container
docker-compose exec frontend npm run lint
```

## Project Structure in Docker

- Backend code is mounted as a volume, so changes are reflected immediately
- Frontend code is mounted as a volume for development
- The `sessions` directory is persisted as a Docker volume

## Troubleshooting

### Backend container exits immediately

Check the logs for errors:

```bash
docker-compose logs backend
```

Common issues:
- Missing environment variables
- Dependency conflicts
- Port conflicts

### Frontend container can't connect to backend

Make sure the backend container is running and the environment variables are set correctly:

```bash
docker-compose ps
```

## Production Deployment

For production deployment, modify the Dockerfiles and docker-compose.yml:

1. Set `FLASK_ENV=production` in the backend environment
2. Remove development volumes
3. Add proper logging configuration
4. Consider using a reverse proxy like Nginx

## Additional Configuration

### Using a different port

Edit the `docker-compose.yml` file and change the port mapping:

```yaml
ports:
  - "8080:3000"  # Change 8080 to your desired port
```

### Adding custom environment variables

Add them to the `.env` file and update the `docker-compose.yml` file to include them.
