# Backend API Extensions for Cori RAG++ System

This document outlines the design for extending Cori's backend API to support the RAG++ memory retrieval system, focusing on new endpoints for knowledge base management, user preference management, feedback collection, and tool execution.

## 1. Current API Structure

The existing backend API (`backend/server.py`) currently:

- Uses Flask with CORS enabled
- Provides a `/chat` endpoint for OpenAI interactions
- Handles basic message formatting and response generation
- Manages session state for conversation history

## 2. API Extension Overview

The API will be extended with the following new endpoints:

```
┌──────────────────────────────────────────────────────────────────┐
│                     Extended Backend API                         │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │  Knowledge Base │  │  User Preference│  │  Feedback       │   │
│  │  Endpoints      │  │  Endpoints      │  │  Endpoints      │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│           │                   │                    │              │
│           ▼                   ▼                    ▼              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │  Tool Execution │  │  Enhanced Chat  │  │  Session        │   │
│  │  Endpoints      │  │  Endpoint       │  │  Management     │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## 3. Knowledge Base Management Endpoints

### 3.1 Knowledge Base CRUD Operations

```
POST /api/knowledge                 # Create knowledge entry
GET /api/knowledge/{entry_id}       # Retrieve knowledge entry
PUT /api/knowledge/{entry_id}       # Update knowledge entry
DELETE /api/knowledge/{entry_id}    # Delete knowledge entry
```

### 3.2 Knowledge Base Search and Query

```
GET /api/knowledge/search?query={search_query}&domain={domain}&type={type}&limit={limit}
POST /api/knowledge/semantic-search # Advanced semantic search with context
```

### 3.3 Batch Knowledge Operations

```
POST /api/knowledge/batch-import    # Batch import knowledge entries
GET /api/knowledge/batch-import/{job_id}/status  # Check import status
```

## 4. User Preference Management Endpoints

### 4.1 User Preference CRUD Operations

```
POST /api/preferences              # Set user preference
GET /api/preferences?type={preference_type}&category={category}  # Get preferences
PUT /api/preferences/{preference_id}  # Update preference
DELETE /api/preferences/{preference_id}  # Delete preference
```

### 4.2 Preference Context Management

```
POST /api/preferences/contextual   # Get contextual preferences
POST /api/preferences/infer        # Infer preferences from interactions
```

## 5. Feedback Collection Endpoints

### 5.1 Feedback Submission

```
POST /api/feedback/response        # Submit response feedback
POST /api/feedback/correction      # Submit correction
POST /api/feedback/implicit        # Submit implicit feedback
```

### 5.2 Feedback Analysis

```
GET /api/feedback/summary?domain={domain}&period={period}  # Get feedback summary
GET /api/feedback/knowledge-gaps?domain={domain}  # Get knowledge gap analysis
```

## 6. Tool Execution Endpoints

### 6.1 Tool Registry and Discovery

```
GET /api/tools?category={category}&domain={domain}  # List available tools
GET /api/tools/{tool_id}           # Get tool details
```

### 6.2 Tool Execution

```
POST /api/tools/{tool_id}/execute  # Execute tool
GET /api/tools/executions/{execution_id}  # Get execution status
```

## 7. Enhanced Chat Endpoint

The existing `/chat` endpoint will be enhanced to integrate with the RAG++ system:

```python
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = [Message(**msg) for msg in data.get('messages', [])]
    user_query = messages[-1].content if messages and messages[-1].role == "user" else ""
    
    # Extract context from request
    context = {
        "conversation_history": data.get('conversation_history', []),
        "excel_state": data.get('excel_state', {}),
        "user_preferences": get_user_preferences(data.get('preference_context', {}))
    }
    
    # Detect domain from query
    domain = detect_domain(user_query, context)
    
    # Get enhanced completion with RAG
    response = openai_handler.get_rag_enhanced_completion(
        messages=messages,
        user_query=user_query,
        context=context,
        domain=domain
    )
    
    # Record interaction for feedback learning
    record_interaction(user_query, response.content, context)
    
    return jsonify(response.to_dict())
```

## 8. Implementation Considerations

### 8.1 Authentication and Authorization

- Implement JWT-based authentication for API endpoints
- Define role-based access control for sensitive operations
- Secure endpoints with appropriate middleware

### 8.2 Error Handling

- Implement consistent error response format
- Include appropriate HTTP status codes
- Provide detailed error messages for debugging

### 8.3 Rate Limiting

- Implement rate limiting for public-facing endpoints
- Configure different limits based on endpoint sensitivity
- Include rate limit information in response headers

### 8.4 Logging and Monitoring

- Log all API requests and responses
- Implement performance monitoring
- Track error rates and response times

### 8.5 API Versioning

- Include API version in URL path (e.g., `/api/v1/knowledge`)
- Maintain backward compatibility for existing clients
- Document breaking changes between versions

## 9. API Documentation

- Generate OpenAPI/Swagger documentation
- Include example requests and responses
- Document authentication requirements
- Provide SDK examples for common languages

## 10. Integration with Frontend

The frontend will need to be updated to interact with these new endpoints:

```typescript
// Example frontend integration for knowledge search
async function searchKnowledge(query: string, domain?: string): Promise<KnowledgeSearchResult[]> {
  const params = new URLSearchParams();
  params.append('query', query);
  if (domain) params.append('domain', domain);
  
  const response = await fetch(`/api/knowledge/search?${params.toString()}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error(`Knowledge search failed: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data.results;
}
```

## 11. Conclusion

This API extension design provides a comprehensive framework for supporting the RAG++ memory retrieval system in Cori. By implementing these endpoints, Cori will be able to manage knowledge, user preferences, and feedback while providing powerful tool execution capabilities for financial modeling tasks.
