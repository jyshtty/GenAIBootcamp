# 🔧 Simple Code Review Assistant - MCP Assignment


**Focus:** Model Context Protocol (MCP) Basics

## 🎯 Learning Objectives

By completing this assignment, you will:
- Build a basic MCP server using **Model Context Protocol**
- Implement simple tool interfaces for AI models
- Practice GitHub API integration
- Understand how AI models connect to external data sources

## 📋 Prerequisites

- Python 3.11+ experience
- Basic understanding of REST APIs
- Familiarity with GitHub API
- Basic knowledge of AI/LLM concepts

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone and navigate to project
cd MCPAssignment

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create `.env` file in the project root:
```env
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO_OWNER=your_github_username
GITHUB_REPO_NAME=your_repository_name
```

### 3. Run the MCP Server
```bash
# Start the MCP Server
python server.py

# Test the server (in another terminal)
python client.py
```

## 📁 Project Structure

```
mcp-code-review/
├── README.md                 # Your implementation documentation
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
├── server.py                # Single MCP Server file
├── client.py                # Simple client to test server
└── docs/
    ├── api_guide.md         # Sample documentation
    └── setup_guide.md       # Sample documentation
```

## 🏗️ System Architecture

### MCP Tools (Keep it Simple!)

| Tool | Purpose | Implementation |
|------|---------|---------------|
| **get_repository** | Get repo info from GitHub | GitHub API call |
| **search_docs** | Search local documentation | Simple file search |
| **get_file_content** | Read file from repo | GitHub API call |

### Simple Flow
```
Client → MCP Server → GitHub API / Local Files → Response
```

## 📋 Core Requirements (Simplified)

### Must-Have Features (6-8 hours scope)

1. **Basic MCP Server**
   - Implement ONE MCP server file (`server.py`)
   - Support 3 simple tools (listed above)
   - Follow basic MCP protocol
   - Handle errors gracefully

2. **GitHub Integration**
   - Connect to GitHub API using token
   - Implement `get_repository` tool
   - Implement `get_file_content` tool
   - Add basic rate limiting

3. **Documentation Search**
   - Implement `search_docs` tool for local files
   - Search through markdown files in `/docs` folder
   - Return relevant file content
   - Support simple keyword matching

4. **Simple Client**
   - Create `client.py` to test your MCP server
   - Demonstrate all 3 tools working
   - Show real GitHub data retrieval
   - Display search results

## 🔧 Implementation Steps 

### Step 1: Setup
```bash
pip install mcp requests
# Create basic file structure
# Setup GitHub token
```

### Step 2: Basic MCP Server
- Implement MCP protocol basics
- Add the 3 required tools
- Test with simple responses

### Step 3: GitHub Integration
- Connect to GitHub API
- Implement repository and file tools
- Add error handling

### Step 4: Documentation Search 
- Create simple file search
- Add sample documentation files
- Test search functionality

### Step 5: Client & Testing
- Build simple client
- Test all tools
- Create demo

## 📋 How You Will Be Evaluated

- **Total marks:** 100. **Passing marks:** 70/100.
- Evaluation focuses on **functionality**: MCP server runs, three tools (`get_repository`, `get_file_content`, `search_docs`) work, GitHub integration and docs search are demonstrated, and the client can exercise the tools. Basic implementations and reasonable variations in response structure are accepted. Code quality is secondary to a working, understandable solution.

## 📝 Submission Requirements (Minimal)

### Required Files
- ✅ `server.py` - Working MCP server
- ✅ `client.py` - Simple test client
- ✅ `requirements.txt` - Dependencies
- ✅ `.env.example` - Environment template
- ✅ Sample docs in `/docs` folder

### Demo Requirements
- ✅ Show MCP server starting up
- ✅ Demonstrate GitHub repository access
- ✅ Show documentation search working
- ✅ Explain your implementation approach


## 🔗 Resources

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [MCP Examples](https://modelcontextprotocol.io/docs/concepts/tools)

## 🔧 Development Commands

```bash
# Start MCP Server
python server.py

# Test with client (in another terminal)
python client.py --test-all

# Test individual tools
python client.py --test-github
python client.py --test-docs
```
