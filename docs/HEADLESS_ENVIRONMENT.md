# Running Cori in a Headless Environment

When running the Cori application in a headless environment (without a GUI), you may encounter issues with the Electron component. This is expected as Electron requires an X server to display the GUI.

## Running the Backend and Frontend

You can still run and test the backend and frontend components separately:

### Backend

```bash
cd backend
python server.py
```

The backend will run on http://localhost:5000.

### Frontend

```bash
npx next dev
```

The frontend will run on http://localhost:3000.

## Testing the Application

You can test the application by accessing the frontend in a browser and interacting with the UI. The frontend will communicate with the backend API.

## Known Issues

- Electron fails with "Missing X server or $DISPLAY" error in headless environments
- This is expected behavior as Electron requires a GUI environment
