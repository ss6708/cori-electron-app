# Environment Setup Guide for Cori Electron App

This guide explains how to set up your environment for the Cori Electron App, including configuring API keys and other environment variables.

## Setting Up Environment Variables

The Cori Electron App uses environment variables to store sensitive information like API keys. Here's how to set them up:

### Method 1: Using a .env File (Recommended)

1. Create a file named `.env` in the root directory of the project.
2. Add your environment variables in the following format:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. Save the file.

### Method 2: Setting Environment Variables Directly

#### Windows
```
set OPENAI_API_KEY=your_openai_api_key_here
```

#### macOS/Linux
```
export OPENAI_API_KEY=your_openai_api_key_here
```

## Required Environment Variables

| Variable Name | Description | Required |
|---------------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key for GPT-4o-mini integration | Yes |

## Installing python-dotenv

The backend uses `python-dotenv` to load environment variables from the `.env` file. If you haven't installed it yet, run:

```
pip install python-dotenv
```

## Updating the Backend to Use .env Files

To ensure the backend properly loads environment variables from the `.env` file, add the following code to the top of `backend/server.py`:

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
```

## Verifying Your Setup

To verify that your environment variables are correctly set up:

1. Start the backend server:
   ```
   cd ~/repos/cori-electron-app
   python backend/server.py
   ```

2. If the server starts without any "API key not found" errors, your environment is correctly configured.

## Troubleshooting

If you encounter the error "OpenAI API key not found in environment variables":

1. Double-check that your `.env` file is in the root directory of the project.
2. Ensure the variable name is exactly `OPENAI_API_KEY` (case-sensitive).
3. Make sure there are no spaces around the equals sign in the `.env` file.
4. Verify that `python-dotenv` is installed.
5. Restart the backend server after making changes.

## Development vs. Production Environment

For development, using a `.env` file is convenient. For production, it's recommended to set environment variables at the system or container level for better security.
