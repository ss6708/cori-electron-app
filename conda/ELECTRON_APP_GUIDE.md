# Cori Electron App - User Guide

This guide provides detailed instructions for running the Cori Electron desktop application both locally and using Docker.

## Application Structure

The Cori Electron app consists of three main components:

1. **Python Flask Backend**: Handles AI services and API requests
2. **Next.js Frontend**: Provides the user interface
3. **Electron Wrapper**: Creates a desktop application experience

## Running the App Locally

### Prerequisites

- Node.js 20+
- Python 3.10+
- OpenAI API key

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/ss6708/cori-electron-app.git
   cd cori-electron-app
   ```

2. **Install dependencies**

   ```bash
   npm ci
   pip install -r backend/requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file and add your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the app in development mode**

   ```bash
   npm run dev
   ```

   This will:
   - Start the Next.js development server
   - Wait for it to be ready
   - Build the Electron app
   - Launch the Electron window

## Running the App in Docker

### Prerequisites

- Docker and Docker Compose
- X11 server (for GUI support)
- OpenAI API key

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/ss6708/cori-electron-app.git
   cd cori-electron-app
   ```

2. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file and add your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the app using Docker**

   #### Linux

   ```bash
   # Make the script executable
   chmod +x run-electron-docker.sh

   # Run the script (this handles X11 permissions)
   ./run-electron-docker.sh
   ```

   #### Windows with WSL2

   1. Install an X server like [VcXsrv](https://sourceforge.net/projects/vcxsrv/) or [Xming](https://sourceforge.net/projects/xming/)
   2. Start the X server with "No Access Control" enabled
   3. Run the following commands in WSL2:

      ```bash
      # Set DISPLAY environment variable
      export DISPLAY=host.docker.internal:0

      # Run Docker compose
      docker-compose -f docker-compose.electron.yml up --build
      ```

   #### macOS

   1. Install [XQuartz](https://www.xquartz.org/)
   2. Start XQuartz and enable "Allow connections from network clients" in Preferences
   3. Run the following commands:

      ```bash
      # Set DISPLAY environment variable
      export DISPLAY=host.docker.internal:0

      # Run Docker compose
      docker-compose -f docker-compose.electron.yml up --build
      ```

## Troubleshooting

### X11 Permission Issues

If you encounter X11 permission issues, try running:

```bash
xhost +local:docker
```

### Docker Build Errors

If you encounter Docker build errors related to Python or node-gyp:

```bash
# Use the fixed Dockerfile
mv Dockerfile.frontend.fixed Dockerfile.frontend
docker-compose -f docker-compose.electron.yml up --build
```

For more Docker troubleshooting, see `docker-troubleshooting.md`.

### Application Not Starting

1. Check if the backend is running:

   ```bash
   docker-compose logs backend
   ```

2. Check if the frontend is running:

   ```bash
   docker-compose logs frontend
   ```

3. Verify your OpenAI API key is correctly set in the `.env` file

## Remote Access Options

If you need to access the Cori app remotely:

1. **Web Version**: Access the Next.js frontend at http://your-server-ip:3000
2. **API Access**: Use the backend API directly at http://your-server-ip:5000
3. **Remote Desktop**: Use a remote desktop solution to access the Electron app GUI

## Additional Resources

- [Docker Configuration Guide](README.docker.md)
- [Docker Troubleshooting Guide](docker-troubleshooting.md)
