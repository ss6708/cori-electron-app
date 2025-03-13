# Running Cori Electron App on Windows

This guide provides detailed instructions for running the Cori Electron desktop application on Windows systems.

## Prerequisites

- Windows 10 or 11
- Docker Desktop for Windows
- WSL2 (Windows Subsystem for Linux)
- X Server for Windows (VcXsrv or Xming)

## Setup Instructions

### 1. Install Docker Desktop

1. Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. Make sure WSL2 integration is enabled in Docker Desktop settings

### 2. Install X Server

1. Download and install [VcXsrv](https://sourceforge.net/projects/vcxsrv/) or [Xming](https://sourceforge.net/projects/xming/)
2. Launch the X Server with these settings:
   - Display number: 0
   - Multiple windows: No (Start no client)
   - Session type: Start no client
   - **Important**: Check "Disable access control" in the Extra settings

### 3. Clone the Repository

```bash
git clone https://github.com/ss6708/cori-electron-app.git
cd cori-electron-app
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the Electron App in Docker

Open a WSL2 terminal and run:

```bash
# Set the DISPLAY environment variable to connect to your X Server
export DISPLAY=host.docker.internal:0

# Run the Docker container
docker-compose -f docker-compose.electron.yml up --build
```

## Troubleshooting

### X Server Connection Issues

If you see errors like "Cannot connect to X server":

1. Make sure your X Server is running with "Disable access control" checked
2. Verify the DISPLAY environment variable is set correctly
3. Check Windows Firewall settings to allow connections to the X Server

### Docker Build Errors

If you encounter Docker build errors related to Python or node-gyp:

```bash
# Use the fixed Dockerfile
mv Dockerfile.frontend.fixed Dockerfile.frontend
docker-compose -f docker-compose.electron.yml up --build
```

### Application Not Starting

1. Check Docker logs:

   ```bash
   docker-compose -f docker-compose.electron.yml logs
   ```

2. Verify your OpenAI API key is correctly set in the `.env` file

## Alternative: Running Without Docker

If you prefer to run the app directly on Windows without Docker:

1. Install Node.js 20+ and Python 3.10+
2. Install dependencies:

   ```bash
   npm ci
   pip install -r backend/requirements.txt
   ```

3. Run the app:

   ```bash
   npm run dev
   ```

## Additional Resources

- [Docker Configuration Guide](README.docker.md)
- [Docker Troubleshooting Guide](docker-troubleshooting.md)
- [Complete Electron App Guide](ELECTRON_APP_GUIDE.md)
