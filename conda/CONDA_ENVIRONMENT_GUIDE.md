# Conda Environment Setup for Cori Electron App

This guide explains how to set up a Conda environment for the Cori Electron App on Windows, which isolates Python dependencies while maintaining access to Excel through win32com.

## Prerequisites

- Windows 10 or 11
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/download/)
- Git

## Setup Instructions

### 1. Install Miniconda or Anaconda

Download and install Miniconda (recommended) or Anaconda from the links above.

### 2. Clone the Repository

```bash
git clone https://github.com/ss6708/cori-electron-app.git
cd cori-electron-app
```

### 3. Create a Conda Environment

```bash
# Create a new conda environment with Python 3.10
conda create -n cori python=3.10

# Activate the environment
conda activate cori
```

### 4. Install Python Dependencies

```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Install pywin32 for Excel integration
pip install pywin32
```

### 5. Install Node.js Dependencies

```bash
# Install Node.js (if not already installed)
conda install -c conda-forge nodejs=20

# Install npm dependencies
npm ci
```

### 6. Configure Environment Variables

```bash
# Create .env file from example
copy .env.example .env
```

Edit the `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 7. Run the Application

```bash
# Make sure the conda environment is activated
conda activate cori

# Run the application
npm run dev
```

## Managing the Environment

### Updating Dependencies

If the project dependencies change, update your environment:

```bash
# Update Python dependencies
pip install -r backend/requirements.txt

# Update npm dependencies
npm ci
```

### Deactivating the Environment

When you're done working with the app:

```bash
conda deactivate
```

### Removing the Environment

If you need to remove the environment completely:

```bash
conda remove --name cori --all
```

## Troubleshooting

### Python Package Conflicts

If you encounter package conflicts:

```bash
# Create a fresh environment
conda create -n cori-new python=3.10
conda activate cori-new
pip install -r backend/requirements.txt
```

### Excel Integration Issues

If Excel integration isn't working:

1. Verify pywin32 is installed:
   ```bash
   pip show pywin32
   ```

2. Make sure you're running the app on Windows (not WSL)

3. Check that Excel is installed and accessible on your system
