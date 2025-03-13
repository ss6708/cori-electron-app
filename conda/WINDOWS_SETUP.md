# Windows Setup Guide for Cori Electron App

This guide provides detailed instructions for setting up and running the Cori Electron App on Windows with Excel integration.

## Prerequisites

- Windows 10 or 11
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (recommended) or [Anaconda](https://www.anaconda.com/download/)
- [Git](https://git-scm.com/download/win)
- Microsoft Excel installed
- OpenAI API key

## Setup Instructions

### 1. Install Miniconda

1. Download Miniconda from [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
2. Run the installer and follow the prompts
3. Select "Add Miniconda3 to my PATH environment variable" during installation

### 2. Clone the Repository

Open Command Prompt or PowerShell and run:

```bash
git clone https://github.com/ss6708/cori-electron-app.git
cd cori-electron-app
```

### 3. Create and Activate Conda Environment

```bash
# Create environment from the provided environment.yml file
conda env create -f conda/environment.yml

# Activate the environment
conda activate cori
```

### 4. Configure Environment Variables

```bash
# Create .env file from example
copy .env.example .env
```

Edit the `.env` file using Notepad or any text editor and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the Application

```bash
# Make sure the conda environment is activated
conda activate cori

# Run the application
npm run dev
```

This will:
1. Start the Python backend server
2. Launch the Next.js frontend
3. Open the Electron desktop application

## Troubleshooting

### Socket Permission Issues

If you encounter the error "an attempt was made to access a socket in a way forbidden by its access permissions", see the [Socket Troubleshooting Guide](SOCKET_TROUBLESHOOTING.md).

### Excel Integration Issues

If Excel integration isn't working:

1. Verify pywin32 is installed:
   ```bash
   pip show pywin32
   ```

2. Make sure you're running the app on Windows (not WSL)

3. Check that Excel is installed and accessible on your system

### Node.js Errors

If you encounter Node.js related errors:

1. Verify Node.js is installed in your conda environment:
   ```bash
   node --version
   ```

2. If Node.js is missing, install it:
   ```bash
   conda install -c conda-forge nodejs=20
   ```

## Development Workflow

### Running the Backend Only

```bash
cd backend
python server.py
```

### Running the Frontend Only

```bash
npm run dev:frontend
```

### Building for Production

```bash
npm run build
npm run start
```

## Additional Resources

- [Conda Environment Guide](CONDA_ENVIRONMENT_GUIDE.md) - Detailed conda environment management
- [Socket Troubleshooting](SOCKET_TROUBLESHOOTING.md) - Solutions for socket permission issues
