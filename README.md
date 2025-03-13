# CORI

Cori is the best financial modeller in the world for the most complex transactions.

## Project Overview

This is an Electron desktop application with a Next.js frontend and a Python backend server. The project aims to provide a powerful financial modelling tool with Excel integration capabilities.

### Current Status

The project is in early development stages with the foundational architecture set up. Key components like the Electron implementation and Python backend are referenced but not fully implemented yet.

## Tech Stack

- **Frontend**: Next.js 15 (pre-release) with React 19 (pre-release)
- **UI Components**: Radix UI component library
- **Styling**: Tailwind CSS 4
- **Desktop Wrapper**: Electron
- **Backend**: Python server (planned)
- **Excel Integration**: Using winax for Windows COM automation

## Project Structure

```
cori-electron-app/
├── backend/              # Python backend server
│   ├── ai_services/      # OpenAI integration
│   ├── core/             # Core infrastructure components
│   ├── models/           # Data models
│   ├── requirements.txt  # Python dependencies
│   └── server.py         # Flask server
├── conda/                # Conda environment setup
│   ├── environment.yml   # Conda environment definition
│   ├── WINDOWS_SETUP.md  # Windows setup guide
│   └── SOCKET_TROUBLESHOOTING.md # Socket troubleshooting
├── docker/               # Docker configuration
│   ├── Dockerfile.*      # Various Dockerfiles
│   └── docker-compose.*  # Docker Compose configurations
├── public/               # Static assets
│   ├── file.svg          # File icon
│   ├── globe.svg         # Globe icon
│   ├── next.svg          # Next.js logo
│   ├── vercel.svg        # Vercel logo
│   └── window.svg        # Window icon
├── src/                  # Frontend source code
│   ├── app/              # Next.js app directory
│   ├── lib/              # Shared libraries
│   └── components/       # React components
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
├── eslint.config.mjs     # ESLint configuration
├── next.config.ts        # Next.js configuration
├── package.json          # Project dependencies and scripts
├── postcss.config.mjs    # PostCSS configuration for Tailwind
└── tsconfig.json         # TypeScript configuration
```

## Development Status

- **Implemented**: 
  - Basic Next.js application structure with Tailwind CSS styling
  - Python Flask backend server with OpenAI integration
  - Core infrastructure components (event system, state management, session persistence)
  - Conda environment setup for Windows with Excel integration
  - Docker configuration for development without Excel dependencies

- **In Progress**: 
  - Electron integration refinement
  - Excel Agent UI enhancements
  - RAG system for specialized knowledge

## Getting Started

### Windows Setup with Conda (Recommended for Excel Integration)

For Windows users who need Excel integration, we recommend using the Conda environment:

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
2. Create and activate the conda environment:
   ```bash
   conda env create -f conda/environment.yml
   conda activate cori
   ```
3. Configure your OpenAI API key in `.env`
4. Run the application:
   ```bash
   npm run dev
   ```

For detailed instructions, see [Windows Setup Guide](conda/WINDOWS_SETUP.md).

### Standard Setup

If you're not using Windows or don't need Excel integration, you can use the standard setup:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Environment Setup Options

### 1. Conda Environment (Recommended for Windows with Excel)

The Conda environment provides:
- Isolated Python dependencies to avoid conflicts
- Access to Excel through win32com on Windows
- Consistent development environment

See [Conda Environment Guide](conda/CONDA_ENVIRONMENT_GUIDE.md) for details.

### 2. Docker Setup (For Development Without Excel)

The Docker configuration provides:
- Completely isolated environment
- Consistent development experience across platforms
- Support for both backend and frontend

**Note:** Docker cannot access Excel through win32com since containers run in a Linux environment.

See [Docker Configuration Guide](docker/README.docker.md) for details.

## Troubleshooting

- **Socket Permission Issues**: See [Socket Troubleshooting Guide](conda/SOCKET_TROUBLESHOOTING.md)
- **Excel Integration Issues**: See [Windows Setup Guide](conda/WINDOWS_SETUP.md)
- **Docker Issues**: See [Docker Troubleshooting Guide](docker/docker-troubleshooting.md)
