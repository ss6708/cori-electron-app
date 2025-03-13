# FactSet Integration Analysis for Cori

## Executive Summary

This document analyzes the approach for integrating FactSet plugin data into Cori to create a "FactSet" agent capable of automatically writing and refreshing FactSet formulas in Excel cells. The integration assumes users already have the FactSet plugin installed and can use the FactSet integration plugin in Excel.

## Current Architecture Analysis

Cori's architecture consists of:
- A minimal Flask backend (`backend/server.py`) that uses `win32com.client` for Excel COM automation
- A React/TypeScript frontend with an Excel agent UI component (`src/excel-agent-ui.tsx`)
- An Electron wrapper that launches both the frontend and backend

The current implementation is lightweight with no existing OpenAI integration or AI services folder, contrary to previous documentation. This simplifies our integration approach as we can design a clean FactSet service implementation.

## FactSet Integration Approach

### 1. Backend Service Layer

**Recommendation: Create a dedicated FactSet service in the backend**

```
backend/
  ├── server.py (existing)
  ├── services/
  │   ├── __init__.py
  │   ├── factset_service.py (new)
  │   └── excel_service.py (new, refactored from server.py)
  └── requirements.txt (update with FactSet dependencies)
```

The `factset_service.py` would:
- Implement OAuth2 authentication with FactSet using user credentials
- Provide an interface to the FactSet Formula API via the Python SDK (`fds.sdk.Formula`)
- Support both time-series and cross-sectional data endpoints
- Generate FQL (FactSet Query Language) formulas programmatically
- Cache authentication tokens and frequently used data

### 2. Excel Integration Layer

**Recommendation: Extend Excel COM automation to interact with FactSet plugin**

The Excel integration would:
- Detect if the FactSet Excel add-in is installed and activated
- Use COM automation to write FactSet formulas to cells
- Trigger formula refreshes via COM commands
- Read formula results back from cells
- Handle error states and authentication issues

### 3. API Endpoints

**Recommendation: Add new Flask endpoints to server.py**

```python
@app.route('/factset/authenticate', methods=['POST'])
def authenticate_factset():
    # Handle FactSet authentication

@app.route('/factset/formula', methods=['POST'])
def create_factset_formula():
    # Generate and insert FactSet formula into Excel

@app.route('/factset/refresh', methods=['POST'])
def refresh_factset_data():
    # Refresh FactSet data in the current worksheet
```

### 4. Frontend Integration

**Recommendation: Add FactSet-specific UI components without modifying Excel code**

Since Excel-related functionality is being developed separately, the FactSet agent UI should be implemented as a standalone component that communicates with the backend services but doesn't modify the Excel embedding code.

## Technical Implementation Considerations

### 1. FactSet Formula Generation

The FactSet agent would need to:
- Understand financial modeling concepts to generate appropriate formulas
- Convert natural language requests into FQL syntax
- Support common financial data points (e.g., P/E ratios, revenue growth, etc.)
- Handle different time periods and frequencies

### 2. Authentication Flow

Since users already have FactSet credentials:
- Store credentials securely using environment variables
- Implement token refresh mechanisms
- Handle authentication errors gracefully

### 3. Excel COM Automation

For interacting with the FactSet Excel plugin:
```python
def insert_factset_formula(cell_reference, formula):
    excel = win32com.client.Dispatch("Excel.Application")
    worksheet = excel.ActiveSheet
    cell = worksheet.Range(cell_reference)
    cell.Formula = formula
    return {"status": "success", "cell": cell_reference, "formula": formula}
```

### 4. Error Handling

Robust error handling for:
- FactSet plugin not installed
- Authentication failures
- Formula syntax errors
- Data retrieval timeouts

## Integration Architecture Diagram

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Cori Frontend  │◄────►│  Flask Backend  │◄────►│  Excel via COM  │
│                 │      │                 │      │                 │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         │                        ▼                        ▼
         │               ┌─────────────────┐      ┌─────────────────┐
         │               │                 │      │                 │
         └──────────────►│ FactSet Service │◄────►│ FactSet Plugin  │
                         │                 │      │                 │
                         └─────────────────┘      └─────────────────┘
```

## FactSet API and SDK Analysis

The FactSet Formula API provides:
- A Python SDK (`fds.sdk.Formula`) available via PyPI
- Two primary endpoints:
  - Time-Series endpoint (optimized for time-series analysis)
  - Cross-Sectional endpoint (designed for cross-sectional analysis)
- OAuth2 authentication with FactSet credentials
- FQL (FactSet Query Language) for formula syntax

## Conclusion

This integration approach leverages Cori's existing architecture while adding a dedicated FactSet service layer that can:
1. Generate FactSet formulas based on user requests
2. Insert those formulas into Excel cells via COM automation
3. Refresh data as needed
4. Read and interpret the results

The approach respects the constraint that Excel-related functionality is being developed separately by creating a standalone service that interacts with Excel through the existing COM automation interface without modifying the Excel embedding code.

This implementation would enable Cori to become a truly proficient financial modeler by incorporating FactSet's extensive financial data directly into spreadsheets, enhancing the analytical capabilities available to users.

## Implementation Requirements

1. **FactSet API Access**: Purchase access to the FactSet Developer API
2. **Python Dependencies**: Install the FactSet Formula SDK (`pip install fds.sdk.Formula`)
3. **Authentication**: Set up secure storage for FactSet credentials
4. **Excel COM Integration**: Ensure compatibility with the FactSet Excel plugin

## Next Steps

1. Acquire FactSet API access and credentials
2. Set up development environment with FactSet SDK
3. Create proof-of-concept for basic formula generation
4. Develop Excel COM automation for FactSet formula insertion
5. Implement authentication flow
6. Build frontend UI components for the FactSet agent
7. Test with real financial data scenarios
