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
├── public/               # Static assets
│   ├── file.svg          # File icon
│   ├── globe.svg         # Globe icon
│   ├── next.svg          # Next.js logo
│   ├── vercel.svg        # Vercel logo
│   └── window.svg        # Window icon
├── src/                  # Source code
│   └── app/              # Next.js app directory
│       ├── globals.css   # Global styles
│       ├── layout.tsx    # Root layout component
│       └── page.tsx      # Main page component
├── .gitignore            # Git ignore rules
├── eslint.config.mjs     # ESLint configuration
├── next.config.ts        # Next.js configuration
├── package.json          # Project dependencies and scripts
├── postcss.config.mjs    # PostCSS configuration for Tailwind
└── tsconfig.json         # TypeScript configuration
```

## Development Status

- **Implemented**: Basic Next.js application structure with Tailwind CSS styling
- **In Progress**: 
  - Electron integration (referenced in package.json but not implemented)
  - Excel Agent UI (referenced in page.tsx but not implemented)
  - Python backend server (mentioned in README but not implemented)

## Getting Started

First, run the development server:

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

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
