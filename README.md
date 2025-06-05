# 🏛️ Spartacus Desktop

**Claude Desktop Alternative** - A powerful desktop application built with Python agents and modern web technologies.

![Status](https://img.shields.io/badge/Status-Phase%203%20In%20Progress-orange)
![Progress](https://img.shields.io/badge/Progress-75%25-green)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+** with virtual environment
- **Node.js 18+** for frontend
- **Git** for version control

### Installation

```bash
# 1. Clone the repository
git clone <your-repo> spartacus
cd spartacus

# 2. Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install frontend dependencies
cd spartacus_frontend
npm install
cd ..

# 5. Start the application
python start_spartacus.py
```

The application will open automatically with:
- **Backend API:** http://127.0.0.1:8000
- **Frontend:** Electron desktop app
- **Documentation:** http://127.0.0.1:8000/docs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Spartacus Desktop                        │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Electron + React + TypeScript)                  │
│  ├── Modern UI with Tailwind CSS                           │
│  ├── Chat interface similar to Claude Desktop              │
│  └── Real-time communication with backend                  │
├─────────────────────────────────────────────────────────────┤
│  Backend (FastAPI + Python)                                │
│  ├── REST API endpoints                                     │
│  ├── Agent management system                               │
│  └── Tool orchestration                                    │
├─────────────────────────────────────────────────────────────┤
│  Agent System (agentic_lib)                                │
│  ├── ReAct pattern (Reasoning + Acting)                    │
│  ├── OpenAI-compatible tool calling                        │
│  ├── Context injection & dependency management             │
│  └── Multi-loop execution with error handling              │
├─────────────────────────────────────────────────────────────┤
│  LLM Integration                                            │
│  ├── Azure OpenAI support                                  │
│  ├── Extensible client system                              │
│  └── Local model support (future)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Current (Phase 1-2 Complete)
- ✅ **Standalone Agent System:** ReAct-based agents with tool calling
- ✅ **FastAPI Backend:** High-performance REST API
- ✅ **Agent Manager:** Lifecycle management and orchestration
- ✅ **Tool System:** Extensible tool framework with context injection
- ✅ **Error Handling:** Comprehensive error management and logging
- ✅ **Modern Frontend:** Electron + React + TypeScript foundation
- ✅ **Developer Experience:** Hot reloading, type safety, documentation

### In Progress (Phase 3)
- 🚧 **Chat Interface:** Modern messaging UI
- 🚧 **Backend Integration:** Real-time communication
- 🚧 **Agent Configuration:** Tool selection and customization

### Planned (Phase 4-5)
- 🔮 **Custom Tools:** User-defined tool creation
- 🔮 **Agent Templates:** Pre-configured setups
- 🔮 **Multi-Modal:** Image and file processing
- 🔮 **Cross-Platform:** Distribution packages

---

## 🛠️ Development

### Project Structure

```
spartacus/
├── agentic_lib/           # Core agent logic
│   ├── base_agent.py      # Multi-loop ReAct agent
│   ├── tools.py           # Tool abstraction layer
│   ├── context_injection.py # Dependency injection
│   └── final_answer.py    # Termination tool
├── spartacus_backend/     # FastAPI backend
│   ├── main.py           # FastAPI application
│   ├── api/              # REST endpoints
│   ├── services/         # Business logic
│   └── config/           # Configuration
├── spartacus_frontend/    # Electron + React frontend
│   ├── src/              # React TypeScript code
│   ├── main/             # Electron main process
│   └── preload/          # Electron preload scripts
├── spartacus_services/    # Shared services
├── llm_clients/          # LLM integrations
├── scripts/              # Development scripts
├── tests/                # Test suites
├── docs/                 # Documentation
└── start_spartacus.py    # Unified launcher
```

### Development Commands

```bash
# Backend development
cd spartacus_backend
python -m uvicorn main:app --reload

# Frontend development
cd spartacus_frontend
npm run dev

# Full application
python start_spartacus.py

# Run tests
python -m pytest tests/
cd spartacus_frontend && npm test

# Standalone agent testing
python test_standalone.py
```

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Azure OpenAI (optional)
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment

# Backend settings
SPARTACUS_HOST=127.0.0.1
SPARTACUS_PORT=8000
SPARTACUS_LOG_LEVEL=INFO

# Development
SPARTACUS_RELOAD=true
```

### Agent Configuration
Configure agents in `spartacus_backend/config/agents.yaml`:

```yaml
default_agent:
  name: "Spartacus Assistant"
  max_iterations: 10
  tools:
    - final_answer
    - web_search  # Future implementation
    - file_operations  # Future implementation
  
custom_agents:
  - name: "Code Assistant"
    specialization: "programming"
    tools: ["final_answer", "code_analysis", "git_operations"]
```

---

## 🧪 Testing

### Backend Tests
```bash
# Run all backend tests
cd spartacus_backend
python -m pytest tests/ -v

# Test specific module
python -m pytest tests/test_agents.py

# Test with coverage
python -m pytest tests/ --cov=spartacus_backend
```

### Frontend Tests
```bash
# Run React tests
cd spartacus_frontend
npm test

# Run with coverage
npm run test:coverage

# E2E tests (future)
npm run test:e2e
```

### Integration Tests
```bash
# Test standalone components
python test_standalone.py

# Test full stack integration
python scripts/test_integration.py
```

---

## 📖 API Reference

### Chat Endpoints
- `POST /api/chat/message` - Send message to agent
- `GET /api/chat/history` - Get conversation history
- `DELETE /api/chat/clear` - Clear conversation

### Agent Management
- `GET /api/agents/available` - List available agents
- `POST /api/agents/create` - Create new agent
- `PUT /api/agents/{id}/config` - Update agent configuration

### System
- `GET /health` - Health check
- `GET /api/system/status` - System status
- `GET /docs` - API documentation

Full API documentation available at http://127.0.0.1:8000/docs when running.

---

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Follow the development setup above
4. Make your changes with tests
5. Submit a pull request

### Coding Standards
- **Python:** Follow PEP 8, use type hints, docstrings
- **TypeScript:** Strict mode, ESLint configuration
- **Commits:** Conventional commit format
- **Tests:** Maintain >90% coverage

### Project Guidelines
- All code must be in English (comments, variables, functions)
- Use explicit parameter names for clarity
- Create tests for new functionality
- Update documentation for changes

---

## 📊 Status & Roadmap

### Current Phase: Frontend Development + Gmail Integration (85% Complete)
- ✅ Phase 1: Analysis & Architecture
- ✅ Phase 2: Backend Integration  
- ✅ **Gmail MCP Integration**: Native email management capabilities
- 🚧 Phase 3: Frontend Development
- 🔮 Phase 4: Advanced Features
- 🔮 Phase 5: Distribution & Polish

### Next Milestones
1. **Gmail Integration Testing** - Complete email functionality testing (3-5 days)
2. **Chat Interface** - Complete messaging UI with Gmail commands (1-2 weeks)
3. **Backend Communication** - Real-time agent interaction (1 week)
4. **Agent Configuration** - Tool selection interface (1 week)
5. **Beta Release** - First distributable version with Gmail (2 weeks)

### Recent Achievements ✨
- **Azure OpenAI Integration**: Real AI agents instead of mock responses
- **Gmail MCP Server**: Native email sending, reading, and searching
- **Email Agent**: Specialized agent for Gmail management
- **10 Gmail Tools**: send_email, search_emails, read_email, labels management, batch operations

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by Claude Desktop's excellent user experience
- Built with modern Python and TypeScript ecosystems
- Community-driven development approach

---

## 🆘 Support

- **Documentation:** `/doc_agent/` folder contains detailed guides
- **Issues:** Use the GitHub issue tracker
- **Discussions:** GitHub Discussions for questions
- **Development:** See `/scripts/` for development utilities

---

*Spartacus Desktop - Where artificial intelligence meets human productivity* 🏛️
