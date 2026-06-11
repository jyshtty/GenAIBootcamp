# API Guide

## Getting Started

This API provides access to repository information and code analysis.

### Authentication

Use GitHub token for authentication:
```
Authorization: Bearer your_token_here
```

### Endpoints

- GET /repository - Get repository information
- GET /files - List repository files
- GET /content - Get file content

## Rate Limits

- 5000 requests per hour per token
- 1000 requests per hour for unauthenticated requests
