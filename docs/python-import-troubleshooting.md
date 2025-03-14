# Python Import Troubleshooting Guide for Cori

This guide addresses common Python import errors when running the Cori backend server, particularly after pulling new changes from the repository.

## Common Import Errors

### 1. `ModuleNotFoundError: No module named 'backend'`

This error occurs when Python cannot find modules in the `backend` package. This is typically due to the Python path not being set correctly.

#### Solution for Windows:

```cmd
cd C:\path\to\cori-electron-app
set PYTHONPATH=%PYTHONPATH%;C:\path\to\cori-electron-app
python backend/server_enhanced.py
```

#### Solution for Linux/macOS:

```bash
cd /path/to/cori-electron-app
PYTHONPATH=$PYTHONPATH:/path/to/cori-electron-app python backend/server_enhanced.py
```

### 2. Missing Dependencies (e.g., `ModuleNotFoundError: No module named 'chromadb'`)

This occurs when required Python packages are not installed in your environment.

#### Solution:

```bash
# Install specific missing package
pip install chromadb

# Or install all requirements
pip install -r backend/requirements.txt
```

### 3. Relative Import Errors

If you see errors like:
```
ModuleNotFoundError: No module named 'backend.memory.knowledge.knowledge_extraction'
```

This may require modifying import statements in the code.

#### Solution:

Edit the file with the import error to use relative imports:

```python
# Change from:
from backend.memory.knowledge.knowledge_extraction import KnowledgeExtractor

# To:
from .knowledge_extraction import KnowledgeExtractor
```

## Conda Environment Issues

### Checking Active Environment

To check if a conda environment is active:

```bash
conda info --envs
```

The active environment will have an asterisk (*) next to it.

### Activating Environment

```bash
conda activate environment_name
```

### Creating a New Environment

If your environment is corrupted:

```bash
conda create -n cori-env python=3.10
conda activate cori-env
pip install -r backend/requirements.txt
```

## Complete Troubleshooting Workflow

If you're experiencing multiple import errors, follow this workflow:

1. **Stop all running servers**
   - Press Ctrl+C in terminals running Python server and Next.js

2. **Set up Python path correctly**
   - Windows:
     ```cmd
     cd C:\path\to\cori-electron-app
     set PYTHONPATH=%PYTHONPATH%;C:\path\to\cori-electron-app
     ```
   - Linux/macOS:
     ```bash
     cd /path/to/cori-electron-app
     export PYTHONPATH=$PYTHONPATH:/path/to/cori-electron-app
     ```

3. **Install or update dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Try running the server again**
   ```bash
   python backend/server_enhanced.py
   ```

5. **If still encountering import errors**:
   - Check the specific error message
   - Look for the file with the problematic import
   - Consider modifying the import to use relative paths
   - If using a complex directory structure, create an empty `__init__.py` file in each directory to make it a proper package

## Advanced: Creating a Launch Script

To avoid setting the Python path manually each time, create a launch script:

### Windows (`run_server.bat`):

```batch
@echo off
cd %~dp0
set PYTHONPATH=%PYTHONPATH%;%CD%
python backend/server_enhanced.py
```

### Linux/macOS (`run_server.sh`):

```bash
#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH=$PYTHONPATH:$(pwd)
python backend/server_enhanced.py
```

Make the script executable on Linux/macOS:
```bash
chmod +x run_server.sh
```

## Electron Build Issues

If encountering symbolic link errors during Electron builds on Windows:

```
ERROR: Cannot create symbolic link : A required privilege is not held by the client.
```

This occurs because Windows requires administrator privileges to create symbolic links.

### Solutions:

1. **Run as Administrator**:
   - Right-click on Command Prompt or PowerShell
   - Select "Run as administrator"
   - Navigate to your project directory
   - Run the build command

2. **Enable Developer Mode**:
   - Open Windows Settings
   - Go to Update & Security > For developers
   - Enable "Developer Mode"
   - Restart your computer

3. **Use WSL (Windows Subsystem for Linux)**:
   - Install WSL
   - Run your build commands in the Linux environment

## Slow Build Performance

If your Electron build is extremely slow:

1. **Check system resources**:
   - Close other resource-intensive applications
   - Monitor CPU, RAM, and disk usage in Task Manager

2. **Optimize node_modules**:
   - Consider using pnpm instead of npm for faster package management
   - Run `npm prune` to remove unused packages

3. **Exclude from antivirus scanning**:
   - Add your project directory to antivirus exclusions

4. **Use SSD storage** if available

5. **Increase Node.js memory limit**:
   ```
   set NODE_OPTIONS=--max-old-space-size=4096
   ```

## Contact Support

If you continue to experience issues after trying these solutions, please:

1. Create an issue on GitHub with:
   - Your operating system details
   - Python version (`python --version`)
   - Complete error message
   - Steps to reproduce

2. Or contact the development team directly
