# Socket Permission Troubleshooting Guide

If you encounter the error "an attempt was made to access a socket in a way forbidden by its access permissions" when running the Cori Electron App in a Conda environment, try the following solutions:

## Solution 0: Use the Updated Server Configuration

The latest version of the app has been updated to fix this issue by binding to all network interfaces (0.0.0.0) instead of just localhost (127.0.0.1). Make sure you're using the latest version from the `core-infrastructure` branch.

If you're still experiencing issues, try the solutions below:

## Solution 1: Run as Administrator

The most common cause of this error is insufficient permissions. Try running your command prompt or terminal as Administrator:

1. Right-click on Command Prompt or PowerShell
2. Select "Run as administrator"
3. Navigate to your project directory
4. Activate your conda environment and run the app

## Solution 2: Check Firewall Settings

Windows Firewall might be blocking the application:

1. Open Windows Defender Firewall
2. Click "Allow an app or feature through Windows Defender Firewall"
3. Click "Change settings" and then "Allow another app..."
4. Browse to your Python executable in the conda environment
   (Typically `C:\Users\<username>\miniconda3\envs\cori\python.exe`)
5. Add it to the allowed apps list

## Solution 3: Check Port Availability

The error might occur if the port is already in use:

1. Open Command Prompt as Administrator
2. Run `netstat -ano | findstr :5000` (for backend port)
3. If you see the port is in use, find the process ID (PID) in the last column
4. Run `taskkill /F /PID <PID>` to terminate the process

## Solution 4: Specify a Different Port

You can modify the Flask server to use a different port:

1. Open `.env` file
2. Add or modify: `FLASK_RUN_PORT=5001` (or any available port)
3. Restart the application

## Solution 5: Disable Antivirus Temporarily

Some antivirus software might block socket connections:

1. Temporarily disable your antivirus software
2. Test if the application works
3. If it works, add an exception for the application in your antivirus settings

## Solution 6: Check IPv6 vs IPv4 Settings

Flask might be trying to use IPv6 when only IPv4 is available:

1. Open `backend/server.py`
2. Find where the Flask app is run
3. Make sure it's using `host='0.0.0.0'` instead of `host='::'`

## Solution 7: Check for Multiple Python Installations

Multiple Python installations can cause conflicts:

1. Run `where python` in Command Prompt
2. If multiple paths are shown, make sure your conda environment is properly activated
3. Verify with `python --version` that you're using the correct Python version

## Solution 8: Restart Computer

Sometimes a simple restart can resolve socket permission issues:

1. Close all applications
2. Restart your computer
3. Try running the application again

If none of these solutions work, please provide more details about your specific error message and environment setup.
